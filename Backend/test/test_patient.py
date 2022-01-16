import datetime
from unittest import TestCase

from Backend.analysis.patient import Patient
from Backend.common.omop_enums import SnomedConcepts


class TestPatient(TestCase):

    TEST_ID: int = 1
    TEST_NAME: str = "example name"
    TEST_BIRTHDATE: datetime.date = datetime.date.today()
    TEST_CASEDATE: datetime.date = datetime.date.today()

    def test_constructor(self):
        """
        Constructor should initialize a patient with the given parameters and empty lists for conditions, etc.
        """
        # Prepare
        expected_day: int = self.TEST_BIRTHDATE.day
        expected_month: int = self.TEST_BIRTHDATE.month
        expected_year: int = self.TEST_BIRTHDATE.year
        expected_list_len: int = 0
        expected_score: float = 0.0

        # Test
        patient: Patient = Patient(patient_id=self.TEST_ID,
                                   name=self.TEST_NAME,
                                   birthdate=self.TEST_BIRTHDATE,
                                   case_date=self.TEST_CASEDATE)

        # Assert
        # Direct values
        self.assertEqual(self.TEST_ID, patient.id, "Id should be set to given value.")
        self.assertEqual(self.TEST_NAME, patient.name, "Name should be set to given value.")
        self.assertEqual(self.TEST_BIRTHDATE, patient.birthdate, "Birthdate should be set to given value.")
        self.assertEqual(self.TEST_CASEDATE, patient.case_date, "Casedate should be set to given value.")
        # Transitive values
        self.assertEqual(expected_day, patient.day, "Day of birth should be set to the correct value.")
        self.assertEqual(expected_month, patient.month, "Month of birth should be set to the correct value.")
        self.assertEqual(expected_year, patient.year, "Year of birth should be set to the correct value.")
        self.assertEqual(len(patient.conditions), expected_list_len, "There shouldn't be any conditions yet.")
        self.assertEqual(len(patient.high_measurements), expected_list_len, "There shouldn't be any measurements yet.")
        self.assertEqual(len(patient.procedures), expected_list_len, "There shouldn't be any procedures yet.")
        self.assertEqual(len(patient.reasons_for_pims), expected_list_len, "There shouldn't be any reasons yet.")
        self.assertEqual(len(patient.reasons_for_kawasaki), expected_list_len, "There shouldn't be any reasons yet.")
        self.assertEqual(expected_score, patient.pims_score, "Score should be zero at initialization.")
        self.assertEqual(expected_score, patient.kawasaki_score, "Score should be zero at initialization.")

    def test_add_condition(self):
        # Prepare
        patient: Patient = Patient(patient_id=self.TEST_ID,
                                   name=self.TEST_NAME,
                                   birthdate=self.TEST_BIRTHDATE,
                                   case_date=self.TEST_CASEDATE)
        test_condition = 12345
        expected_size = 1

        # Test
        patient.add_condition(test_condition)

        # Assert
        self.assertTrue(test_condition in patient.conditions, "Condition should be added by the method.")
        self.assertEqual(expected_size, len(patient.conditions), "Should not add any other conditions.")

    def test_add_high_measurement(self):
        # Prepare
        patient: Patient = Patient(patient_id=self.TEST_ID,
                                   name=self.TEST_NAME,
                                   birthdate=self.TEST_BIRTHDATE,
                                   case_date=self.TEST_CASEDATE)
        test_measurement = 11111
        expected_size = 1

        # Test
        patient.add_high_measurement(test_measurement)

        # Assert
        self.assertTrue(test_measurement in patient.high_measurements, "Measurement should be added by the method.")
        self.assertEqual(expected_size, len(patient.high_measurements), "Should not add any other measurements.")

    def test_add_procedure(self):
        # Prepare
        patient: Patient = Patient(patient_id=self.TEST_ID,
                                   name=self.TEST_NAME,
                                   birthdate=self.TEST_BIRTHDATE,
                                   case_date=self.TEST_CASEDATE)
        test_procedure = 222222
        expected_size = 1

        # Test
        patient.add_procedure(test_procedure)

        # Assert
        self.assertTrue(test_procedure in patient.procedures, "Procedure should be added by the method.")
        self.assertEqual(expected_size, len(patient.procedures), "Should not add any other procedures.")

    def test_calculate_age(self):
        # Prepare
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")
        date_ten = datetime.date.fromisoformat("2009-02-03")
        date_hundred = datetime.date.fromisoformat("1920-02-02")
        date_minus = datetime.date.fromisoformat("2030-01-01")
        expected_age_one = 1
        expected_age_ten = 10
        expected_age_hundred = 100
        expected_age_minus = -10

        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient10: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_ten, case_date=case_date)
        patient100: Patient = Patient(3, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        patient_minus_one: Patient = Patient(4, name=self.TEST_NAME, birthdate=date_minus, case_date=case_date)

        # Test
        actual_age_one = patient1.calculate_age()
        actual_age_ten = patient10.calculate_age()
        actual_age_hundred = patient100.calculate_age()
        actual_age_minus = patient_minus_one.calculate_age()

        # Assert
        self.assertEqual(expected_age_one, actual_age_one, "Age should be calculated correctly")
        self.assertEqual(expected_age_ten, actual_age_ten, "Age should be calculated correctly")
        self.assertEqual(expected_age_hundred, actual_age_hundred, "Age should be calculated correctly")
        self.assertEqual(expected_age_minus, actual_age_minus, "Age should be calculated correctly, even if invalid.")

    def test_has_fever(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.FEVER.value)

        # Test/Assert
        self.assertTrue(patient1.has_fever(), "Should resolve to true, if the patient has a fever condition.")
        self.assertFalse(patient2.has_fever(), "Should resolve to false, if the patient has no fever condition.")

    def test_has_exanthem(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.ERUPTION.value)

        # Test/Assert
        self.assertTrue(patient1.has_exanthem(), "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_exanthem(), "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_swollen_extremities(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)

        # Test/Assert
        self.assertTrue(patient1.has_swollen_extremities(), "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_swollen_extremities(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_conjunctivitis(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)

        # Test/Assert
        self.assertTrue(patient1.has_conjunctivitis(), "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_conjunctivitis(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_lymphadenopathy(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)

        # Test/Assert
        self.assertTrue(patient1.has_lymphadenopathy(), "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_lymphadenopathy(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_mouth_or_mucosa_inflammation(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)

        # Test/Assert
        self.assertTrue(patient1.has_mouth_or_mucosa_inflammation(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_mouth_or_mucosa_inflammation(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_cardiac_condition(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.PERICARDITIS.value)

        # Test/Assert
        self.assertTrue(patient1.has_cardiac_condition(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_cardiac_condition(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_gastro_intestinal_condition(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)

        # Test/Assert
        self.assertTrue(patient1.has_gastro_intestinal_condition(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_gastro_intestinal_condition(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_inflammation_lab(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        # Add high CRP (LOINC 3020460)
        patient1.add_high_measurement(3020460)

        # Test/Assert
        self.assertTrue(patient1.has_inflammation_lab(),
                        "Should resolve to true, if the patient has a high inflammation parameter.")
        self.assertFalse(patient2.has_inflammation_lab(),
                         "Should resolve to false, if the patient hasn't got a high inflammation parameter")

    def test_has_effusion(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.PLEURAL_EFFUSION.value)

        # Test/Assert
        self.assertTrue(patient1.has_effusion(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_effusion(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_covid(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.COVID_19.value)

        # Test/Assert
        self.assertTrue(patient1.has_covid(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_covid(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_kawasaki(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.KAWASAKI.value)

        # Test/Assert
        self.assertTrue(patient1.has_kawasaki(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_kawasaki(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_calculate_kawasaki_score(self):
        # Prepare
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")
        date_hundred = datetime.date.fromisoformat("1920-02-02")
        # Patient with no conditions and correct age
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patient with one major condition and correct age
        patient1b: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patient with all (major) conditions and correct age
        patient1c: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patient with all possible conditions and correct age
        patient1d: Patient = Patient(5, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patients with same conditions as above, but incorrect age
        patient2: Patient = Patient(3, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        patient2b: Patient = Patient(4, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        patient2c: Patient = Patient(4, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)

        patient1b.add_condition(SnomedConcepts.FEVER.value)
        patient2b.add_condition(SnomedConcepts.FEVER.value)

        patient1c.add_condition(SnomedConcepts.FEVER.value)
        patient1c.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient1c.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient1c.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient1c.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient1c.add_condition(SnomedConcepts.ERUPTION.value)
        patient2c.add_condition(SnomedConcepts.FEVER.value)
        patient2c.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient2c.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient2c.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient2c.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient2c.add_condition(SnomedConcepts.ERUPTION.value)

        patient1d.add_condition(SnomedConcepts.COVID_19.value)
        patient1d.add_condition(SnomedConcepts.FEVER.value)
        patient1d.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient1d.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient1d.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient1d.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient1d.add_condition(SnomedConcepts.ERUPTION.value)
        patient1d.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient1d.add_condition(SnomedConcepts.PLEURAL_EFFUSION.value)
        patient1d.add_condition(SnomedConcepts.KAWASAKI.value)
        patient1d.add_high_measurement(3020460)  # Add high CRP (LOINC 3020460)

        # Asserts
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.0)
        self.assertEqual(0.0, patient2.calculate_kawasaki_score(), 0.0)
        self.assertEqual(0.0, patient2b.calculate_kawasaki_score(), 0.0)
        self.assertEqual(0.0, patient2c.calculate_kawasaki_score(), 0.0)
        # Score should be greater than 0.0 with a symptom and correct age
        self.assertGreater(patient1b.calculate_kawasaki_score(), 0.0)
        # Score should be 1.0 with all major symptoms
        self.assertEqual(1.0, patient1c.calculate_kawasaki_score())
        # Score should be 1.0 with all symptoms and not higher
        self.assertLessEqual(patient1d.calculate_kawasaki_score(), 1.0)

    def test_calculate_pims_score(self):
        # Prepare
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")
        date_hundred = datetime.date.fromisoformat("1920-02-02")
        # Patient with no conditions and correct age
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patient with one major condition and correct age and covid
        patient1b: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patient with all (major) conditions and correct age
        patient1c: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patient with all conditions that get evaluated
        patient1d: Patient = Patient(5, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patients with same conditions as above, but incorrect age
        patient2: Patient = Patient(3, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        patient2b: Patient = Patient(4, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        patient2c: Patient = Patient(4, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)

        patient1b.add_condition(SnomedConcepts.FEVER.value)
        patient1b.add_condition(SnomedConcepts.COVID_19.value)
        patient2b.add_condition(SnomedConcepts.FEVER.value)
        patient2b.add_condition(SnomedConcepts.COVID_19.value)

        patient1c.add_condition(SnomedConcepts.COVID_19.value)
        patient1c.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)
        patient1c.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient1c.add_condition(SnomedConcepts.PLEURAL_EFFUSION.value)
        patient1c.add_condition(SnomedConcepts.FEVER.value)
        patient1c.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient1c.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient1c.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient1c.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient1c.add_condition(SnomedConcepts.ERUPTION.value)
        patient2c.add_condition(SnomedConcepts.COVID_19.value)
        patient2c.add_condition(SnomedConcepts.FEVER.value)
        patient2c.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient2c.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient2c.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient2c.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient2c.add_condition(SnomedConcepts.ERUPTION.value)
        patient2c.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient2c.add_condition(SnomedConcepts.PLEURAL_EFFUSION.value)

        patient1d.add_condition(SnomedConcepts.COVID_19.value)
        patient1d.add_condition(SnomedConcepts.FEVER.value)
        patient1d.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient1d.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient1d.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient1d.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient1d.add_condition(SnomedConcepts.ERUPTION.value)
        patient1d.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient1d.add_condition(SnomedConcepts.PLEURAL_EFFUSION.value)
        patient1d.add_condition(SnomedConcepts.KAWASAKI.value)
        patient1d.add_high_measurement(3020460)  # Add high CRP (LOINC 3020460)

        # Asserts
        self.assertEqual(patient1.calculate_pims_score(), 0.0)
        self.assertEqual(0.0, patient2.calculate_pims_score(), 0.0)
        self.assertEqual(0.0, patient2b.calculate_pims_score(), 0.0)
        self.assertEqual(0.0, patient2c.calculate_pims_score(), 0.0)
        # Score should be greater than 0.0 with a symptom and correct age
        self.assertGreater(patient1b.calculate_pims_score(), 0.0)
        # Score should be 1.0 with all major symptoms
        self.assertEqual(1.0, patient1c.calculate_pims_score())
        # Score should be 1.0 with all symptoms and not higher
        self.assertLessEqual(patient1d.calculate_pims_score(), 1.0)

    def test_has_ascites(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.ASCITES.value)

        # Test/Assert
        self.assertTrue(patient1.has_ascites(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_ascites(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_pericardial_effusions(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.PERICARDIAL_EFFUSION.value)

        # Test/Assert
        self.assertTrue(patient1.has_pericardial_effusions(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_pericardial_effusions(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_pleural_effusions(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.PLEURAL_EFFUSION.value)

        # Test/Assert
        self.assertTrue(patient1.has_pleural_effusions(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_pleural_effusions(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_pericarditis(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.PERICARDITIS.value)

        # Test/Assert
        self.assertTrue(patient1.has_pericarditis(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_pericarditis(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_has_myocarditis(self):
        # Prepare
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)
        patient2: Patient = Patient(2, name=self.TEST_NAME, birthdate=self.TEST_BIRTHDATE, case_date=self.TEST_CASEDATE)

        patient1.add_condition(SnomedConcepts.MYOCARDITIS.value)

        # Test/Assert
        self.assertTrue(patient1.has_myocarditis(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_myocarditis(),
                         "Should resolve to false, if the patient hasn't got the condition.")

    def test_to_string(self):
        # Prepare
        case_date = datetime.date.fromisoformat("2020-02-02")
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=case_date, case_date=case_date)
        expected_string = f"1: 2-2-2020, Kawsawki: 0.0, Pims: 0.0"

        # Test
        actual_string = str(patient)

        # Assert
        self.assertEqual(expected_string, actual_string, "To String should format correct data.")
