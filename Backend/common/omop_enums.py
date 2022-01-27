from enum import Enum


class OmopTableEnum(Enum):
    """
    Enum for the table-names in the used OMOP-database.
    """
    VISIT_OCCURRENCE = "visit_occurrence"
    OBSERVATION_PERIOD = "observation_period"
    PROCEDURE_OCCURRENCE = "procedure_occurrence"
    MEASUREMENT = "measurement"
    CONDITION_OCCURRENCE = "condition_occurrence"
    PERSON = "person"
    LOCATION = "location"
    PROVIDER = "provider"


class OmopPersonFieldsEnum(Enum):
    """
    Enum for the fields of the person table.
    """
    PERSON_ID = "person_id"
    GENDER_CONCEPT_ID = "gender_concept_id"
    YEAR_OF_BIRTH = "year_of_birth"
    MONTH_OF_BIRTH = "month_of_birth"
    DAY_OF_BIRTH = "day_of_birth"
    BIRTH_DATETIME = "birth_datetime"
    RACE_CONCEPT_ID = "race_concept_id"
    ETHNICITY_CONCEPT_ID = "ethnicity_concept_id"
    LOCATION_ID = "location_id"
    PERSON_SOURCE_VALUE = "person_source_value"
    GENDER_SOURCE_VALUE = "gender_source_value"
    PROVIDER_ID = "provider_id"


class OmopConditionOccurrenceFieldsEnum(Enum):
    """
    Enum for the fields of the condition-occurrence table
    """
    CONDITION_OCCURRENCE_ID = 'condition_occurrence_id'
    PERSON_ID = 'person_id'
    CONDITION_CONCEPT_ID = 'condition_concept_id'
    CONDITION_START_DATE = 'condition_start_date'
    CONDITION_TYPE_CONCEPT_ID = 'condition_type_concept_id'
    CONDITION_SOURCE_VALUE = 'condition_source_value'


class OmopLocationFieldsEnum(Enum):
    """
    Enum for the fields of the location table.
    """
    LOCATION_ID = 'location_id'
    ZIP = 'zip'
    CITY = 'city'


class OmopProviderFieldsEnum(Enum):
    """
    Enum for the fields of the provider table.
    """
    PROVIDER_ID = 'provider_id'


class OmopObservationPeriodFieldsEnum(Enum):
    """
    Enum for the fields of the observation period table.
    """
    ID = 'observation_period_id'
    PERSON_ID = 'person_id'
    START_DATE = 'observation_period_start_date'
    END_DATE = 'observation_period_end_date'
    TYPE_CONCEPT_ID = 'period_type_concept_id'


class OmopMeasurementEnum(Enum):
    """
    Enum for the fields of the measurement table.
    """
    ID = 'measurement_id'
    PERSON_ID = 'person_id'
    CONCEPT_ID = 'measurement_concept_id'
    DATE = 'measurement_date'
    DATETIME = 'measurement_datetime'
    TYPE_CONCEPT_ID = 'measurement_type_concept_id'
    VALUE_NUMBER = "value_as_number"
    VALUE_CONCEPT = "value_as_concept_id"
    SOURCE_VALUE = "measurement_source_value"
    UNIT_SOURCE_VALUE = "unit_source_value"


class SnomedConcepts(Enum):
    """
    Enum for conditions known to this program. The values of the fields are the corresponding snomed ids.
    In all cases the most generic snomed id was chosen as the value
    """
    FEVER = 437663
    FEVER_WITH_CHILLS = 4164645
    FEBRILE_CONVULSIONS = 444413
    CONTINUOUS_FEVER = 4158330
    ERUPTION = 140214  # R.21 Exanthem maps to this
    # B.09 'Nicht näher bezeichnete Virusinfektion, die durch Haut- und Schleimhautläsionen gekennzeichnet ist'
    SKIN_OR_MUCOSA_FINDING_DUE_TO_VIRUS = 4212577
    # B08.0: Sonstige näher bezeichnete Virusinfektionen, die durch Haut- und Schleimhautläsionen gekennzeichnet sind
    SKIN_OR_MUCOSA_FINDING_DUE_TO_OTHER_VIRUSES = 443724
    SWELLING = 443257  # R22
    SWELLING_UPPER_LIMB = 4168701  # R22.3
    SWELLING_LOWER_LIMB = 4171919  # R22.4
    OTHER_CONJUNCTIVITIS = 379019
    MUCOPURULENT_CONJUNCTIVITIS = 376422
    ACUTE_CONJUNCTIVITIS = 376707
    LYMPHADENOPATHY = 315085
    LOCALIZED_ENLARGED_LYMPH_NODES = 4168700
    GENERALIZED_ENLARGED_LYMPH_NODES = 4165998
    DISORDER_OF_ORAL_SOFT_TISSUE = 139057
    DISORDER_OF_LIP = 135858
    LESION_OF_ORAL_MUCOSA = 37016130
    PERICARDITIS = 315293
    MYOCARDITIS = 4331309
    MYOCARDIAL_INFARCTION = 434376
    NAUSEA_AND_VOMITING = 27674
    ASCITES = 200528  # R18
    PLEURAL_EFFUSION = 254061  # J90
    PERICARDIAL_EFFUSION = 4108814  # I31.3
    COVID_19 = 37311061
    COVID_19_VIRUS_NOT_IDENTIFIED = 37311060
    COVID_19_IN_PERSONAL_HISTORY = 37311061
    POST_COVID = 705076
    # Actual PIMS-Id is 703578, but not in our database, this is a replacement
    PIMS = 434821
    KAWASAKI = 314381
    CRP = 3020460
    LAB = 32856
    HIGH = 4328749
    LOW = 4267416
    NORMAL = 4124457
    PTT_BLOOD = 3013466
    PTT_PLASMA = 3018677
    D_DIMER = 3052648
    PT = 3033658
