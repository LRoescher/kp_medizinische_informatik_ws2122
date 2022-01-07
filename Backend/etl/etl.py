from typing import List

import pandas as pd
import os
import logging

from Backend.analysis.patient import Patient
from Backend.common.config import DbConfig, generate_config
from Backend.common.database import DBManager, OmopTableEnum
from Backend.etl import extract, transform


def run_etl_job_for_csvs(csv_dir: str, db_config: DbConfig):
    """
    Runs the entire ETL-Job for the given csvs files at the specified path.
    First all csv files are transformed into pandas dataframes. Then they are transformed into omop compliant tables.
    Finally they are loaded into the postgres common.

    :param csv_dir: Directory containing PERSON.csv, ..
    :param db_config: dict with keys: [host, port, db_name, username, password, db_schema]
    :return: void
    """
    # extract original csv files
    cwd = os.getcwd()
    os.chdir(csv_dir)

    logging.info("Extracting data from the given csv files...")
    person_df: pd.DataFrame = extract.extract_csv("PERSON.csv")
    case_df: pd.DataFrame = extract.extract_csv("CASE.csv")
    lab_df: pd.DataFrame = extract.extract_csv("LAB.csv")
    diagnosis_df: pd.DataFrame = extract.extract_csv("DIAGNOSIS.csv")
    procedure_df: pd.DataFrame = extract.extract_csv("PROCEDURE.csv")
    # Remove all rows with missing data
    procedure_df = procedure_df.dropna()

    os.chdir(cwd)

    # Establish database connection
    # 'clear_tables' remove all previously added omop-entries from the database
    db_manager = DBManager(db_config, clear_tables=True)

    _transform_and_load(person_df=person_df, case_df=case_df, procedure_df=procedure_df, lab_df=lab_df,
                        diagnosis_df=diagnosis_df, db_manager=db_manager)


def run_etl_job_for_patient(patient: Patient, db_config: DbConfig):
    # Establish database connection
    # 'clear_tables' remove all previously added omop-entries from the database
    db_manager = DBManager(db_config, clear_tables=False)
    run_etl_job_for_patient(patient, db_manager)


def run_etl_job_for_patient(patient: Patient, diagnosis: List[str], db_manager: DBManager):
    logging.info("Extracting data from the given patient...")

    # Todo Implement for provider-id, gender as soon as present in Patient Class
    birthdate: str = f"{patient.year}-{patient.month}-{patient.day}"
    data_person = {'PATIENT_ID': [patient.id], 'PROVIDER_ID': [0], 'BIRTHDATE': [birthdate], 'GENDER': ['w'],
                   'FORNAME': [patient.name], 'NAME': [''], 'CITY': ['Unbekannt'], 'ZIP': ['Unbekannt']}
    person_df: pd.DataFrame = pd.DataFrame(data_person)

    # 'ICD_PRIMARY_CODE', 'ICD_SECONDARY_CODE'

    # Todo use date -> now
    admission_date: str = "2020-12-12"

    entries = len(diagnosis)

    data_conditions = {'PROVIDER_ID': [0] * entries, 'PATIENT_ID': [patient.id] * entries,
                       'DIAGNOSIS_TYPE': ['HD'] * entries, 'ADMISSION_DATE': [admission_date] * entries,
                       'ICD_PRIMARY_CODE': diagnosis, 'ICD_SECONDARY_CODE': ['-'] * entries}
    diagnosis_df: pd.DataFrame = pd.DataFrame(data_conditions)

    # Todo other dfs
    case_df: pd.DataFrame = pd.DataFrame(columns=['PROVIDER_ID'])
    lab_df: pd.DataFrame = pd.DataFrame(columns=['IDENTIFIER', 'PARAMETER_NAME', 'PARAMETER_LOINC',
                                                 'Patientidentifikator', 'TEST_DATE', 'NUMERIC_VALUE', 'UCUM_UNIT',
                                                 'IS_NORMAL', 'DEVIATION'])
    procedure_df: pd.DataFrame = pd.DataFrame(columns=['ID', 'OPS_CODE', 'PATIENT_ID', 'EXECUTION_DATE'])

    _transform_and_load(person_df=person_df, case_df=case_df, procedure_df=procedure_df, lab_df=lab_df,
                        diagnosis_df=diagnosis_df, db_manager=db_manager)


def _transform_and_load(person_df: pd.DataFrame, case_df: pd.DataFrame, procedure_df: pd.DataFrame,
                        lab_df: pd.DataFrame, diagnosis_df: pd.DataFrame, db_manager: DBManager):
    """
    Transforms the given dataframes into omop compliant tables and loads them into the database specified by the config.
    """

    # Transform into omop tables
    logging.info("Transforming input files into omop tables...")
    omop_provider_df: pd.DataFrame = transform.generate_provider_table(person_df, case_df)
    omop_location_df: pd.DataFrame = transform.generate_location_table(person_df)
    omop_person_df: pd.DataFrame = transform.generate_person_table(person_df)
    omop_observation_period_df: pd.DataFrame = transform.generate_observation_period_table(case_df)
    omop_visit_occurrence_df: pd.DataFrame = transform.generate_visit_occurrence_table(case_df)
    omop_procedure_occurrence_df: pd.DataFrame = transform.generate_procedure_occurrence_table(procedure_df, db_manager)
    omop_measurement_df: pd.DataFrame = transform.generate_measurement_table(lab_df, db_manager)
    omop_condition_occurrence_df: pd.DataFrame = transform.generate_condition_occurrence_table(diagnosis_df, db_manager)
    logging.info("Transformations finished.")

    # Load into postgres database
    logging.info("Loading omop tables into the database...")
    db_manager.save(OmopTableEnum.PROVIDER, omop_provider_df)
    db_manager.save(OmopTableEnum.LOCATION, omop_location_df)
    db_manager.save(OmopTableEnum.PERSON, omop_person_df)
    db_manager.save(OmopTableEnum.OBSERVATION_PERIOD, omop_observation_period_df)
    db_manager.save(OmopTableEnum.VISIT_OCCURRENCE, omop_visit_occurrence_df)
    db_manager.save(OmopTableEnum.PROCEDURE_OCCURRENCE, omop_procedure_occurrence_df)
    db_manager.save(OmopTableEnum.MEASUREMENT, omop_measurement_df)
    db_manager.save(OmopTableEnum.CONDITION_OCCURRENCE, omop_condition_occurrence_df)
    logging.info("Done loading omop tables into the database.")


if __name__ == "__main__":
    csv_dir, db_config = generate_config()
    run_etl_job_for_csvs(csv_dir, db_config)
