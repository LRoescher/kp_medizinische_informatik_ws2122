from abc import ABC, abstractmethod
from datetime import date
from typing import Iterator, TypedDict, List, Dict, NewType, Optional
from enum import Enum
from Backend.Singleton import Singleton
import os

PatientId = NewType("PatientId", int)


class Disease(Enum):
    """ The diseases this system should detect """
    KAWASAKI = "Kawasaki-Syndrom"
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
    missing: List[str]


# Übersetzung der Symptome ins Deutsche
TranslationGerman = {
    "birthdate": "Geburtsdatum",
    # Full name
    "name": "Name",
    "hasCovid": "Covid19",
    "hasFever": "Fieber",
    # Ausschlag auf der Haut
    "hasExanthem": "Exanthem",
    # Entzündung im Mundraum (Lippen, Zunge, Mundschleimhaut)
    "hasEnanthem": "Entzündung von Lippen, Zunge oder Mundschleimhaut",
    # Geschwollene, gerötete Extremitäten
    "hasSwollenExtremeties": "Geschwollene, gerötete Extremitäten",
    # Bindehautentzündung
    "hasConjunctivitis": "Bindehautentzündung",
    # Geschwollene Lymphknoten
    "hasSwollenLymphnodes": "Geschwollene Lymphknoten",
    # Erbrechen, Übelkeit, Durchfall und/oder Bauchschmerzen
    "hasGastroIntestinalCondition": "Erbrechen, Übelkeit, Durchfall und/oder Bauchschmerzen",
    # Aszites (Flüssigkeitsansammlung im Bauchraum)
    "hasAscites": "Aszites",
    # Perikardergüsse (Flüssigkeitsansammlung im Herzbeutel)
    "hasPericardialEffusions": "Perikardergüsse",
    # Pleuraergüsse (Flüssigkeitsansammlung in der Lunge)
    "hasPleuralEffusions": "Pleuraergüsse",
    # Perikarditits (Herzbeutelentzündung)
    "hasPericarditis": "Perikarditits",
    # Hat Myokarditis (Herzmuskelenzündung)
    "hasMyocarditis": "Myokarditis"
}


TranslationPercentageKawasaki = {
    1.0: "Kawsaki-Syndrom",
    0.75: "Inkomplettes Kawasaki-Syndrom",
    0.5: "Verdacht",
    0.0: "Nicht erkrankt"
}


TranslationPercentagePims = {
    1.0: "PIMS",
    0.75: "Erhöhter Verdacht",
    0.5: "Verdacht",
    0.0: "Nicht erkrankt"
}


class Interface(Singleton, ABC):

    @abstractmethod
    def reset_config(self):
        """
        Resets the configuration and database connection.
        To be used when the configuration files are changed.
        """
        pass

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
    def run_etl(self, csv_dir: os.path) -> bool:
        '''
        executes etl-job

        :param csv_dir: with all needed files
        :return: success
        '''
        pass

    @abstractmethod
    def run_analysis(self) -> bool:
        '''
        analyse data

        :return: success
        '''
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
