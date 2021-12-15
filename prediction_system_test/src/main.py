import pandas as pd
import os
import yaml
import sys
import getopt
import logging
from database import DBManager, OmopTableEnum, DbConfig
# type hints
from typing import Tuple, Optional, Dict

from src.patient import Patient


def generate_config() -> Tuple[DbConfig]:
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
    if all(key in data for key in ["db_config", "log_level"]):
        data["db_config"].update(tmp_dict)

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

    return data["db_config"]


def evaluate_patient(dbManager, patient_id):
    """
    ToDo
    """
    # print(f"evaluating patient {patient_id}")

    # Create patient object from database query
    query = f"SELECT * FROM cds_cdm.person WHERE person_id = {patient_id}"
    df = dbManager.send_query(query)
    id = df.iloc[0]['person_id']
    day = df.iloc[0]['day_of_birth']
    month = df.iloc[0]['month_of_birth']
    year = df.iloc[0]['year_of_birth']
    patient = Patient(id, day, month, year)

    query = f"SELECT * FROM cds_cdm.condition_occurrence WHERE person_id = {patient_id}"
    df = dbManager.send_query(query)
    for index, row in df.iterrows():
        patient.add_condition(row['condition_concept_id'])

    # Do Similar with procedure and measurement

    evaluation_kawasaki = patient.calculate_kawasaki_score()
    evaluation_pims = patient.calculate_pims_score()

    return evaluation_kawasaki, evaluation_pims


def evaluate_patients(dbManager, patient_ids):
    """
    ToDo
    :param dbManager:
    :param patient_ids:
    :return:
    """
    evaluations = list()
    for patient_id in patient_ids:
        result = evaluate_patient(dbManager, patient_id)
        evaluations.append((patient_id, result))
    print(evaluations)


def evaluate_all_in_database(dbManager):
    """
    ToDo
    :param db_config:
    :return:
    """
    # load all patient_ids from db as patient_ids
    # return evaluate_patients(patient_ids)
    query = f"SELECT person_id FROM cds_cdm.person"
    df = dbManager.send_query(query)
    patient_ids = df['person_id'].values.tolist()
    result = evaluate_patients(dbManager, patient_ids)


if __name__ == "__main__":
    db_config = generate_config()
    dbManager = DBManager(db_config, clear_tables=False)
    # evaluate_patient(dbManager, 1000)
    evaluate_all_in_database(dbManager)


