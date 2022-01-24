import datetime
from unittest import TestCase

import pandas as pd

from Backend.common.omop_enums import OmopProviderFieldsEnum
from Backend.etl.csv_enums import CaseColumnsEnum, PersonColumnsEnum
from Backend.etl.transform import *


class TestEtlTransform(TestCase):

    def __init__(self):
        super().__init__()
        self.date_one = datetime.date.fromisoformat("2020-02-02")
        self.date_two = datetime.date.fromisoformat("2019-01-03")
        self.date_three = datetime.date.fromisoformat("2012-07-08")
        self.date_four = datetime.date.fromisoformat("2002-05-11")
        person_data = {
            PersonColumnsEnum.PROVIDER_ID.value: [1, 2, "123", None, 4],
            PersonColumnsEnum.ID.value: [1, 2, -3, None, 4],
            PersonColumnsEnum.NAME.value: ["A", "", 12, None, "c"],
            PersonColumnsEnum.FORENAME.value: ["B", "", 3, None, "c"],
            PersonColumnsEnum.GENDER.value: ["w", "m", "x", None, 3],
            PersonColumnsEnum.BIRTHDATE.value: [self.date_one, self.date_two, self.date_three, self.date_four, None],
            PersonColumnsEnum.CITY.value: ["a", None, 3, "b", "c"],
            PersonColumnsEnum.ZIP.value: [12345, "111111", None, True, ""],
            PersonColumnsEnum.DEATH.value: [False, False, True, None, 12],
            PersonColumnsEnum.DEATH_DATE: [self.date_one, self.date_two, self.date_one, self.date_four, self.date_one],
            PersonColumnsEnum.DATE_OF_LIFE: [self.date_one, self.date_two, self.date_one, self.date_one, self.date_one],
            PersonColumnsEnum.INSURANCE: ["A", "B", "C", "D", "E"],
            PersonColumnsEnum.INSURANCE_ID: ["A", "B", "C", "D", "E"]
        }
        self.person_df: pd.DataFrame = pd.DataFrame(person_data)
        case_data = {
            CaseColumnsEnum.ID.value: [1, 2, 3, 4],
            CaseColumnsEnum.PROVIDER_ID.value: [1, 0, "123", None],
            CaseColumnsEnum.PATIENT_ID.value: [1, 2, 3, 4],
            CaseColumnsEnum.START.value: [self.date_one, self.date_two, self.date_three, self.date_four],
            CaseColumnsEnum.END.value: [self.date_two, self.date_three, self.date_four, self.date_one]
        }
        self.case_df: pd.DataFrame = pd.DataFrame(case_data)

    def test_generate_provider_table(self):
        # Prepare
        expected_ids = [1, 0, 2, 4]
        expected_cols = [OmopProviderFieldsEnum.PROVIDER_ID]
        # Test
        result = generate_provider_table(self.person_df, self.case_df)

        # Assert
        # correct cols
        # no errors
        # correct ids
        # correct length