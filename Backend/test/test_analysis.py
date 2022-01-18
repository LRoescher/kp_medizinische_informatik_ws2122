from unittest import TestCase

from Backend.analysis.analysis import evaluate_patient, evaluate_patients, evaluate_all_in_database
from Backend.common.config import DbConfig
from Backend.common.database import DBManager


class TestAnalysis(TestCase):
    def test_evaluate_patient_without_db_connection(self):
        # Prepare
        # Create DBManager with invalid config and therefore invalid database connection
        invalid: str = "invalid"
        config = DbConfig(db_name=invalid, db_schema=invalid, host="localhost",
                          password=invalid, username=invalid, port="1234")

        db_manager = DBManager(db_config=config, clear_tables=False)

        # Test
        try:
            result = evaluate_patient(db_manager=db_manager, patient_id=1)
            # Assert
            self.assertIsNone(result, "Should return 'None' as a result if the analysis can not be conducted.")
        except Exception:
            # Assert
            self.fail("Should catch all exceptions and not terminate.")

    def test_evaluate_patients_without_db_connection(self):
        # Prepare
        # Create DBManager with invalid config and therefore invalid database connection
        invalid: str = "invalid"
        config = DbConfig(db_name=invalid, db_schema=invalid, host="localhost",
                          password=invalid, username=invalid, port="1234")

        db_manager = DBManager(db_config=config, clear_tables=False)

        # Test
        try:
            result: list = evaluate_patients(db_manager=db_manager, patient_ids=[1000, 1111])
            # Assert
            # S
            self.assertListEqual(result, list(), "Returned list should be empty.")
        except Exception:
            # Assert
            self.fail("Should catch all exceptions and not terminate. Should return an empty list.")

    def test_evaluate_all_in_database_without_db_connection(self):
        # Prepare
        # Create DBManager with invalid config and therefore invalid database connection
        invalid: str = "invalid"
        config = DbConfig(db_name=invalid, db_schema=invalid, host="localhost",
                          password=invalid, username=invalid, port="1234")

        db_manager = DBManager(db_config=config, clear_tables=False)

        # Test
        try:
            result: list = evaluate_all_in_database(db_manager=db_manager)
            # Assert
            self.assertListEqual(result, list(), "Returned list should be empty.")
        except Exception:
            # Assert
            self.fail("Should catch all exceptions and not terminate. Should return an empty list.")

