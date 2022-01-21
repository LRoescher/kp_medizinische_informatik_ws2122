import datetime
from typing import List

import pandas as pd
import os
import logging

from Backend.analysis.patient import Patient
from Backend.common.config import DbConfig, generate_config
from Backend.common.database import DBManager
from Backend.common.omop_enums import OmopTableEnum, OmopPersonFieldsEnum, OmopLocationFieldsEnum, \
    OmopProviderFieldsEnum, OmopConditionOccurrenceFieldsEnum, SnomedConcepts, OmopObservationPeriodFieldsEnum, \
    OmopMeasurementEnum
from Backend.etl import extract, transform
from Backend.etl.csv_enums import CsvFilesEnum


def run_etl_job_for_csvs(csv_dir: str, db_config: DbConfig) -> bool:
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
    person_df: pd.DataFrame = extract.extract_csv(CsvFilesEnum.PERSON.value)
    case_df: pd.DataFrame = extract.extract_csv(CsvFilesEnum.CASE.value)
    lab_df: pd.DataFrame = extract.extract_csv(CsvFilesEnum.LAB.value)
    diagnosis_df: pd.DataFrame = extract.extract_csv(CsvFilesEnum.DIAGNOSIS.value)
    procedure_df: pd.DataFrame = extract.extract_csv(CsvFilesEnum.PROCEDURE.value)
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
    try:
        omop_procedure_occurrence_df: pd.DataFrame = transform.generate_procedure_occurrence_table(procedure_df,
                                                                                                   db_manager)
        omop_measurement_df: pd.DataFrame = transform.generate_measurement_table(lab_df,
                                                                                 db_manager)
        omop_condition_occurrence_df: pd.DataFrame = transform.generate_condition_occurrence_table(diagnosis_df,
                                                                                                   db_manager)
    except AttributeError:
        logging.error("Error during Transformation.")
        return False
    logging.info("Transformations finished.")

    # Load into postgres database
    logging.info("Loading omop tables into the database...")
    try:
        db_manager.save(OmopTableEnum.PROVIDER, omop_provider_df)
        db_manager.save(OmopTableEnum.LOCATION, omop_location_df)
        db_manager.save(OmopTableEnum.PERSON, omop_person_df)
        db_manager.save(OmopTableEnum.OBSERVATION_PERIOD, omop_observation_period_df)
        db_manager.save(OmopTableEnum.VISIT_OCCURRENCE, omop_visit_occurrence_df)
        db_manager.save(OmopTableEnum.PROCEDURE_OCCURRENCE, omop_procedure_occurrence_df)
        db_manager.save(OmopTableEnum.MEASUREMENT, omop_measurement_df)
        db_manager.save(OmopTableEnum.CONDITION_OCCURRENCE, omop_condition_occurrence_df)
        logging.info("Done loading omop tables into the database.")
        return True
    except AttributeError:
        return False


def run_etl_job_for_patient(patient: Patient, db_manager: DBManager) -> bool:
    """
    Runs an etl-job for a single given patient on the connection specified by the given database manager.
    """
    logging.info("Extracting data from the given patient...")

    data_person = {OmopPersonFieldsEnum.PERSON_ID.value: [patient.id],
                   OmopPersonFieldsEnum.GENDER_CONCEPT_ID.value: [0],
                   OmopPersonFieldsEnum.YEAR_OF_BIRTH.value: [patient.year],
                   OmopPersonFieldsEnum.MONTH_OF_BIRTH.value: [patient.month],
                   OmopPersonFieldsEnum.DAY_OF_BIRTH.value: [patient.day],
                   OmopPersonFieldsEnum.BIRTH_DATETIME.value: [patient.birthdate],
                   OmopPersonFieldsEnum.RACE_CONCEPT_ID.value: [4218674],
                   OmopPersonFieldsEnum.ETHNICITY_CONCEPT_ID.value: [0],
                   OmopPersonFieldsEnum.LOCATION_ID.value: [patient.id],
                   OmopPersonFieldsEnum.PROVIDER_ID.value: [DBManager.PROVIDER_ID],
                   OmopPersonFieldsEnum.PERSON_SOURCE_VALUE.value: [patient.name],
                   OmopPersonFieldsEnum.GENDER_SOURCE_VALUE.value: ['w']}
    omop_person_df: pd.DataFrame = pd.DataFrame(data_person)

    data_location = {OmopLocationFieldsEnum.LOCATION_ID.value: [patient.id],
                     OmopLocationFieldsEnum.CITY.value: ['Unbekannt'],
                     OmopLocationFieldsEnum.ZIP.value: ['Unbekannt']}
    omop_location_df: pd.DataFrame = pd.DataFrame(data_location)

    # Set current date as observation start and end date
    current_date: datetime.date = datetime.date.today()
    # Generate unused case id
    try:
        case_id: int = db_manager.generate_case_id()
    except AttributeError:
        logging.error("Error during database access.")
        return False
    data_observation_period = {OmopObservationPeriodFieldsEnum.ID.value: [case_id],
                               OmopObservationPeriodFieldsEnum.PERSON_ID.value: [patient.id],
                               OmopObservationPeriodFieldsEnum.START_DATE.value: [current_date],
                               OmopObservationPeriodFieldsEnum.END_DATE.value: [current_date],
                               OmopObservationPeriodFieldsEnum.TYPE_CONCEPT_ID.value: [32817]}
    omop_observation_period_df: pd.DataFrame = pd.DataFrame(data_observation_period)

    data_provider = {OmopProviderFieldsEnum.PROVIDER_ID.value: [DBManager.PROVIDER_ID]}
    omop_provider_df: pd.DataFrame = pd.DataFrame(data_provider)

    # Generate unused ids for all conditions
    try:
        condition_occurrence_ids: List[int] = list()
        for _ in patient.conditions:
            condition_occurrence_id: int = db_manager.generate_condition_occurrence_id()
            while condition_occurrence_id in condition_occurrence_ids:
                condition_occurrence_id: int = db_manager.generate_condition_occurrence_id()
            condition_occurrence_ids.append(condition_occurrence_id)
    except AttributeError:
        logging.error("Error during database access.")
        return False

    current_date = datetime.datetime.now()
    entries = len(patient.conditions)

    # Create dataframe for conditions
    data_condition_occurrence = {
        OmopConditionOccurrenceFieldsEnum.CONDITION_OCCURRENCE_ID.value: condition_occurrence_ids,
        OmopConditionOccurrenceFieldsEnum.PERSON_ID.value: [patient.id] * entries,
        OmopConditionOccurrenceFieldsEnum.CONDITION_CONCEPT_ID.value: patient.conditions,
        OmopConditionOccurrenceFieldsEnum.CONDITION_START_DATE.value: [current_date] * entries,
        OmopConditionOccurrenceFieldsEnum.CONDITION_TYPE_CONCEPT_ID.value: [44786627] * entries
    }
    omop_condition_occurrence_df: pd.DataFrame = pd.DataFrame(data_condition_occurrence)

    # Generate unused ids for all measurement
    try:
        measurement_ids: List[int] = list()
        for _ in patient.high_measurements:
            measurement_id: int = db_manager.generate_measurement_id()
            while measurement_id in measurement_ids:
                measurement_id: int = db_manager.generate_measurement_id()
            measurement_ids.append(measurement_id)
    except AttributeError:
        logging.error("Error during database access.")
        return False

    entries = len(patient.high_measurements)

    data_measurement = {
        OmopMeasurementEnum.ID.value: measurement_ids,
        OmopMeasurementEnum.PERSON_ID.value: [patient.id] * entries,
        OmopMeasurementEnum.CONCEPT_ID.value: patient.high_measurements,
        OmopMeasurementEnum.DATE.value: [current_date] * entries,
        OmopMeasurementEnum.TYPE_CONCEPT_ID.value: [SnomedConcepts.LAB.value] * entries,
        OmopMeasurementEnum.VALUE_CONCEPT.value: [SnomedConcepts.HIGH.value] * entries
    }
    omop_measurement_df: pd.DataFrame = pd.DataFrame(data_measurement)

    # Load dataframe into the omop database
    try:
        db_manager.save(OmopTableEnum.LOCATION, omop_location_df)
        # Add Provider if provider id is not taken.
        if not db_manager.id_is_taken(OmopTableEnum.PROVIDER.value,
                                      OmopProviderFieldsEnum.PROVIDER_ID.value,
                                      DBManager.PROVIDER_ID):
            db_manager.save(OmopTableEnum.PROVIDER, omop_provider_df)
        db_manager.save(OmopTableEnum.PERSON, omop_person_df)
        db_manager.save(OmopTableEnum.OBSERVATION_PERIOD, omop_observation_period_df)
        db_manager.save(OmopTableEnum.CONDITION_OCCURRENCE, omop_condition_occurrence_df)
        db_manager.save(OmopTableEnum.MEASUREMENT, omop_measurement_df)
        logging.info("Done loading a single Patient into the database.")
        return True
    except AttributeError:
        logging.error("Error during database access.")
        return False


def update_patient(old_patient: Patient, update: Patient, db_manager: DBManager) -> bool:
    logging.info("Updating a patient...")
    try:
        db_manager.update_person_field(old_patient.id, OmopPersonFieldsEnum.PERSON_SOURCE_VALUE.value, update.name)
        db_manager.update_person_field(old_patient.id, OmopPersonFieldsEnum.DAY_OF_BIRTH.value, update.day)
        db_manager.update_person_field(old_patient.id, OmopPersonFieldsEnum.MONTH_OF_BIRTH.value, update.month)
        db_manager.update_person_field(old_patient.id, OmopPersonFieldsEnum.YEAR_OF_BIRTH.value, update.year)
        db_manager.update_person_field(old_patient.id, OmopPersonFieldsEnum.BIRTH_DATETIME.value, update.birthdate)

        if old_patient.has_covid() and not update.has_covid():
            # Remove covid from conditions
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.COVID_19.value)
        if not old_patient.has_covid() and update.has_covid():
            # Add covid as condition
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.COVID_19.value)

        if old_patient.has_fever() and not update.has_fever():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.FEVER.value)
        if not old_patient.has_fever() and update.has_fever():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.FEVER.value)

        if old_patient.has_exanthem() and not update.has_exanthem():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.ERUPTION.value)
        if not old_patient.has_exanthem() and update.has_exanthem():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.ERUPTION.value)

        if old_patient.has_enanthem() and not update.has_enanthem():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.DISORDER_OF_ORAL_SOFT_TISSUE.value)
        if not old_patient.has_enanthem() and update.has_enanthem():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.DISORDER_OF_ORAL_SOFT_TISSUE.value)

        if old_patient.has_swollen_extremities() and not update.has_swollen_extremities():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.SWELLING.value)
        if not old_patient.has_swollen_extremities() and update.has_swollen_extremities():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.SWELLING.value)

        if old_patient.has_conjunctivitis() and not update.has_conjunctivitis():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        if not old_patient.has_conjunctivitis() and update.has_conjunctivitis():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.OTHER_CONJUNCTIVITIS.value)

        if old_patient.has_lymphadenopathy() and not update.has_lymphadenopathy():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.LYMPHADENOPATHY.value)
        if not old_patient.has_lymphadenopathy() and update.has_lymphadenopathy():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.LYMPHADENOPATHY.value)

        if old_patient.has_gastro_intestinal_condition() and not update.has_gastro_intestinal_condition():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.NAUSEA_AND_VOMITING.value)
        if not old_patient.has_gastro_intestinal_condition() and update.has_gastro_intestinal_condition():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.NAUSEA_AND_VOMITING.value)

        if old_patient.has_pericardial_effusions() and not update.has_pericardial_effusions():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.PERICARDIAL_EFFUSION.value)
        if not old_patient.has_pericardial_effusions() and update.has_pericardial_effusions():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.PERICARDIAL_EFFUSION.value)

        if old_patient.has_pericarditis() and not update.has_pericarditis():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.PERICARDITIS.value)
        if not old_patient.has_pericarditis() and update.has_pericarditis():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.PERICARDITIS.value)

        if old_patient.has_myocarditis() and not update.has_myocarditis():
            db_manager.delete_condition_for_patient(old_patient.id, SnomedConcepts.MYOCARDITIS.value)
        if not old_patient.has_myocarditis() and update.has_myocarditis():
            _add_condition_for_patient(db_manager=db_manager,
                                       patient_id=old_patient.id,
                                       concept_id=SnomedConcepts.MYOCARDITIS.value)

        if old_patient.has_inflammation_lab() and not update.has_inflammation_lab():
            db_manager.delete_measurement_for_patient(old_patient.id, SnomedConcepts.CRP.value)
        if not old_patient.has_inflammation_lab() and update.has_inflammation_lab():
            _add_measurement_for_patient(db_manager=db_manager,
                                         patient_id=old_patient.id,
                                         concept_id=SnomedConcepts.CRP.value)

        logging.info("Done updating the patient.")
        return True
    except AttributeError:
        logging.info("Error during database access.")
        return False


def _add_condition_for_patient(db_manager: DBManager, patient_id: int, concept_id: int):
    # Create dataframe for conditions
    condition_occurrence_id: int = db_manager.generate_condition_occurrence_id()
    current_date = datetime.datetime.now()
    data_condition_occ = {OmopConditionOccurrenceFieldsEnum.CONDITION_OCCURRENCE_ID.value: [condition_occurrence_id],
                          OmopConditionOccurrenceFieldsEnum.PERSON_ID.value: [patient_id],
                          OmopConditionOccurrenceFieldsEnum.CONDITION_CONCEPT_ID.value: [concept_id],
                          OmopConditionOccurrenceFieldsEnum.CONDITION_START_DATE.value: [current_date],
                          OmopConditionOccurrenceFieldsEnum.CONDITION_TYPE_CONCEPT_ID.value: [44786627]}
    omop_condition_occurrence_df: pd.DataFrame = pd.DataFrame(data_condition_occ)
    # Save in database
    db_manager.save(OmopTableEnum.CONDITION_OCCURRENCE, omop_condition_occurrence_df)


def _add_measurement_for_patient(db_manager: DBManager, patient_id: int, concept_id: int):
    # Create dataframe for conditions
    measurement_id: int = db_manager.generate_measurement_id()
    current_date = datetime.datetime.now()
    data_measurement = {
        OmopMeasurementEnum.ID.value: [measurement_id],
        OmopMeasurementEnum.PERSON_ID.value: [patient_id],
        OmopMeasurementEnum.CONCEPT_ID.value: [concept_id],
        OmopMeasurementEnum.DATE.value: [current_date],
        OmopMeasurementEnum.TYPE_CONCEPT_ID.value: [SnomedConcepts.LAB.value],
        OmopMeasurementEnum.VALUE_CONCEPT.value: [SnomedConcepts.HIGH.value]
    }
    omop_measurement_df: pd.DataFrame = pd.DataFrame(data_measurement)
    # Save in database
    db_manager.save(OmopTableEnum.MEASUREMENT, omop_measurement_df)


if __name__ == "__main__":
    csv_dir, db_config = generate_config()
    run_etl_job_for_csvs(csv_dir, db_config)
