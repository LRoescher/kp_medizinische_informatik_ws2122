import pandas as pd

import extract
import transform
import load
import os
import yaml
import sys
import getopt

# type hints
from typing import Tuple, Optional


def generate_config() -> Tuple[str, load.DB_CONFIG]:
    '''
    combine config-file and cmd arguments

    :return: dir with csv files, config options for the db
    '''
    # path to default config file
    config_path = "config.yml"

    # cmd arguments
    argv = sys.argv[1:]

    # parse cmd options
    opts, args = getopt.getopt(argv, "H:P:N:u:p:S:D:C:h", ["host =",
                                                           "port =",
                                                           "db_name =",
                                                           "username =",
                                                           "password =",
                                                           "db_schema =",
                                                           "csv_dir =",
                                                           "config_file =",
                                                           "help"])
    tmp_dict: dict = {}
    tmp_csv_dir: Optional[str] = None
    for opt, arg in opts:
        opt = opt.strip()
        arg = arg.strip()
        if opt in ("-H", "--host"):
            print("host", opt, arg)
            tmp_dict["host"] = arg
        elif opt in ("-P", "--port"):
            tmp_dict["port"] = arg
        elif opt in ("-N", "--db_name"):
            tmp_dict["db_name"] = arg
        elif opt in ("-u", "--username"):
            tmp_dict["username"] = arg
        elif opt in ("-p", "--password"):
            tmp_dict["password"] = arg
        elif opt in ("-S", "--db_schema"):
            tmp_dict["db_schema"] = arg
        elif opt in ("-D", "--csv_dir"):
            tmp_csv_dir = arg
        elif opt in ("-C", "--config_file"):
            config_path = arg
        elif opt in ("-h", "--help"):
            print('''CMD Options:
            -H, --host      \t host of the postgres-DB
            -P, --port      \t port of the postgres-DB
            -N, --db_name   \t name of the postgres-DB
            -u, --username  \t postgres username
            -p, --password  \t postgres password
            -S, --db_schema \t postgres DB-Schema
            -D, --csv_dir   \t directory the following files are located:
                                    - PERSON.CSV
                                    - LAB.csv
                                    - DIAGNOSIS.csv
                                    - PROCEDURE.csv 
            -C, --config_file \t path to the config file
            ''')
            sys.exit(0)

    # load configuration file
    with open(config_path) as file:
        data = yaml.load(file, Loader=yaml.SafeLoader)

    # override config with cmd arguments
    data["db_config"].update(tmp_dict)
    data["csv_dir"] = tmp_csv_dir if tmp_csv_dir is not None else data["csv_dir"]

    return data["csv_dir"], data["db_config"]


def run_etl_job(csv_dir: str, db_config: load.DB_CONFIG):
    """
    Runs the entire ETL-Job.
    First all csv files are transformed into pandas dataframes. Then they are transformed into omop compliant tables.
    Finally they are loaded into the postgres database.

    :param csv_dir: Directory containing PERSON.csv, ..
    :param db_config: dict with keys: [host, port, db_name, username, password, db_schema]
    :return: void
    """
    # extract original csv files
    cwd = os.getcwd()
    os.chdir(csv_dir)

    person_df: pd.DataFrame = extract.extract_csv("PERSON.csv")
    case_df: pd.DataFrame = extract.extract_csv("CASE.csv")
    lab_df: pd.DataFrame = extract.extract_csv("LAB.csv")
    diagnosis_df: pd.DataFrame = extract.extract_csv("DIAGNOSIS.csv")
    procedure_df: pd.DataFrame = extract.extract_csv("PROCEDURE.csv")
    # Remove all rows with missing data
    procedure_df = procedure_df.dropna()

    os.chdir(cwd)

    # Transform into omop tables
    omop_provider_df: pd.DataFrame = transform.generate_provider_table(person_df, case_df)
    omop_location_df: pd.DataFrame = transform.generate_location_table(person_df)
    omop_person_df: pd.DataFrame = transform.generate_person_table(person_df)
    omop_observation_period_df: pd.DataFrame = transform.generate_observation_period_table(case_df)
    omop_visit_occurrence_df: pd.DataFrame = transform.generate_visit_occurrence_table(case_df)
    omop_procedure_occurrence_df: pd.DataFrame = transform.generate_procedure_occurrence_table(procedure_df)
    # TODO transform other tables

    # Load into postgres database
    # 'clear_tables' remove all previously added omop-entries from the database
    loader = load.Loader(db_config, clear_tables=True)
    loader.save(load.OMOP_TABLE.PROVIDER, omop_provider_df)
    loader.save(load.OMOP_TABLE.LOCATION, omop_location_df)
    loader.save(load.OMOP_TABLE.PERSON, omop_person_df)
    loader.save(load.OMOP_TABLE.OBSERVATION_PERIOD, omop_observation_period_df)
    loader.save(load.OMOP_TABLE.VISIT_OCCURRENCE, omop_visit_occurrence_df)
    loader.save(load.OMOP_TABLE.PROCEDURE_OCCURRENCE, omop_procedure_occurrence_df)
    # TODO load other dataframes into postgres


if __name__ == "__main__":
    csv_dir, db_config = generate_config()
    run_etl_job(csv_dir, db_config)
