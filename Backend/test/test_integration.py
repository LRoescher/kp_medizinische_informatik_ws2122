import datetime
import os
from unittest import TestCase

from Backend.backend_interface import BackendManager
from Backend.interface import Interface, PatientData, PatientId, Disease
from config.definitions import ROOT_DIR


class TestIntegration(TestCase):
    """
    Tests that cover the whole system.
    WARNING: Tests can empty the database.
    """

    # Default folder for the csv files
    upload_folder = os.path.join(ROOT_DIR, "upload")

    def test_round_trip_valid(self):
        """
        Tests a round trip of backend functions with valid parameters. A valid config file is needed.
        This tests performs long running database operations and may take some time to perform.
        """
        # Init BackendManager
        backend_manager: Interface = BackendManager()
        # Reset database to have same starting conditions
        reset_successful: bool = backend_manager.reset_db()

        # Test database reset
        self.assertTrue(reset_successful, "Reset should return true if successful.")
        self.assertTrue(backend_manager.is_db_empty(), "Should return true after database reset.")
        # (analyzed) patient list should be empty after database reset
        patients = backend_manager.analysis_data
        self.assertEqual(len(patients), 0)

        # Run ETL Job
        result = backend_manager.run_etl(self.upload_folder)
        self.assertTrue(result, "Should return true if successful.")
        patients = backend_manager.analysis_data
        self.assertEqual(len(patients), 0, "Patient list should still be empty, after etl job.")

        # Run analysis
        result = backend_manager.run_analysis()
        self.assertTrue(result, "Should return true if successful.")
        patients = backend_manager.analysis_data
        self.assertNotEqual(len(patients), 0, "Patient list should not be empty after analysis and etl job.")

        # Get first patient to get valid id
        first_patient_id: int = list(patients.keys())[0]
        patient = backend_manager.get_patient_data(PatientId(first_patient_id))
        # Check valid patient data
        self.assertIsNotNone(patient['name'])

        # Get according decision reason
        decision_reason = backend_manager.get_decision_reason(PatientId(first_patient_id), Disease.KAWASAKI)
        # Check valid decision reason data
        self.assertIsNotNone(decision_reason['probability'])
        self.assertTrue(0.0 <= decision_reason['probability'] <= 1.0)

        # Adding a new patient
        birthday = datetime.date.today()
        patient_data: PatientData = {
            'name': "Alfred Beispiel",
            'birthdate': birthday,
            'hasCovid': True,
            'hasFever': False,
            'hasExanthem': False,
            'hasEnanthem': False,
            'hasSwollenExtremeties': False,
            'hasConjunctivitis': False,
            'hasSwollenLymphnodes': False,
            'hasGastroIntestinalCondition': False,
            'hasPericardialEffusions': False,
            'hasPericarditis': False,
            'hasMyocarditis': False,
            'hasInflammationLab': False,
            'hasKawasaki': False,
            'hasCoagulopathy': False
        }
        result_id = backend_manager.add_patient(patient_data)

        self.assertIsNotNone(result_id, "Valid data should add the patient")

        # Check if there is data for the just created patient
        patient = backend_manager.get_patient_data(PatientId(result_id))
        # Check valid patient data
        self.assertIsNotNone(patient['name'])

        # Get according decision reason
        decision_reason = backend_manager.get_decision_reason(PatientId(result_id), Disease.KAWASAKI)
        # Check decision reason
        self.assertIsNotNone(decision_reason['probability'])
        self.assertTrue(decision_reason['probability'] == 0.0)

        # Check if fields are correctly set.
        self.assertEqual(patient['name'], 'Alfred Beispiel')
        self.assertEqual(patient['birthdate'], birthday)
        self.assertTrue(patient['hasCovid'])
        self.assertFalse(patient['hasFever'])
        self.assertFalse(patient['hasEnanthem'])
        self.assertFalse(patient['hasPericarditis'])
        self.assertFalse(patient['hasExanthem'])
        self.assertFalse(patient['hasKawasaki'])
        self.assertFalse(patient['hasSwollenExtremeties'])
        self.assertFalse(patient['hasSwollenLymphnodes'])
        self.assertFalse(patient['hasMyocarditis'])
        self.assertFalse(patient['hasPericardialEffusions'])
        self.assertFalse(patient['hasConjunctivitis'])
        self.assertFalse(patient['hasInflammationLab'])
        self.assertFalse(patient['hasGastroIntestinalCondition'])
        self.assertFalse(patient['hasCoagulopathy'])

        # Updating patient
        new_birthdate = datetime.date.fromisoformat("2010-01-01")
        update_data: PatientData = {
            'name': "Alfred Beispiel2",
            'birthdate': new_birthdate,
            'hasCovid': False,
            'hasFever': True,
            'hasExanthem': True,
            'hasEnanthem': True,
            'hasSwollenExtremeties': True,
            'hasConjunctivitis': True,
            'hasSwollenLymphnodes': True,
            'hasGastroIntestinalCondition': True,
            'hasPericardialEffusions': True,
            'hasPericarditis': True,
            'hasMyocarditis': True,
            'hasInflammationLab': True,
            'hasKawasaki': True,
            'hasCoagulopathy': True
        }
        result = backend_manager.update_patient(result_id, update_data)

        self.assertTrue(result, "Should return true if the update was successful.")

        # Check if there is data for the just updated patient
        patient = backend_manager.get_patient_data(PatientId(result_id))
        # Check valid patient data
        self.assertIsNotNone(patient['name'])

        # Get according decision reason
        decision_reason = backend_manager.get_decision_reason(PatientId(result_id), Disease.PIMS)
        decision_reason2 = backend_manager.get_decision_reason(PatientId(result_id), Disease.KAWASAKI)
        # Check decision reason
        self.assertIsNotNone(decision_reason['probability'])
        self.assertEqual(decision_reason['probability'], 0.75)
        self.assertIsNotNone(decision_reason2['probability'])
        self.assertEqual(decision_reason2['probability'], 1.0)

        # Check if fields are correctly updated
        self.assertEqual(patient['name'], 'Alfred Beispiel2')
        self.assertEqual(patient['birthdate'], new_birthdate)
        self.assertFalse(patient['hasCovid'])
        self.assertTrue(patient['hasFever'])
        self.assertTrue(patient['hasEnanthem'])
        self.assertTrue(patient['hasPericarditis'])
        self.assertTrue(patient['hasExanthem'])
        self.assertTrue(patient['hasKawasaki'])
        self.assertTrue(patient['hasSwollenExtremeties'])
        self.assertTrue(patient['hasSwollenLymphnodes'])
        self.assertTrue(patient['hasMyocarditis'])
        self.assertTrue(patient['hasPericardialEffusions'])
        self.assertTrue(patient['hasConjunctivitis'])
        self.assertTrue(patient['hasInflammationLab'])
        self.assertTrue(patient['hasGastroIntestinalCondition'])
        self.assertTrue(patient['hasCoagulopathy'])

        # Test with full PIMS score
        update_data: PatientData = {
            'name': "Alfred Beispiel2",
            'birthdate': new_birthdate,
            'hasCovid': True,
            'hasFever': True,
            'hasExanthem': True,
            'hasEnanthem': True,
            'hasSwollenExtremeties': True,
            'hasConjunctivitis': True,
            'hasSwollenLymphnodes': True,
            'hasGastroIntestinalCondition': True,
            'hasPericardialEffusions': True,
            'hasPericarditis': True,
            'hasMyocarditis': True,
            'hasInflammationLab': True,
            'hasKawasaki': True,
            'hasCoagulopathy': False
        }
        result = backend_manager.update_patient(result_id, update_data)
        self.assertTrue(result, "Should return true if the update was successful.")

        # Get according decision reason
        patient = backend_manager.get_patient_data(PatientId(result_id))
        decision_reason = backend_manager.get_decision_reason(PatientId(result_id), Disease.PIMS)
        # Check decision reason
        self.assertEqual(decision_reason['probability'], 1.0)
        self.assertFalse(patient['hasCoagulopathy'])

        # Reset db to keep database consistent.
        self.assertTrue(backend_manager.reset_db())
