import pandas as pd
import extract
import transform
import os
import yaml
import sys
import getopt
import logging
from load import DBManager, OmopTableEnum, DbConfig
# type hints
from typing import Tuple, Optional, Dict


def generate_config() -> Tuple[str, DbConfig]:
    """
    Combines the config-file and command line arguments to one configuration, including database credentials and the
    path to the input directory.

    :return: dir with csv files, config options for the db
    """
    # path to default config file
    config_path = "config.yml"

    # cmd arguments
    argv = sys.argv[1:]

    # parse cmd options
    opts, args = getopt.getopt(argv, "H:P:N:u:p:S:D:C:l:h", ["host =",
                                                              "port =",
                                                              "db_name =",
                                                              "username =",
                                                              "password =",
                                                              "db_schema =",
                                                              "csv_dir =",
                                                              "config_file =",
                                                              "log_level =" 
                                                              "help"])
    tmp_dict: dict = {}
    tmp_csv_dir: Optional[str] = None
    tmp_log_level: Optional[int] = None
    for opt, arg in opts:
        opt = opt.strip()
        arg = arg.strip()
        if opt in ("-H", "--host"):
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
        elif opt in ("-l", "--log_level"):
            tmp_log_level = int(arg)
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
            -l, --log_level  \t log level: (int)
                                    - CRITICAL = 50
                                    - ERROR = 40
                                    - WARNING = 30 (default)
                                    - INFO = 20
                                    - DEBUG = 10
                                    - NOTSET = 0
            -h, --help      \t opens this menu
            ''')
            sys.exit(0)

    # load configuration file
    with open(config_path) as file:
        data = yaml.load(file, Loader=yaml.SafeLoader)

    # override config with cmd arguments
    if all(key in data for key in ["db_config", "csv_dir", "log_level"]):
        data["db_config"].update(tmp_dict)
        data["csv_dir"] = tmp_csv_dir if tmp_csv_dir is not None else data["csv_dir"]

        # set log_level
        tmp_log_level = tmp_log_level if tmp_log_level is not None else data["log_level"]
        log_levels = [0, 10, 20, 30, 40, 50]
        if tmp_log_level not in log_levels:
            logging.error(f"The log level has to be: {log_levels}, but continue with: 30 (WARNING)")
            logging.basicConfig(level=30)
        else:
            logging.basicConfig(level=tmp_log_level)
            logging.info(f"log_level set to: {tmp_log_level}")
        del data["log_level"]
    else:
        logging.error("The default config.yaml is invalid.")
        sys.exit(0)

    # check config / type checking
    expected_config_format: Dict[str, type] = DbConfig.__annotations__
    check_ok: bool = True
    for k, v in data["db_config"].items():
        if k not in expected_config_format:
            check_ok = False
            logging.error(f"There is no configuration Argument with the name: {k}")
        else:
            if not isinstance(v, expected_config_format[k]):
                check_ok = False
                logging.error(f"The Argument: {k} should have the type {expected_config_format[k]} not {type(v)}")

            del expected_config_format[k]

    if len(expected_config_format) != 0:
        check_ok = False
        logging.error(f"The following arguments are missing for a correct configuration: {list(expected_config_format.keys())}")

    csv_files = ["PERSON.csv", "CASE.csv", "LAB.csv", "DIAGNOSIS.csv", "PROCEDURE.csv"]
    if not (os.path.isdir(data["csv_dir"]) and
            all(csv_table in os.listdir(data["csv_dir"]) for csv_table in csv_files)):
        check_ok = False
        logging.error(f"The csv_dir should contain the following files: {csv_files}. Wrong path: {data['csv_dir']}")

    if not check_ok:
        logging.error("Shutting down ETL-process due to wrong configuration.")
        sys.exit(0)

    return data["csv_dir"], data["db_config"]


def run_etl_job(csv_dir: str, db_config: DbConfig):
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

    # Load into postgres database
    logging.info("Loading omop tables into the database...")
    loader.save(OmopTableEnum.PROVIDER, omop_provider_df)
    loader.save(OmopTableEnum.LOCATION, omop_location_df)
    loader.save(OmopTableEnum.PERSON, omop_person_df)
    loader.save(OmopTableEnum.OBSERVATION_PERIOD, omop_observation_period_df)
    loader.save(OmopTableEnum.VISIT_OCCURRENCE, omop_visit_occurrence_df)
    loader.save(OmopTableEnum.PROCEDURE_OCCURRENCE, omop_procedure_occurrence_df)
    loader.save(OmopTableEnum.MEASUREMENT, omop_measurement_df)
    loader.save(OmopTableEnum.CONDITION_OCCURRENCE, omop_condition_occurrence_df)
    logging.info("Done loading omop tables into the database.")


if __name__ == "__main__":
    csv_dir, db_config = generate_config()
    run_etl_job(csv_dir, db_config)


