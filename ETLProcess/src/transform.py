import numpy
import pandas as pd


def generate_provider_table(person_df: pd.DataFrame, case_df: pd.DataFrame):
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


def generate_location_table(person_df: pd.DataFrame):
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


def generate_observation_period_table(case_df: pd.DataFrame):
    """
    Generates an omop compliant version of the observation_period table from a given case table.

    :param case_df: the original version of the case table
    :return: an omop compliant version of a observation_period table
    """
    # Get unique patient ids
    unique_patient_ids: numpy.ndarray = case_df['PATIENT_ID'].unique()
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


def generate_person_table(person_df: pd.DataFrame):
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

    # Remove entries with missing values
    omop_person_df.dropna()
    return omop_person_df


def generate_visit_occurrence_table(case_df: pd.DataFrame):
    """
    Generates an omop compliant version of the visit_occurrence table from a given case table.

    :param case_df: the original version of the case table
    :return: an omop compliant version of a visit_occurrence table
    """
    omop_visit_occurence_df: pd.DataFrame = case_df.copy(deep=True)
    # Rename columns to target values
    omop_visit_occurence_df.columns = ['visit_occurrence_id', 'provider_id', 'person_id', 'visit_start_date',
                                       'visit_end_date']
    # Generate unique visit occurrence ids because case ids are duplicated
    for index, row in omop_visit_occurence_df.iterrows():
        omop_visit_occurence_df.at[index, 'visit_occurrence_id'] = index + 1

    # Add values for visit_concept_id and visit_type_concept_id
    # 32209 unknown value, 32817 EHR
    omop_visit_occurence_df['visit_concept_id'] = 32209
    omop_visit_occurence_df['visit_type_concept_id'] = 32817
    return omop_visit_occurence_df
