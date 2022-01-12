import os
from typing import Dict, Iterator, Optional

from Backend.interface import PatientId, Disease, DecisionReasons, PatientData, AnalysisData, Interface
from time import sleep

import random, string


class Example(Interface):
    def __init__(self):
        self.__analyse_data = {}
        self.__patient_data = {}
        for i in range(0, 40):
            name = ''.join(random.choice(string.ascii_letters) for x in range(random.randint(3, 10)))
            self.__analyse_data[PatientId(i)] = AnalysisData(name=name,
                                                             probability_pims=random.random(),
                                                             probability_kawasaki=random.random())
            self.__patient_data[PatientId(i)] = PatientData(age=random.randint(0, 110),
                                                            name=name,
                                                            hasFever=bool(random.randint(0, 1)),
                                                            hasCovid=bool(random.randint(0, 1)))

    def reset_config(self):
        """
        Resets the configuration and database connection.
        To be used when the configuration files are changed.
        """
        pass

    def is_db_empty(self) -> bool:
        return True

    def reset_db(self) -> bool:
        return True

    def add_patient(self, patient_data: PatientData) -> Optional[PatientId]:
        i = PatientId(len(self.__patient_data))
        self.__patient_data[i] = patient_data
        self.__analyse_data[i]["name"] = patient_data["name"]
        return

    def update_patient(self, patient_id: PatientId, patient_data: PatientData) -> bool:
        self.__patient_data[patient_id] = patient_data
        self.__analyse_data[patient_id]["name"] = patient_data["name"]
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
        return self.__analyse_data

    def get_patient_data(self, patient_id: PatientId) -> PatientData:
        return self.__patient_data[patient_id]

    def get_decision_reason(self, patient_id: PatientId, disease: Disease) -> DecisionReasons:
        # ToDo: extend
        if disease == Disease.KAWASAKI:
            return DecisionReasons(disease=Disease.KAWASAKI, probability=0.5, pro=["hasCovid"], con=["hasFever"])
        if disease == Disease.PIMS:
            return DecisionReasons(disease=Disease.PIMS, probability=0.5, pro=["hasCovid"], con=["hasFun"])
