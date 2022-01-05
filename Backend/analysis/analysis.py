import logging

from Backend.analysis.patient import Patient
from Backend.common.config import generate_config
from Backend.common.database import DBManager


def evaluate_patient(db_manager, patient_id):
    """
    Evaluates the pims and kawasaki-scores for a single patient.

    :param db_manager: Database-Manager with a running connection to the common
    :param patient_id: id of the patient
    :return: A Tuple containing another tuple with the score for kawasaki and reasons if not 0.0 and the score for pims
    with the reasons for pims if not 0.0
    """

    # Create patient object from common query
    query = f"SELECT * FROM cds_cdm.person WHERE person_id = {patient_id}"
    df = db_manager.send_query(query)
    patient_id = df.iloc[0]['person_id']
    day = df.iloc[0]['day_of_birth']
    month = df.iloc[0]['month_of_birth']
    year = df.iloc[0]['year_of_birth']
    name = df.iloc[0]['person_source_value']
    patient = Patient(patient_id, day, month, year, name)

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

    return patient.get_patient_as_tuple()


def evaluate_patients(db_manager, patient_ids: list):
    """
    Evaluates all given patients for having kawasaki or pims.

    :param db_manager: Database-Manager with a running connection to the common
    :param patient_ids: list of patient ids
    :return: List of Tuples containing scores and reasons for kawasaki and pims for every patient
    """
    logging.info(f"Evaluating {len(patient_ids)} patients.")
    evaluations = list()
    for patient_id in patient_ids:
        result = evaluate_patient(db_manager, patient_id)
        evaluations.append(result)
    logging.info(f"Finished evaluating {len(patient_ids)} patients.")
    return evaluations


def evaluate_all_in_database(db_manager):
    """
    Evaluates all patients currently stored in the common.

    :param db_manager: DatabaseManager with an active connection to the common
    :return: List of Tuples containing scores and reasons for kawasaki and pims for every patient
    """
    # load all patient_ids from db as patient_ids
    logging.info("Evaluating all patients currently in the given OMOP-Database.")
    query = f"SELECT person_id FROM cds_cdm.person"
    df = db_manager.send_query(query)
    patient_ids = df['person_id'].values.tolist()
    result = evaluate_patients(db_manager, patient_ids)
    logging.info(f"Finished evaluating all patients currently in the common.")
    return result


if __name__ == "__main__":
    db_config = generate_config()
    dbManager = DBManager(db_config, clear_tables=False)
    print(evaluate_all_in_database(dbManager))
