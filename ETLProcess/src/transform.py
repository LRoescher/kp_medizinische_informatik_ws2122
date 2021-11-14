import pandas as pd


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
    # Copy Case-Id, Patient-Id, Start-Date and End-Date
    omop_observation_period_df: pd.DataFrame = case_df[['CASE_ID', 'PATIENT_ID', 'START_DATE', 'END_DATE']].copy(
        deep=True)
    # Rename columns
    omop_observation_period_df.columns = ['observation_period_id', 'person_id', 'observation_period_start_date',
                                          'observation_period_end_date']
    omop_observation_period_df['observation_period_start_date'] = pd.to_datetime(
        omop_observation_period_df['observation_period_start_date'],
        format='%Y-%m-%d')
    omop_observation_period_df['observation_period_end_date'] = pd.to_datetime(
        omop_observation_period_df['observation_period_end_date'],
        format='%Y-%m-%d')
    omop_observation_period_df['period_type_concept_id'] = 32817
    return omop_observation_period_df


def generate_person_table(person_df: pd.DataFrame):
    """
    Generates an omop compliant version of the person table from a given unedited person table.
    :param person_df: the original version of the person table
    :return: an omop compliant version of a person table
    """
    omop_person_df: pd.DataFrame = person_df[['PROVIDER_ID', 'PATIENT_ID', 'GENDER', 'BIRTHDATE', ]].copy(deep=True)
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
    omop_person_df['race_concept_id'] = ["4218674" for p in omop_person_df['person_source_value']]
    omop_person_df['ethnicity_concept_id'] = ["0" for p in omop_person_df['person_source_value']]

    # Remove entries with missing values
    omop_person_df.dropna()
    return omop_person_df
