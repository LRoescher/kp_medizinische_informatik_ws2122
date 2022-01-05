import os
from typing import Dict, Iterator, Optional, List

from Backend.analysis.analysis import evaluate_patient, evaluate_all_in_database
from Backend.analysis.patient import Patient
from Backend.common.config import generate_config
from Backend.common.database import DBManager
from Backend.etl.etl import run_etl_job
from Backend.interface import PatientId, Disease, DecisionReasons, PatientData, AnalysisData, Interface


class BackendManager(Interface):

    def __init__(self):
        self.db_config = generate_config()[1]
        self.dbManager = DBManager(self.db_config, clear_tables=False)
        self.patients: List[Patient] = list()

    def _update_patients(self):
        self.patients = evaluate_all_in_database(self.dbManager)

    def analyze_all_in_database(self):
        self._update_patients()

    def is_db_empty(self) -> bool:
        return self.dbManager.check_if_database_is_empty()

    def reset_db(self) -> bool:
        return self.dbManager.clear_omop_tables()
        # Todo:
        # Falls die Ergebnisse der Analyse auch in der DB gespeichert werden, sollten auch diese zurückgesetzt werden

    def add_patient(self, patient_data: PatientData) -> Optional[PatientId]:
        # Todo create new patient, save in db, start analysis, add to patients list
        pass

    def update_patient(self, patient_id: PatientId, patient_data: PatientData) -> bool:
        # Todo get patient with id, update fields insert into database, start analysis, add to patients list
        pass

    def upload_csv(self, csv_file: os.path) -> Iterator[int]:
        run_etl_job(csv_file, self.db_config)
        # Todo get path to target directory, start etl job here? or with a dedicated method call

    @property
    def analysis_data(self) -> Dict[PatientId, AnalysisData]:
        if not self.patients:
            self._update_patients()
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
    print(r.analysis_data)
    print(r.get_decision_reason(PatientId(2426), Disease.KAWASAKI))
    print(r.get_decision_reason(PatientId(2426), Disease.PIMS))
