from abc import ABC, abstractmethod
from typing import Iterator, TypedDict, List, TypeAlias, Dict
from enum import Enum
import os

PatientId: TypeAlias = int


class Disease(Enum):
    """ The diseases this system should detect """
    KAWASAKI = "Kawasaki"
    PIMS = "Pediatric Inflammatory Multisystem Syndrome"


class AnalysisData(TypedDict):
    """ Expected format for analysis data """
    forename: str
    surname: str
    probability_pims: int
    probability_kawasaki: int


class PatientData(TypedDict):
    """ Expected format for patient data """
    forename: str
    surname: str
    # ToDo: Covid, Fieber, ..


class DecisionReasons(TypedDict):
    """ Description of why this disease may have broken out """
    disease: Disease
    probability: int
    pro: List[str]  # strs have to be equal to PatientData
    con: List[str]  # strs have to be equal to PatientData


class Interface(ABC):

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
    def add_patient(self, patient_data: PatientData) -> bool:
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

    @abstractmethod
    @property
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

