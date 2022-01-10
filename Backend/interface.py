from abc import ABC, abstractmethod
from datetime import date
from typing import Iterator, TypedDict, List, Dict, NewType, Optional
from enum import Enum
from Backend.Singleton import Singleton
import os

PatientId = NewType("PatientId", int)


class Disease(Enum):
    """ The diseases this system should detect """
    KAWASAKI = "Kawasaki"
    PIMS = "Pediatric Inflammatory Multisystem Syndrome"


class AnalysisData(TypedDict):
    """ Expected format for analysis data """
    name: str
    probability_pims: float
    probability_kawasaki: float


class PatientData(TypedDict):
    """ Expected format for patient data """
    birthdate: date
    # Full name
    name: str
    hasCovid: bool
    hasFever: bool
    # Ausschlag auf der Haut
    hasExanthem: bool
    # Entzündung im Mundraum (Lippen, Zunge, Mundschleimhaut)
    hasEnanthem: bool
    # Geschwollene, gerötete Extremitäten
    hasSwollenExtremeties: bool
    # Bindehautentzündung
    hasConjunctivitis: bool
    # Geschwollene Lymphknoten
    hasSwollenLymphnodes: bool
    # Erbrechen, Übelkeit, Durchfall und/oder Bauchschmerzen
    hasGastroIntestinalCondition: bool
    # Aszites (Flüssigkeitsansammlung im Bauchraum)
    hasAscites: bool
    # Perikardergüsse (Flüssigkeitsansammlung im Herzbeutel)
    hasPericardialEffusions: bool
    # Pleuraergüsse (Flüssigkeitsansammlung in der Lunge)
    hasPleuralEffusions: bool
    # Perikarditits (Herzbeutelentzündung)
    hasPericarditis: bool
    # Hat Myokarditis (Herzmuskelenzündung)
    hasMyocarditis: bool


class DecisionReasons(TypedDict):
    """ Description of why this disease may have broken out """
    disease: Disease
    probability: float
    pro: List[str]  # strs have to be equal to PatientData


class Interface(Singleton, ABC):

    @abstractmethod
    def is_db_empty(self) -> bool:
        """
        check if db is empty

        :return: is empty
        """
        pass

    @abstractmethod
    def reset_db(self) -> bool:
        """
        Remove all patient data from the db

        :return: successfully reset
        """
        pass

    @abstractmethod
    def add_patient(self, patient_data: PatientData) -> Optional[PatientId]:
        """
        Add a new patient to the db

        :param patient_data: of the new patient
        :return: successfully added new patient
        """
        pass

    @abstractmethod
    def update_patient(self, patient_id: PatientId, patient_data: PatientData) -> bool:
        """
        Update existing patient

        :param patient_id: of the patient
        :param patient_data: with all updates
        :return: successfully update patient
        """
        pass

    @abstractmethod
    def upload_csv(self, csv_file: os.path) -> Iterator[int]:
        """
        run ETL-job for new csv-file

        After checking if the db is really empty, this function run the ETL-job. The Progress will be represented by the
        numbers from 0 to 100.
        :param csv_file: with new data
        :return: progress
        """
        pass

    @property
    @abstractmethod
    def analysis_data(self) -> Dict[PatientId, AnalysisData]:
        """
        Patient analysis for kawasaki and pims

        :return: the analysis and the associated patient id
        """
        pass

    @abstractmethod
    def get_patient_data(self, patient_id: PatientId) -> PatientData:
        """
        data for a single patient

        :param patient_id:
        :return: data for the selected patient
        """
        pass

    @abstractmethod
    def get_decision_reason(self, patient_id: PatientId, disease: Disease) -> DecisionReasons:
        """
        reason why this decision was made

        :param patient_id: for which the reason for the decision is sought
        :param disease: for which the reason for the decision is sought
        :return:reason for the decision
        """
        pass
