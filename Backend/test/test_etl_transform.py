import datetime
from unittest import TestCase

import pandas as pd

from Backend.common.omop_enums import OmopProviderFieldsEnum, OmopPersonFieldsEnum
from Backend.etl.csv_enums import CaseColumnsEnum, PersonColumnsEnum
from Backend.etl.transform import *


class TestEtlTransform(TestCase):
    date_one = datetime.date.fromisoformat("2020-02-02")
    date_two = datetime.date.fromisoformat("2019-01-03")
    date_three = datetime.date.fromisoformat("2012-07-08")
    date_four = datetime.date.fromisoformat("2002-05-11")

    def test_generate_provider_table_valid(self):
        # Prepare
        person_data = {
            PersonColumnsEnum.PROVIDER_ID.value: [1],
            PersonColumnsEnum.ID.value: [1],
            PersonColumnsEnum.NAME.value: ["A"],
            PersonColumnsEnum.FORENAME.value: ["B"],
            PersonColumnsEnum.GENDER.value: ["w"],
            PersonColumnsEnum.BIRTHDATE.value: [TestEtlTransform.date_one],
            PersonColumnsEnum.CITY.value: ["C"],
            PersonColumnsEnum.ZIP.value: [12345],
            PersonColumnsEnum.DEATH.value: ["nein"],
            PersonColumnsEnum.DEATH_DATE: [self.date_one],
            PersonColumnsEnum.DATE_OF_LIFE: [self.date_one],
            PersonColumnsEnum.INSURANCE: ["A"],
            PersonColumnsEnum.INSURANCE_ID: ["A"]
        }
        person_df: pd.DataFrame = pd.DataFrame(person_data)
        case_data = {
            CaseColumnsEnum.ID.value: [1, 2],
            CaseColumnsEnum.PROVIDER_ID.value: [1, 0],
            CaseColumnsEnum.PATIENT_ID.value: [1, 2],
            CaseColumnsEnum.START.value: [self.date_one, self.date_two],
            CaseColumnsEnum.END.value: [self.date_one, self.date_two]
        }
        case_df: pd.DataFrame = pd.DataFrame(case_data)
        expected_ids = [0, 1]
        expected_cols = [OmopProviderFieldsEnum.PROVIDER_ID.value]
        # Test
        result: pd.DataFrame = generate_provider_table(person_df, case_df)

        # Assert
        self.assertTrue(OmopProviderFieldsEnum.PROVIDER_ID.value in result.columns)
        self.assertEqual(len(result.columns), len(expected_cols))
        self.assertEqual(len(result.index), len(expected_ids))
        for expected_id in expected_ids:
            self.assertTrue(expected_id in result[OmopProviderFieldsEnum.PROVIDER_ID.value])

    def test_generate_provider_table_invalid_person(self):
        # Test with None value as Provider Id for the Person Table
        # Prepare
        person_data = {
            PersonColumnsEnum.PROVIDER_ID.value: [None],
            PersonColumnsEnum.ID.value: [1],
            PersonColumnsEnum.NAME.value: ["A"],
            PersonColumnsEnum.FORENAME.value: ["B"],
            PersonColumnsEnum.GENDER.value: ["w"],
            PersonColumnsEnum.BIRTHDATE.value: [TestEtlTransform.date_one],
            PersonColumnsEnum.CITY.value: ["C"],
            PersonColumnsEnum.ZIP.value: [12345],
            PersonColumnsEnum.DEATH.value: ["nein"],
            PersonColumnsEnum.DEATH_DATE: [self.date_one],
            PersonColumnsEnum.DATE_OF_LIFE: [self.date_one],
            PersonColumnsEnum.INSURANCE: ["A"],
            PersonColumnsEnum.INSURANCE_ID: ["A"]
        }
        person_df: pd.DataFrame = pd.DataFrame(person_data)
        case_data = {
            CaseColumnsEnum.ID.value: [1, 2],
            CaseColumnsEnum.PROVIDER_ID.value: [1, 0],
            CaseColumnsEnum.PATIENT_ID.value: [1, 2],
            CaseColumnsEnum.START.value: [self.date_one, self.date_two],
            CaseColumnsEnum.END.value: [self.date_one, self.date_two]
        }
        case_df: pd.DataFrame = pd.DataFrame(case_data)
        expected_ids = [0, 1]
        expected_cols = [OmopProviderFieldsEnum.PROVIDER_ID.value]
        # Test
        result: pd.DataFrame = generate_provider_table(person_df, case_df)

        # Assert
        self.assertTrue(OmopProviderFieldsEnum.PROVIDER_ID.value in result.columns)
        self.assertEqual(len(result.columns), len(expected_cols))
        self.assertEqual(len(result.index), len(expected_ids))
        for expected_id in expected_ids:
            self.assertTrue(expected_id in result[OmopProviderFieldsEnum.PROVIDER_ID.value])

    def test_generate_provider_table_invalid_case(self):
        # Test with None value as Provider Id for the CaseTable
        # Prepare
        person_data = {
            PersonColumnsEnum.PROVIDER_ID.value: [None],
            PersonColumnsEnum.ID.value: [1],
            PersonColumnsEnum.NAME.value: ["A"],
            PersonColumnsEnum.FORENAME.value: ["B"],
            PersonColumnsEnum.GENDER.value: ["w"],
            PersonColumnsEnum.BIRTHDATE.value: [TestEtlTransform.date_one],
            PersonColumnsEnum.CITY.value: ["C"],
            PersonColumnsEnum.ZIP.value: [12345],
            PersonColumnsEnum.DEATH.value: ["nein"],
            PersonColumnsEnum.DEATH_DATE: [self.date_one],
            PersonColumnsEnum.DATE_OF_LIFE: [self.date_one],
            PersonColumnsEnum.INSURANCE: ["A"],
            PersonColumnsEnum.INSURANCE_ID: ["A"]
        }
        person_df: pd.DataFrame = pd.DataFrame(person_data)
        case_data = {
            CaseColumnsEnum.ID.value: [1, 2],
            CaseColumnsEnum.PROVIDER_ID.value: [1, 0],
            CaseColumnsEnum.PATIENT_ID.value: [1, 2],
            CaseColumnsEnum.START.value: [self.date_one, self.date_two],
            CaseColumnsEnum.END.value: [self.date_one, self.date_two]
        }
        case_df: pd.DataFrame = pd.DataFrame(case_data)
        expected_ids = [0, 1]
        expected_cols = [OmopProviderFieldsEnum.PROVIDER_ID.value]
        # Test
        result: pd.DataFrame = generate_provider_table(person_df, case_df)

        # Assert
        self.assertTrue(OmopProviderFieldsEnum.PROVIDER_ID.value in result.columns)
        self.assertEqual(len(result.columns), len(expected_cols))
        self.assertEqual(len(result.index), len(expected_ids))
        for expected_id in expected_ids:
            self.assertTrue(expected_id in result[OmopProviderFieldsEnum.PROVIDER_ID.value])

    def test_generate_location_table_valid(self):
        # Prepare
        person_data = {
            PersonColumnsEnum.PROVIDER_ID.value: [1],
            PersonColumnsEnum.ID.value: [1],
            PersonColumnsEnum.NAME.value: ["A"],
            PersonColumnsEnum.FORENAME.value: ["B"],
            PersonColumnsEnum.GENDER.value: ["w"],
            PersonColumnsEnum.BIRTHDATE.value: [TestEtlTransform.date_one],
            PersonColumnsEnum.CITY.value: ["C"],
            PersonColumnsEnum.ZIP.value: [12345],
            PersonColumnsEnum.DEATH.value: ["nein"],
            PersonColumnsEnum.DEATH_DATE: [self.date_one],
            PersonColumnsEnum.DATE_OF_LIFE: [self.date_one],
            PersonColumnsEnum.INSURANCE: ["A"],
            PersonColumnsEnum.INSURANCE_ID: ["A"]
        }
        person_df: pd.DataFrame = pd.DataFrame(person_data)
        expected_id = 1
        expected_zip = 12345
        expected_city = "C"
        expected_cols = ['location_id', 'city', 'zip']

        # Test
        result: pd.DataFrame = generate_location_table(person_df)

        # Assert
        print(result)
        for col in expected_cols:
            self.assertTrue(col in result.columns)
        self.assertEqual(len(result.columns), len(expected_cols))
        self.assertTrue(expected_id in result["location_id"].values)
        self.assertTrue(expected_city in result['city'].values)
        self.assertTrue(expected_zip in result['zip'].values)

    def test_generate_person_table_valid(self):
        # Prepare
        person_data = {
            PersonColumnsEnum.PROVIDER_ID.value: [1],
            PersonColumnsEnum.ID.value: [1],
            PersonColumnsEnum.NAME.value: ["A"],
            PersonColumnsEnum.FORENAME.value: ["B"],
            PersonColumnsEnum.GENDER.value: ["w"],
            PersonColumnsEnum.BIRTHDATE.value: [TestEtlTransform.date_one],
            PersonColumnsEnum.CITY.value: ["C"],
            PersonColumnsEnum.ZIP.value: [12345],
            PersonColumnsEnum.DEATH.value: ["nein"],
            PersonColumnsEnum.DEATH_DATE: [self.date_one],
            PersonColumnsEnum.DATE_OF_LIFE: [self.date_one],
            PersonColumnsEnum.INSURANCE: ["A"],
            PersonColumnsEnum.INSURANCE_ID: ["A"]
        }
        person_df: pd.DataFrame = pd.DataFrame(person_data)
        # Test
        result: pd.DataFrame = generate_person_table(person_df)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result.index),  1)
