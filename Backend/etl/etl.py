import pandas as pd
import os
import logging

from Backend.common.config import DbConfig, generate_config
from Backend.common.database import DBManager, OmopTableEnum
from Backend.etl import extract, transform


def run_etl_job(csv_dir: str, db_config: DbConfig):
    """
    Runs the entire ETL-Job.
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

    # Establish common connection
    # 'clear_tables' remove all previously added omop-entries from the common
    loader = DBManager(db_config, clear_tables=True)

    # Transform into omop tables
    logging.info("Transforming input files into omop tables...")
    omop_provider_df: pd.DataFrame = transform.generate_provider_table(person_df, case_df)
    omop_location_df: pd.DataFrame = transform.generate_location_table(person_df)
    omop_person_df: pd.DataFrame = transform.generate_person_table(person_df)
    omop_observation_period_df: pd.DataFrame = transform.generate_observation_period_table(case_df)
    omop_visit_occurrence_df: pd.DataFrame = transform.generate_visit_occurrence_table(case_df)
    omop_procedure_occurrence_df: pd.DataFrame = transform.generate_procedure_occurrence_table(procedure_df, loader)
    omop_measurement_df: pd.DataFrame = transform.generate_measurement_table(lab_df, loader)
    omop_condition_occurrence_df: pd.DataFrame = transform.generate_condition_occurrence_table(diagnosis_df, loader)
    logging.info("Transformations finished.")

    # Load into postgres common
    logging.info("Loading omop tables into the common...")
    loader.save(OmopTableEnum.PROVIDER, omop_provider_df)
    loader.save(OmopTableEnum.LOCATION, omop_location_df)
    loader.save(OmopTableEnum.PERSON, omop_person_df)
    loader.save(OmopTableEnum.OBSERVATION_PERIOD, omop_observation_period_df)
    loader.save(OmopTableEnum.VISIT_OCCURRENCE, omop_visit_occurrence_df)
    loader.save(OmopTableEnum.PROCEDURE_OCCURRENCE, omop_procedure_occurrence_df)
    loader.save(OmopTableEnum.MEASUREMENT, omop_measurement_df)
    loader.save(OmopTableEnum.CONDITION_OCCURRENCE, omop_condition_occurrence_df)
    logging.info("Done loading omop tables into the common.")


if __name__ == "__main__":
    csv_dir, db_config = generate_config()
    run_etl_job(csv_dir, db_config)
