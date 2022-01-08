import logging
import os
from typing import Dict, Iterator, Optional, List

from Backend.analysis.analysis import evaluate_patient, evaluate_all_in_database
from Backend.analysis.patient import Patient
from Backend.common.config import generate_config
from Backend.common.database import DBManager, OmopTableEnum
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
        self.db_config = generate_config()[1]
        self.dbManager = DBManager(self.db_config, clear_tables=False)
        self.patients: List[Patient] = list()

    def _synchronize(self):
        """
        Synchronizes the maintained list of patients with the database.
        """
        self.patients = evaluate_all_in_database(self.dbManager)

    def analyze_all_in_database(self):
        """
        Analyzes all patients currently saved in the database.
        """
        self._synchronize()

    def is_db_empty(self) -> bool:
        """
        Returns whether the database is empty.

        :return: True if the database is empty
        """
        # Checks if there any entries in the condition table
        return self.dbManager.check_if_table_is_empty(table_name=OmopTableEnum.CONDITION_OCCURRENCE.value)

    def reset_db(self) -> bool:
        """
        Empties the database of all entries created by the etl job or via the frontend.

        :return: True if the database was successfully reset.
        """
        self.patients.clear()
        return self.dbManager.clear_omop_tables()
        # Todo: Falls die Ergebnisse der Analyse in der DB gespeichert werden, sollten auch diese zurückgesetzt werden

    def add_patient(self, patient_data: PatientData) -> Optional[PatientId]:
        """
        Creates a patient-object from the given data and saves it in the database.

        :param patient_data: PatientData from the frontend
        :return: PatientId of the saved patient if successful else None
        """
        # Create Patient object
        patient: Patient = self._create_patient_from_data(patient_data)

        # Save in database
        run_etl_job_for_patient(patient=patient, db_manager=self.dbManager)

        # Evaluate patient
        evaluated_patient = evaluate_patient(self.dbManager, patient.id)
        self.patients.append(evaluated_patient)

        return PatientId(patient.id)

    def _create_patient_from_data(self, patient_data: PatientData) -> Patient:
        """
        Creates a patient-object from the given data.

        :param patient_data: PatientData from the Frontend
        :return: Corresponding Patient
        """
        # Generate Random id that is not already in the database
        patient_id = self.dbManager.generate_patient_id()

        # Todo remove dummy data (birthdate, etc.), get from front end instead
        # Get birthday data
        day = 1
        month = 1
        year = 2020

        patient: Patient = Patient(patient_id=patient_id, name=patient_data['name'], day=day, month=month, year=year)

        # Get snomed ids from patient_data
        if patient_data['hasCovid']:
            patient.conditions.append(37311061)
        if patient_data['hasFever']:
            patient.conditions.append(437663)
        # Todo Add missing hasX -> Conditions

        return patient

    def update_patient(self, patient_id: PatientId, patient_data: PatientData) -> bool:
        """
        Updates the patient with the given id with the provided patient-data. Overwrites the values of the existing
        patient. Only fields that can be set via the PatientData will be overwritten.

        :return: True if successfully updated
        """
        try:
            # Get already saved patient
            old_patient: Patient = evaluate_patient(self.dbManager, patient_id)

            # Create new patient from the given PatientData
            new_patient: Patient = self._create_patient_from_data(patient_data)
            new_patient.id = old_patient.id

            # Update old patient with new patient
            update_patient(old_patient, new_patient, self.dbManager)

            # Evaluate (updated) patient
            evaluated_patient = evaluate_patient(self.dbManager, new_patient.id)

            # Update evaluation list
            for patient in self.patients:
                if patient.id == new_patient.id:
                    self.patients.remove(patient)
                    self.patients.append(evaluated_patient)

            return True

        except:
            logging.error("Updating patient failed.")
            return False

    def upload_csv(self, csv_file: os.path) -> Iterator[int]:
        run_etl_job_for_csvs(csv_file, self.db_config)
        # Todo get path to target directory, start etl job here? or with a dedicated method call

    @property
    def analysis_data(self) -> Dict[PatientId, AnalysisData]:
        """
        Returns the analysis data as a dictionary with patient-ids as keys.

        :return: A dictionary with PatientIds as keys and AnalysisData as values
        """
        if not self.patients:
            self._synchronize()
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
                    'hasFever': patient.has_fever()
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
                        'pro': patient.reasons_for_kawasaki,
                        'con': list()
                    }
                elif disease == Disease.PIMS:
                    decision_reasons = {
                        'disease': Disease.PIMS,
                        'probability': patient.pims_score,
                        'pro': patient.reasons_for_pims,
                        'con': list()
                    }
                return decision_reasons


if __name__ == "__main__":
    r = BackendManager()
    # print(r.analysis_data)
    # print(r.get_decision_reason(PatientId(2426), Disease.KAWASAKI))
    # print(r.get_decision_reason(PatientId(2426), Disease.PIMS))
    # print(r.dbManager.delete_condition_for_patient(1547, 444413))
