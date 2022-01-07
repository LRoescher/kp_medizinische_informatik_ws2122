import datetime
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


def run_etl_job_for_patient(patient: Patient, db_manager: DBManager):
    logging.info("Extracting data from the given patient...")

    # Todo Remove dummy data (gender, etc) as soon as present in Patient Object and Frontend
    birthdate = datetime.datetime(year=patient.year, month=patient.month, day=patient.day)
    data_person = {'person_id': [patient.id], 'gender_concept_id': [8532], 'year_of_birth': [patient.year],
                   'month_of_birth': [patient.month], 'day_of_birth': [patient.day], 'birth_datetime': [birthdate],
                   'race_concept_id': [4218674], 'ethnicity_concept_id': [0], 'location_id': [patient.id],
                   'provider_id': [patient.id], 'person_source_value': [patient.name], 'gender_source_value': ['w']}
    omop_person_df: pd.DataFrame = pd.DataFrame(data_person)

    data_location = {'location_id': [patient.id], 'city': ['Unbekannt'], 'zip': ['Unbekannt']}
    omop_location_df: pd.DataFrame = pd.DataFrame(data_location)

    data_provider = {'provider_id': [patient.id]}
    omop_provider_df: pd.DataFrame = pd.DataFrame(data_provider)

    print("before generating.")
    # Generate untaken ids for all conditions
    condition_occurrence_ids: List[int] = list()
    for _ in patient.conditions:
        condition_occurrence_id: int = db_manager.generate_condition_occurrence_id()
        while condition_occurrence_id in condition_occurrence_ids:
            condition_occurrence_id: int = db_manager.generate_condition_occurrence_id()
        condition_occurrence_ids.append(condition_occurrence_id)

    print(condition_occurrence_ids)

    current_date = datetime.datetime.now()
    entries = len(patient.conditions)

    # Create dataframe for conditions
    data_condition_occurrence = {'condition_occurrence_id': condition_occurrence_ids,
                                 'person_id': [patient.id] * entries,
                                 'condition_concept_id': patient.conditions,
                                 'condition_start_date': [current_date] * entries,
                                 'condition_type_concept_id': [44786627] * entries}
    omop_condition_occurrence_df: pd.DataFrame = pd.DataFrame(data_condition_occurrence)

    db_manager.save(OmopTableEnum.LOCATION, omop_location_df)
    db_manager.save(OmopTableEnum.PROVIDER, omop_provider_df)
    db_manager.save(OmopTableEnum.PERSON, omop_person_df)
    db_manager.save(OmopTableEnum.CONDITION_OCCURRENCE, omop_condition_occurrence_df)
    logging.info("Done loading a single Patient into the database.")


if __name__ == "__main__":
    csv_dir, db_config = generate_config()
    run_etl_job_for_csvs(csv_dir, db_config)
