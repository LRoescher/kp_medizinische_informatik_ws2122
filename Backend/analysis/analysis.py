import datetime
import logging
from typing import List, Optional
from Backend.analysis.patient import Patient
from Backend.common.database import DBManager
from Backend.common.omop_enums import OmopPersonFieldsEnum, OmopTableEnum, OmopObservationPeriodFieldsEnum


def evaluate_patient(db_manager: DBManager, patient_id: int) -> Optional[Patient]:
    """
    Evaluates the pims and kawasaki-scores for a given patient id. If the patient id does not exists in the database
    this will return None. This also returns None if the database connection is invalid.

    :param db_manager: Database-Manager with a running connection to the database
    :param patient_id: id of the patient
    :return: A patient with scores calculated for each disease
    """
    try:
        # Get basic person data
        query = f"SELECT * FROM cds_cdm.{OmopTableEnum.PERSON.value} WHERE person_id = {patient_id}"
        df = db_manager.send_query(query)
        patient_id = df.iloc[0]['person_id']
        day = df.iloc[0]['day_of_birth']
        month = df.iloc[0]['month_of_birth']
        year = df.iloc[0]['year_of_birth']
        birthdate = datetime.date(year, month, day)
        name = df.iloc[0]['person_source_value']

        # Get (latest) case date from observation period
        case_date = datetime.date.today()
        try:
            query = f"SELECT * FROM cds_cdm.{OmopTableEnum.OBSERVATION_PERIOD.value} " \
                    f"WHERE {OmopObservationPeriodFieldsEnum.PERSON_ID.value} = {patient_id}"
            df = db_manager.send_query(query)
            case_date = df.iloc[0]['observation_period_end_date']
        except (AttributeError, IndexError):
            logging.warning("Could not find a valid case date. Using today.")
            case_date = datetime.date.today()

        # Create patient object from the database query
        patient = Patient(patient_id=patient_id, name=name, birthdate=birthdate, case_date=case_date)

        # Get all conditions for every patient
        query = f"SELECT * FROM cds_cdm.condition_occurrence WHERE person_id = {patient_id}"
        df = db_manager.send_query(query)
        for index, row in df.iterrows():
            patient.add_condition(row['condition_concept_id'])

        # Get all measurements with a high value for every patient
        concept_high = 4328749
        query = f"SELECT * FROM cds_cdm.measurement WHERE person_id = {patient_id} AND value_as_concept_id = {concept_high}"
        df = db_manager.send_query(query)
        for index, row in df.iterrows():
            patient.add_high_measurement(row['measurement_concept_id'])

        # For Kawasaki and PIMS only high lab results seem to be relevant for other diseases the concepts for
        # normal = 4124457 and low = 4267416 should be checked

        patient.calculate_kawasaki_score()
        patient.calculate_pims_score()
    except AttributeError as error:
        logging.error("Error during Analysis.")
        logging.error(error)
        patient = None

    return patient


def evaluate_patients(db_manager: DBManager, patient_ids: List[int]) -> List[Patient]:
    """
    Evaluates all given patients for having kawasaki or pims.

    :param db_manager: Database-Manager with a running connection to the database
    :param patient_ids: list of patient ids
    :return: List of patients
    """
    patients: List[Patient] = list()
    try:
        logging.info(f"Evaluating {len(patient_ids)} patients.")
        patients = list()
        for patient_id in patient_ids:
            patient = evaluate_patient(db_manager, patient_id)
            if patient:
                patients.append(patient)
        logging.info(f"Finished evaluating {len(patient_ids)} patients.")
    except TypeError:
        # None returned
        logging.error("Error during evaluation. List of Patients might be incomplete")
    return patients


def evaluate_all_in_database(db_manager: DBManager) -> List[Patient]:
    """
    Evaluates all patients currently stored in the database.

    :param db_manager: DatabaseManager with an active connection to the database
    :return: List of patients
    """
    patients: List[Patient] = list()
    try:
        # load all patient_ids from db as patient_ids
        logging.info("Evaluating all patients currently in the given OMOP-Database.")
        query = f"SELECT {OmopPersonFieldsEnum.PERSON_ID.value} FROM {db_manager.DB_SCHEMA}.{OmopTableEnum.PERSON.value}"
        df = db_manager.send_query(query)
        patient_ids = df['person_id'].values.tolist()
        patients = evaluate_patients(db_manager, patient_ids)
        logging.info(f"Finished evaluating all patients currently in the database.")
    except (TypeError, AttributeError):
        logging.error("Error during evaluation. List of Patients might be incomplete")
    return patients
