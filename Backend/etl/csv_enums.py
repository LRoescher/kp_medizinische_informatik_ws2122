from enum import Enum


class CsvFilesEnum(Enum):
    """
    Enum for the names of the provided csv files.
    """
    CASE = "CASE.csv"
    DIAGNOSIS = "DIAGNOSIS.csv"
    LAB = "LAB.csv"
    PERSON = "PERSON.csv"
    PROCEDURE = "PROCEDURE.csv"


class CaseColumnsEnum(Enum):
    """
    Enum for the column names of the case table.
    """
    ID = "CASE_ID"
    PROVIDER_ID = "PROVIDER_ID"
    PATIENT_ID = "PATIENT_ID"
    START = "START_DATE"
    END = "END_DATE"


class DiagnosisColumnsEnum(Enum):
    """
    Enum for the column names of the diagnosis table.
    """
    PROVIDER_ID = "PROVIDER_ID"
    PATIENT_ID = "PATIENT_ID"
    ADMISSION_NUMBER = "ADMISSION_NUMBER"
    ADMISSION_DATE = "ADMISSION_DATE"
    ICD_PRIMARY_CODE = "ICD_PRIMARY_CODE",
    ICD_SECONDARY_CODE = "ICD_SECONDARY_CODE"
    DIAGNOSIS_TYPE = "DIAGNOSIS_TYPE"


class LabColumnsEnum(Enum):
    """
    Enum for the column names of the lab table.
    """
    ID = "IDENTIFIER"
    STATUS = "STATUS"
    LOINC = "PARAMETER_LOINC"
    PATIENT_ID = "PATIENT_ID"
    PATIENT_ID_ALT = "Patientidentifikator"
    DATE = "TEST_DATE"
    NUMERIC_VALUE = "NUMERIC_VALUE"
    TEXT_VALUE = "TEXTUAL_VALUE"
    UNIT = "UNIT"
    NORMAL_VALUES = "NORMAL_VALUES"
    IS_NORMAL = "IS_NORMAL"
    DEVIATION = "COMMENT"
    COMMENT = "COMMENT"
    UCUM_UNIT = "UCUM_UNIT"


class PersonColumnsEnum(Enum):
    """
    Enum for the column names of the person table.
    """
    PROVIDER_ID = "PROVIDER_ID"
    ID = "PATIENT_ID"
    NAME = "NAME"
    FORENAME = "FORNAME"  # sic! Typo is in the dataset
    GENDER = "GENDER"
    BIRTHDATE = "BIRTHDATE"
    CITY = "CITY"
    ZIP = "ZIP"
    DEATH = "DEATH"
    DEATH_DATE = "DEATH_DATE"
    DATE_OF_LIFE = "DATE_OF_LIFE"
    INSURANCE = "INSURANCE"
    INSURANCE_ID = "INSURANCE_ID"


class ProcedureColumnsEnum(Enum):
    """
    Enum for the column names of the procedure table.
    """
    ID = "ID"
    OPS_VERSION = "OPS_VERSION"
    OPS_CODE = "OPS_CODE"
    PATIENT_ID = "PATIENT_ID"
    DATE = "EXECUTION_DATE"
