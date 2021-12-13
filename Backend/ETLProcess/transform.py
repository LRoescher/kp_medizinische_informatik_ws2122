import numpy as np
import pandas as pd

from load import DBManager


def generate_provider_table(person_df: pd.DataFrame, case_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates an omop compliant version of the provider table from a given person and case table.

    :param person_df: the original version of the person table
    :param case_df: the original version of the case table
    :return: an omop compliant version of a provider table
    """
    combined_df: pd.DataFrame = pd.concat([person_df, case_df])
    # Copy provider id
    omop_provider_df: pd.DataFrame = combined_df[['PROVIDER_ID']].copy(deep=True)
    # Rename provider id
    omop_provider_df.columns = ['provider_id']
    # Delete duplicates
    omop_provider_df = omop_provider_df.drop_duplicates()
    return omop_provider_df


def generate_location_table(person_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates an omop compliant version of the location table from a given person table.

    :param person_df: the original version of the person table
    :return: an omop compliant version of a location table
    """
    # Copy only id, city and zip
    omop_location_df: pd.DataFrame = person_df[['PATIENT_ID', 'CITY', 'ZIP']].copy(deep=True)
    # Rename person_id to location id, should be unique
    omop_location_df.columns = ['location_id', 'city', 'zip']
    return omop_location_df


def generate_observation_period_table(case_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates an omop compliant version of the observation_period table from a given case table.

    :param case_df: the original version of the case table
    :return: an omop compliant version of a observation_period table
    """
    # Get unique patient ids
    unique_patient_ids: np.ndarray = case_df['PATIENT_ID'].unique()
    # Create a list of observation periods for every patient
    observation_periods: list = []
    # Generate observation period ids because case ids are duplicated
    observation_period_id: int = 1
    period_type_concept_id: int = 32817
    for patient_id in unique_patient_ids:
        subset: pd.DataFrame = case_df[case_df['PATIENT_ID'] == patient_id]
        start_date: object = subset['START_DATE'].min()
        end_date: object = subset['END_DATE'].max()
        observation_periods.append([observation_period_id, patient_id, start_date, end_date, period_type_concept_id])
        observation_period_id += 1
    # Create omop compliant dataframe out of the list
    omop_observation_period_df: pd.DataFrame = pd.DataFrame(observation_periods, columns=[
        'observation_period_id',
        'person_id',
        'observation_period_start_date',
        'observation_period_end_date',
        'period_type_concept_id'])

    return omop_observation_period_df


def generate_person_table(person_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates an omop compliant version of the person table from a given person table.

    :param person_df: the original version of the person table
    :return: an omop compliant version of a person table
    """
    omop_person_df: pd.DataFrame = person_df[['PROVIDER_ID', 'PATIENT_ID', 'GENDER', 'BIRTHDATE']].copy(deep=True)
    # Rename columns to source values
    omop_person_df.columns = ['provider_id', 'person_source_value', 'gender_source_value', 'birth_datetime']
    # Refactor birth_datetime
    # Add column for person_id, year/month/day_of_birth, gender_concept id
    omop_person_df['person_id'] = omop_person_df['person_source_value']
    omop_person_df['location_id'] = omop_person_df['person_source_value']
    omop_person_df['gender_concept_id'] = [8532 if g == 'w' else 8507 if g == 'm' else 0 for g in
                                           omop_person_df['gender_source_value']]
    omop_person_df['birth_datetime'] = pd.to_datetime(omop_person_df['birth_datetime'], format='%Y-%m-%d')
    omop_person_df['year_of_birth'] = omop_person_df['birth_datetime'].dt.year
    omop_person_df['month_of_birth'] = omop_person_df['birth_datetime'].dt.month
    omop_person_df['day_of_birth'] = omop_person_df['birth_datetime'].dt.day

    # Fill non-null columns with dummy data
    # 4218674 Unknown racial group, 0 as ethnicity (no value for unknown)
    omop_person_df['race_concept_id'] = 4218674
    omop_person_df['ethnicity_concept_id'] = 0
    return omop_person_df


def generate_visit_occurrence_table(case_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates an omop compliant version of the visit_occurrence table from a given case table.

    :param case_df: the original version of the case table
    :return: an omop compliant version of a visit_occurrence table
    """
    omop_visit_occurrence_df: pd.DataFrame = case_df.copy(deep=True)
    # Rename columns to target values
    omop_visit_occurrence_df.columns = ['visit_occurrence_id', 'provider_id', 'person_id', 'visit_start_date',
                                        'visit_end_date']
    # Generate unique visit occurrence ids because case ids are duplicated
    for index, row in omop_visit_occurrence_df.iterrows():
        omop_visit_occurrence_df.at[index, 'visit_occurrence_id'] = index + 1

    # Add values for visit_concept_id and visit_type_concept_id
    # Concept 38004515 Hospital
    # Concept 44818518 Visit derived from EHR record
    omop_visit_occurrence_df['visit_concept_id'] = 38004515
    omop_visit_occurrence_df['visit_type_concept_id'] = 44818518
    return omop_visit_occurrence_df


def generate_procedure_occurrence_table(procedure_df: pd.DataFrame, loader: DBManager) -> pd.DataFrame:
    """
    Generates an omop compliant version of the procedure_occurrence table from a given procedure table.

    :param loader: Loader used to query database for snomed codes
    :param procedure_df: the original version of the procedure table
    :return: an omop compliant version of a procedure_occurrence table
    """
    # Change datatype of column ID to int
    procedure_df = procedure_df.astype({'ID': int})
    # Copy values from original dataframe to omop compliant version
    omop_procedure_occurrence_df: pd.DataFrame = procedure_df[['ID', 'OPS_CODE', 'PATIENT_ID', 'EXECUTION_DATE']] \
        .copy(deep=True)
    # Rename columns to target values
    omop_procedure_occurrence_df.columns = ['procedure_occurrence_id',
                                            'procedure_source_value',
                                            'person_id',
                                            'procedure_datetime']
    # Refactor procedure_date
    omop_procedure_occurrence_df['procedure_date'] = pd.to_datetime(omop_procedure_occurrence_df['procedure_datetime'],
                                                                    format='%Y-%m-%d').dt.date

    omop_procedure_occurrence_df['procedure_concept_id'] = [loader.get_snomed_id(code, 'OPS') for code in
                                                            omop_procedure_occurrence_df['procedure_source_value']]
    # Add value for procedure_type_concept_id
    # 32817 EHR
    omop_procedure_occurrence_df['procedure_type_concept_id'] = 32817
    omop_procedure_occurrence_df.dropna()
    return omop_procedure_occurrence_df


def generate_measurement_table(lab_df: pd.DataFrame, loader: DBManager) -> pd.DataFrame:
    """
    Generates an omop compliant version of the measurement table from a given lab table.

    :param loader: Loader used to query database for snomed codes
    :param lab_df: the original version of the lab table
    :return: an omop compliant version of a measurement table
    """
    # Remove all columns with no identifier
    lab_df = lab_df.dropna(subset=['IDENTIFIER'])
    # Change datatype of column ID to int
    lab_df = lab_df.astype({'IDENTIFIER': int})
    # Copy values from original dataframe to omop compliant version
    omop_measurement_df: pd.DataFrame = lab_df[['IDENTIFIER', 'PARAMETER_NAME', 'PARAMETER_LOINC',
                                                'Patientidentifikator', 'TEST_DATE', 'NUMERIC_VALUE',
                                                'UCUM_UNIT', 'IS_NORMAL', 'DEVIATION']].copy(deep=True)
    # Get Patient-ID from Patientidentifikator
    for index, row in omop_measurement_df.iterrows():
        patientidentifikator: str = row['Patientidentifikator']
        patientidentifikator = patientidentifikator[-4:]
        omop_measurement_df.at[index, 'Patientidentifikator'] = int(patientidentifikator)

    # Translate IS_NORMAL and DEVIATION values to value_as_concept_id and delete old columns
    # 4124457 = normal range, 4328749 = high, 4267416 = low
    omop_measurement_df['value_as_concept_id'] = np.where(omop_measurement_df['IS_NORMAL'] == 1, 4124457,
                                                          np.where(omop_measurement_df['DEVIATION'] == "+", 4328749,
                                                                   4267416))
    omop_measurement_df.drop(columns=['IS_NORMAL', 'DEVIATION'], axis=1, inplace=True)
    # Rename columns to target values
    omop_measurement_df.columns = ['measurement_id', 'measurement_source_value', 'measurement_concept_id',
                                   'person_id', 'measurement_date', 'value_as_number', 'unit_source_value',
                                   'value_as_concept_id']
    omop_measurement_df['measurement_datetime'] = omop_measurement_df['measurement_date']
    # Refactor measurement_date
    omop_measurement_df['measurement_date'] = pd.to_datetime(omop_measurement_df['measurement_date'],
                                                             format='%Y-%m-%d').dt.date
    # Translate LOINC to SNOMED
    omop_measurement_df['measurement_concept_id'] = [loader.get_snomed_id(code, 'LOINC') for code in
                                                     lab_df['PARAMETER_LOINC']]

    # Add value for measurement_concept_type_id
    # 32856 Lab
    omop_measurement_df['measurement_type_concept_id'] = 32856
    return omop_measurement_df


def generate_condition_occurrence_table(diagnosis_df: pd.DataFrame, loader: DBManager) -> pd.DataFrame:
    """
    Generates an omop compliant version of the condition_occurrence table from a given diagnosis table.

    :param diagnosis_df: the original version of the diagnosis table
    :param loader: Loader used to query database for snomed codes
    :return: an omop compliant version of a condition_occurrence table
    """
    # Remove all columns with no admission date
    diagnosis_df.dropna(subset=['ADMISSION_DATE'], inplace=True)

    # Set Type-Concept-Id to 44786627 Concept code for 'Primary Condition' or 44786629 for 'Secondary Condition'
    conditions = [
        (diagnosis_df['DIAGNOSIS_TYPE'] == 'HD'),
        (diagnosis_df['DIAGNOSIS_TYPE'] == 'ND')]
    choices = [44786627, 44786629]
    diagnosis_df['temp'] = np.select(conditions, choices, default=0)

    # Create table containing primary ICD Codes
    primary_condition_df = diagnosis_df[
        ['PROVIDER_ID', 'PATIENT_ID', 'ADMISSION_DATE', 'ICD_PRIMARY_CODE', 'temp']].copy(deep=True)
    # Rename columns
    primary_condition_df.columns = ['provider_id', 'person_id', 'condition_start_date', 'condition_source_value',
                                    'condition_type_concept_id']

    # Create table containing secondary ICD Codes
    secondary_condition_df = diagnosis_df[
        ['PROVIDER_ID', 'PATIENT_ID', 'ADMISSION_DATE', 'ICD_SECONDARY_CODE', 'temp']].copy(deep=True)
    # Drop rows where the secondary code ist either null or '-'
    secondary_condition_df.dropna(subset=['ICD_SECONDARY_CODE'], inplace=True)
    secondary_condition_df = secondary_condition_df[secondary_condition_df['ICD_SECONDARY_CODE'] != "-"]
    # Rename columns
    secondary_condition_df.columns = ['provider_id', 'person_id', 'condition_start_date', 'condition_source_value',
                                      'condition_type_concept_id']

    # Append primary and secondary ICD code tables
    omop_condition_occurrence: pd.DataFrame = pd.concat([primary_condition_df, secondary_condition_df],
                                                        ignore_index=True)
    
    # Get Snomed Ids for ICD 10 GM codes
    omop_condition_occurrence['condition_concept_id'] = [loader.get_snomed_id(icd, 'ICD10GM') for icd in
                                                         omop_condition_occurrence['condition_source_value']]

    # Refactor condition_start_date
    omop_condition_occurrence['condition_start_date'] = pd.to_datetime(
        omop_condition_occurrence['condition_start_date'],
        format='%d.%m.%Y')

    # Generate condition_occurrence_id
    for index, row in omop_condition_occurrence.iterrows():
        omop_condition_occurrence.at[index, 'condition_occurrence_id'] = index + 1

    omop_condition_occurrence.dropna(inplace=True)
    return omop_condition_occurrence
