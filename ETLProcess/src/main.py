import pandas as pd

import extract
import transform
import load

# TODO: Move constants to Config file and load them

PATH_TO_PERSON_CSV: str = "../../data/1. Bereistellung Daten/PERSON.csv"
PATH_TO_LAB_CSV: str = "../../data/1. Bereistellung Daten/LAB.csv"
PATH_TO_DIAGNOSIS_CSV: str = "../../data/1. Bereistellung Daten/DIAGNOSIS.csv"
PATH_TO_PROCEDURE_CSV: str = "../../data/1. Bereistellung Daten/PROCEDURE.csv"
PATH_TO_CASE_CSV: str = "../../data/1. Bereistellung Daten/CASE.csv"


def run_etl_job():
    """
    Runs the entire ETL-Job.
    First all csv files are transformed into pandas dataframes. Then they are transformed into omop compliant tables.
    Finally they are loaded into the postgres database.
    :return: void
    """
    # extract original csv files
    person_df: pd.DataFrame = extract.extract_csv(PATH_TO_PERSON_CSV)
    case_df: pd.DataFrame = extract.extract_csv(PATH_TO_CASE_CSV)
    lab_df: pd.DataFrame = extract.extract_csv(PATH_TO_LAB_CSV)
    diagnosis_df: pd.DataFrame = extract.extract_csv(PATH_TO_DIAGNOSIS_CSV)
    procedure_df: pd.DataFrame = extract.extract_csv(PATH_TO_PROCEDURE_CSV)

    # Transform into omop tables
    omop_location_df: pd.DataFrame = transform.generate_location_table(person_df)
    omop_person_df: pd.DataFrame = transform.generate_person_table(person_df)
    # TODO transform other tables

    # Load into postgres database
    loader = load.Loader()
    loader.save_location(omop_location_df)
    loader.save_person(omop_person_df)
    # TODO load other dataframes into postgres


if __name__ == "__main__":
    run_etl_job()
