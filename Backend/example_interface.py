import os
from typing import Dict, Iterator

from Backend.interface import PatientId, Disease, DecisionReasons, PatientData, AnalysisData, Interface
from time import sleep


class Example(Interface):
    def is_db_empty(self) -> bool:
        return True

    def reset_db(self) -> bool:
        return True

    def add_patient(self, patient_data: PatientData) -> bool:
        return True

    def update_patient(self, patient_id: PatientId, patient_data: PatientData) -> bool:
        return True

    def upload_csv(self, csv_file: os.path) -> Iterator[int]:
        sleep(2)
        yield 5
        sleep(2)
        yield 10
        sleep(2)
        yield 20
        sleep(2)
        yield 30
        sleep(2)
        yield 34
        sleep(2)
        yield 49
        sleep(2)
        yield 63
        sleep(2)
        yield 70
        sleep(2)
        yield 99
        sleep(5)
        return 100

    @property
    def analysis_data(self) -> Dict[PatientId, AnalysisData]:
        return {
            PatientId(0): AnalysisData(name="ALICE", probability_pims=0.0, probability_kawasaki=0.0),
            PatientId(1): AnalysisData(name="BOB", probability_pims=0.7, probability_kawasaki=0.4),
            PatientId(2): AnalysisData(name="EVE", probability_pims=0.1, probability_kawasaki=0.27774563),
            PatientId(3): AnalysisData(name="MALLOC", probability_pims=0.3, probability_kawasaki=0.9)
        }

    def get_patient_data(self, patient_id: PatientId) -> PatientData:
        return {
            PatientId(0): PatientData(id=0, age=5, name="ALICE", hasCovid=False, hasFever=False),
            PatientId(1): PatientData(id=1, age=5, name="BOB", hasCovid=False, hasFever=False),
            PatientId(2): PatientData(id=2, age=5, name="EVE", hasCovid=False, hasFever=False),
            PatientId(3): PatientData(id=3, age=5, name="MALLOC", hasCovid=False, hasFever=False)
        }[patient_id]

    def get_decision_reason(self, patient_id: PatientId, disease: Disease) -> DecisionReasons:
        # ToDo: extend
        return DecisionReasons(disease=Disease.KAWASAKI, probability=0.5, pro=["hasCovid"], con=["hasFever"])