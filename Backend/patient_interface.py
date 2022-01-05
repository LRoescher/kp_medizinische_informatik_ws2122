import os
from typing import Dict, Iterator, Optional

from Backend.analysis.analysis import evaluate_patient, evaluate_all_in_database
from Backend.common.config import generate_config
from Backend.common.database import DBManager
from Backend.etl.etl import run_etl_job
from Backend.interface import PatientId, Disease, DecisionReasons, PatientData, AnalysisData, Interface


class Results(Interface):

    def __init__(self):
        self.db_config = generate_config()
        self.dbManager = DBManager(self.db_config, clear_tables=False)

    def is_db_empty(self) -> bool:
        return self.dbManager.check_if_database_is_empty()

    def reset_db(self) -> bool:
        return self.dbManager.clear_omop_tables()
        # Todo:
        # Falls die Ergebnisse der Analyse auch in der DB gespeichert werden, sollten auch diese zurückgesetzt werden

    def add_patient(self, patient_data: PatientData) -> Optional[PatientId]:
        pass

    def update_patient(self, patient_id: PatientId, patient_data: PatientData) -> bool:
        pass

    def upload_csv(self, csv_file: os.path) -> Iterator[int]:
        run_etl_job(csv_file, self.db_config)

    @property
    def analysis_data(self) -> Dict[PatientId, AnalysisData]:
        results = evaluate_all_in_database(self.dbManager)
        data_dict = dict()
        for result in results:
            analysis_data: AnalysisData = {
                'name': result[1],
                'probability_kawasaki': result[2],
                'probability_pims': result[4],
            }
            data_dict[result[0]] = analysis_data
        return data_dict

    def get_patient_data(self, patient_id: PatientId) -> PatientData:
        evaluate_patient(self.db_manager, patient_id)

    def get_decision_reason(self, patient_id: PatientId, disease: Disease) -> DecisionReasons:
        results = evaluate_all_in_database(self.dbManager)
        for result in results:
            if result[0] == patient_id:
                decision_reasons: DecisionReasons = DecisionReasons()
                if disease == Disease.KAWASAKI:
                    decision_reasons = {
                        'disease': Disease.KAWASAKI,
                        'probability': result[2],
                        'pro': result[3],
                        'con': list()
                    }
                elif disease == Disease.PIMS:
                    decision_reasons = {
                        'disease': Disease.PIMS,
                        'probability': result[4],
                        'pro': result[5],
                        'con': list()
                    }
                return decision_reasons


if __name__ == "__main__":
    r = Results()
    print(r.analysis_data)
    print(r.get_decision_reason(PatientId(2426), Disease.KAWASAKI))
