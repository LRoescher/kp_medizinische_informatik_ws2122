import logging
import os
from datetime import date
from typing import Dict, Iterator, Optional, List

from Backend.analysis.analysis import evaluate_patient, evaluate_all_in_database
from Backend.analysis.patient import Patient
from Backend.common.config import generate_config
from Backend.common.database import DBManager
from Backend.common.omop_enums import OmopTableEnum, SnomedConcepts
from Backend.etl.etl import run_etl_job_for_csvs, run_etl_job_for_patient, update_patient
from Backend.interface import PatientId, Disease, DecisionReasons, PatientData, AnalysisData, Interface


class BackendManager(Interface):
    """
    Interface for Backend-functionality, like accessing the database.
    """

    def __init__(self):
        """
        Creates a new BackendManager.
        Maintains a list of patient-objects that hold evaluation results.
        """
        self.db_config = None
        self.dbManager = None
        self.reset_config()
        self.patients: List[Patient] = list()
        self.analyze_all_in_database()

    def reset_config(self):
        """
        Resets the configuration and database connection.
        To be used when the configuration files are changed.

        If the config file is invalid both the config and the db-manager will be set to none.
        """
        try:
            logging.info("Resetting Configuration.")
            self.db_config = generate_config()[1]
            logging.info("Resetting DatabaseManager.")
            self.dbManager = DBManager(self.db_config, clear_tables=False)
        except AttributeError as error:
            logging.error("Error during initialization. Make sure the config file is valid.")
            logging.error(error)
            self.db_config = None
            self.dbManager = None

    def analyze_all_in_database(self):
        """
        Analyzes all patients currently saved in the database.
        """
        if self.dbManager:
            self.patients = evaluate_all_in_database(self.dbManager)

    def is_db_empty(self) -> bool:
        """
        Returns whether the database is empty.

        :return: True if the database is empty
        """
        # Checks if there any entries in the condition table
        try:
            return self.dbManager.check_if_table_is_empty(table_name=OmopTableEnum.CONDITION_OCCURRENCE.value)
        except AttributeError:
            # Return False if the database operation fails
            return False

    def reset_db(self) -> bool:
        """
        Empties the database of all entries created by the etl job or via the frontend.

        :return: True if the database was successfully reset.
        """
        self.patients.clear()
        try:
            return self.dbManager.clear_omop_tables()
        except AttributeError:
            # Return False if the database operation fails
            return False

    def add_patient(self, patient_data: PatientData) -> Optional[PatientId]:
        """
        Creates a patient-object from the given data and saves it in the database.

        :param patient_data: PatientData from the frontend
        :return: PatientId of the saved patient if successful else None
        """
        # Create Patient object
        patient: Patient = self._create_patient_from_data(patient_data)

        if not patient:
            logging.error("Could not create a valid Patient from the given PatientData.")
            return None

        # Save in database
        if not run_etl_job_for_patient(patient=patient, db_manager=self.dbManager):
            logging.error("Error storing patient in the database.")
            return None

        # Evaluate patient
        evaluated_patient = evaluate_patient(self.dbManager, patient.id)
        if not evaluated_patient:
            return None

        self.patients.append(evaluated_patient)
        return PatientId(patient.id)

    def _create_patient_from_data(self, patient_data: PatientData) -> Optional[Patient]:
        """
        Creates a patient-object from the given data. Returns None if the creation failed.

        :param patient_data: PatientData from the Frontend
        :return: Corresponding Patient
        """
        # Generate Random id that is not already in the database
        try:
            patient_id = self.dbManager.generate_patient_id()
        except AttributeError:
            # Error during database interaction
            return None

        # Get birthday data
        birthdate: date = patient_data['birthdate']

        patient: Patient = Patient(patient_id=patient_id, name=patient_data['name'], birthdate=birthdate)
        try:
            # Get snomed ids from patient_data and add as conditions
            if patient_data['hasCovid']:
                patient.conditions.append(SnomedConcepts.COVID_19.value)
            if patient_data['hasFever']:
                patient.conditions.append(SnomedConcepts.FEVER.value)
            if patient_data['hasExanthem']:
                patient.conditions.append(SnomedConcepts.ERUPTION.value)
            if patient_data['hasEnanthem']:
                patient.conditions.append(SnomedConcepts.DISORDER_OF_ORAL_SOFT_TISSUE.value)
            if patient_data['hasSwollenExtremeties']:
                patient.conditions.append(SnomedConcepts.SWELLING.value)
            if patient_data['hasConjunctivitis']:
                patient.conditions.append(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
            if patient_data['hasSwollenLymphnodes']:
                patient.conditions.append(SnomedConcepts.LYMPHADENOPATHY.value)
            if patient_data['hasGastroIntestinalCondition']:
                patient.conditions.append(SnomedConcepts.NAUSEA_AND_VOMITING.value)
            if patient_data['hasAscites']:
                patient.conditions.append(SnomedConcepts.ASCITES.value)
            if patient_data['hasPericardialEffusions']:
                patient.conditions.append(SnomedConcepts.PERICARDIAL_EFFUSION.value)
            if patient_data['hasPleuralEffusions']:
                patient.conditions.append(SnomedConcepts.PLEURAL_EFFUSION.value)
            if patient_data['hasPericarditis']:
                patient.conditions.append(SnomedConcepts.PERICARDITIS.value)
            if patient_data['hasMyocarditis']:
                patient.conditions.append(SnomedConcepts.MYOCARDITIS.value)
        except (KeyError, ValueError, AttributeError) as error:
            logging.error("Error during patient creation from patient_data.")
            logging.error(error)
            return None

        return patient

    def update_patient(self, patient_id: PatientId, patient_data: PatientData) -> bool:
        """
        Updates the patient with the given id with the provided patient-data. Overwrites the values of the existing
        patient. Only fields that can be set via the PatientData will be overwritten.

        :return: True if successfully updated
        """
        # Get already saved patient
        old_patient: Patient = evaluate_patient(self.dbManager, patient_id)
        if not old_patient:
            logging.error("Could not update a patient, because the id does not exist.")
            return False

        # Create new patient from the given PatientData
        new_patient: Patient = self._create_patient_from_data(patient_data)
        if not new_patient:
            logging.error("Could not create a patient with the given patient_data.")
            return False
        new_patient.id = old_patient.id

        # Update old patient with new patient
        if not update_patient(old_patient, new_patient, self.dbManager):
            logging.error("Could not update the patient.")
            return False

        # Evaluate (updated) patient
        evaluated_patient = evaluate_patient(self.dbManager, new_patient.id)
        if not evaluated_patient:
            logging.error("Error during evaluation of the new patient.")
            return False

        # Update evaluation list
        for patient in self.patients:
            if patient.id == new_patient.id:
                self.patients.remove(patient)
                self.patients.append(evaluated_patient)

        return True

    def run_etl(self, csv_dir: os.path) -> bool:
        try:
            run_etl_job_for_csvs(csv_dir, self.db_config)
        except Exception as e:
            print(e)
            return False
        return True

    def run_analysis(self) -> bool:
        try:
            if not self.is_db_empty():
                self.analyze_all_in_database()
            else:
                return False
        except Exception as e:
            print(e)
            return False
        return True

    @property
    def analysis_data(self) -> Dict[PatientId, AnalysisData]:
        """
        Returns the analysis data as a dictionary with patient-ids as keys.

        :return: A dictionary with PatientIds as keys and AnalysisData as values
        """
        data_dict = dict()
        for patient in self.patients:
            analysis_data: AnalysisData = {
                'name': patient.name,
                'probability_pims': patient.pims_score,
                'probability_kawasaki': patient.kawasaki_score
            }
            data_dict[PatientId(patient.id)] = analysis_data
        return data_dict

    def get_patient_data(self, patient_id: PatientId) -> PatientData:
        """
        Gets the PatientData for a specific patientId.

        :param patient_id: id of the patient
        :return: corresponding PatientData
        """
        for patient in self.patients:
            if PatientId(patient.id) == patient_id:
                # Found corresponding patient
                patient_data: PatientData = {
                    'name': patient.name,
                    'age': patient.calculate_age(),
                    'hasCovid': patient.has_covid(),
                    'hasFever': patient.has_fever(),
                    'hasExanthem': patient.has_exanthem(),
                    'hasEnanthem': patient.has_mouth_or_mucosa_inflammation(),
                    'hasSwollenExtremeties': patient.has_swollen_extremities(),
                    'hasConjunctivitis': patient.has_conjunctivitis(),
                    'hasSwollenLymphnodes': patient.has_lymphadenopathy(),
                    'hasGastroIntestinalCondition': patient.has_gastro_intestinal_condition(),
                    'hasAscites': patient.has_ascites(),
                    'hasPericardialEffusions': patient.has_pericardial_effusions(),
                    'hasPleuralEffusions': patient.has_pleural_effusions(),
                    'hasPericarditis': patient.has_pericarditis(),
                    'hasMyocarditis': patient.has_myocarditis()
                }
                return patient_data
        # No patient found, Todo what to return?
        return PatientData()

    def get_decision_reason(self, patient_id: PatientId, disease: Disease) -> DecisionReasons:
        """
        Gets the reasons for the calculated score for a given disease and a given patient (id).

        :param patient_id: id of the patient
        :param disease: disease
        :return: DecisionReasons for the patient and disease
        """
        for patient in self.patients:
            if PatientId(patient.id) == patient_id:
                # Found corresponding patient
                decision_reasons: DecisionReasons = DecisionReasons()
                if disease == Disease.KAWASAKI:
                    decision_reasons = {
                        'disease': Disease.KAWASAKI,
                        'probability': patient.kawasaki_score,
                        'pro': patient.reasons_for_kawasaki
                    }
                elif disease == Disease.PIMS:
                    decision_reasons = {
                        'disease': Disease.PIMS,
                        'probability': patient.pims_score,
                        'pro': patient.reasons_for_pims
                    }
                return decision_reasons


if __name__ == "__main__":
    r = BackendManager()
    # print(r.analysis_data)
    # print(r.get_decision_reason(PatientId(2426), Disease.KAWASAKI))
    # print(r.get_decision_reason(PatientId(2426), Disease.PIMS))
    # print(r.dbManager.delete_condition_for_patient(1547, 444413))
