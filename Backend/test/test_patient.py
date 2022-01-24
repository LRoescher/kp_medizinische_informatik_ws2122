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
        self.assertTrue(patient1.has_enanthem(),
                        "Should resolve to true, if the patient has the condition.")
        self.assertFalse(patient2.has_enanthem(),
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

    def test_calculate_kawasaki_score_complete_kawasaki(self):
        # Prepare
        # Set correct age
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient2: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient3: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient4: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient5: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient6: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)

        # Add fever to all
        patient1.add_condition(SnomedConcepts.FEVER.value)
        patient2.add_condition(SnomedConcepts.FEVER.value)
        patient3.add_condition(SnomedConcepts.FEVER.value)
        patient4.add_condition(SnomedConcepts.FEVER.value)
        patient5.add_condition(SnomedConcepts.FEVER.value)
        patient6.add_condition(SnomedConcepts.FEVER.value)

        # Add all other conditions for patient1
        patient1.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient1.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient1.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient1.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient1.add_condition(SnomedConcepts.ERUPTION.value)

        # Add all other conditions but enanthem for patient2
        patient2.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient2.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient2.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient2.add_condition(SnomedConcepts.ERUPTION.value)

        # Add all other conditions but conjunctivitis for patient3
        patient3.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient3.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient3.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient3.add_condition(SnomedConcepts.ERUPTION.value)

        # Add all other conditions but lymphadenopathy for patient4
        patient4.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient4.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient4.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient4.add_condition(SnomedConcepts.ERUPTION.value)

        # Add all other conditions but swelling for patient5
        patient5.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient5.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient5.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient5.add_condition(SnomedConcepts.ERUPTION.value)

        # Add all other conditions but exanthem for patient6
        patient6.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient6.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient6.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient6.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)

        self.assertEqual(patient1.calculate_kawasaki_score(), 1.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 7)
        self.assertEqual(len(patient1.missing_for_kawasaki), 0)

        self.assertEqual(patient2.calculate_kawasaki_score(), 1.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 6)
        self.assertTrue(Patient.REASON_ENANTHEM in patient2.missing_for_kawasaki)
        self.assertEqual(len(patient2.missing_for_kawasaki), 1)

        self.assertEqual(patient3.calculate_kawasaki_score(), 1.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 6)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient3.missing_for_kawasaki)
        self.assertEqual(len(patient3.missing_for_kawasaki), 1)

        self.assertEqual(patient4.calculate_kawasaki_score(), 1.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 6)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient4.missing_for_kawasaki)
        self.assertEqual(len(patient4.missing_for_kawasaki), 1)

        self.assertEqual(patient5.calculate_kawasaki_score(), 1.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient5.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 6)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient5.missing_for_kawasaki)
        self.assertEqual(len(patient5.missing_for_kawasaki), 1)

        self.assertEqual(patient6.calculate_kawasaki_score(), 1.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient6.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient6.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient6.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient6.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient6.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient6.reasons_for_kawasaki)
        self.assertEqual(len(patient6.reasons_for_kawasaki), 6)
        self.assertTrue(Patient.REASON_EXANTHEM in patient6.missing_for_kawasaki)
        self.assertEqual(len(patient6.missing_for_kawasaki), 1)

    def test_calculate_kawasaki_score_incomplete_kawasaki(self):
        # Prepare
        # Set correct age
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient2: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient3: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient4: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient5: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)

        # Add fever to all
        patient1.add_condition(SnomedConcepts.FEVER.value)
        patient2.add_condition(SnomedConcepts.FEVER.value)
        patient3.add_condition(SnomedConcepts.FEVER.value)
        patient4.add_condition(SnomedConcepts.FEVER.value)
        patient5.add_condition(SnomedConcepts.FEVER.value)

        # Add one condition per patient
        patient1.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient2.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient3.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient4.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient5.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts with one extra condition
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient1.missing_for_kawasaki), 4)

        self.assertEqual(patient2.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient2.missing_for_kawasaki), 4)

        self.assertEqual(patient3.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient3.missing_for_kawasaki), 4)

        self.assertEqual(patient4.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient4.missing_for_kawasaki), 4)

        self.assertEqual(patient5.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient5.missing_for_kawasaki), 4)

        # Add another condition per patient and repeat
        patient5.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient1.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient2.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient3.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient4.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts with two extra conditions
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient1.missing_for_kawasaki), 3)

        self.assertEqual(patient2.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient2.missing_for_kawasaki), 3)

        self.assertEqual(patient3.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient3.missing_for_kawasaki), 3)

        self.assertEqual(patient4.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient4.missing_for_kawasaki), 3)

        self.assertEqual(patient5.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient5.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient5.missing_for_kawasaki), 3)

        # Add another condition per patient and repeat
        patient4.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient5.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient1.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient2.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient3.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts with two extra conditions
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient1.missing_for_kawasaki), 2)

        self.assertEqual(patient2.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient2.missing_for_kawasaki), 2)

        self.assertEqual(patient3.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient3.missing_for_kawasaki), 2)

        self.assertEqual(patient4.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient4.missing_for_kawasaki), 2)

        self.assertEqual(patient5.calculate_kawasaki_score(), 0.75)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient5.missing_for_kawasaki), 2)

    def test_calculate_kawasaki_score_possibly_kawasaki(self):
        # Prepare
        # Set correct age
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")
        patient0: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient2: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient3: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient4: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient5: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)

        # Add one condition per patient
        patient0.add_condition(SnomedConcepts.FEVER.value)
        patient1.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient2.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient3.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient4.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient5.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts with one condition
        self.assertEqual(patient0.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient0.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient0.reasons_for_kawasaki)
        self.assertEqual(len(patient0.reasons_for_kawasaki), 2)
        self.assertEqual(len(patient0.missing_for_kawasaki), 5)

        self.assertEqual(patient1.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 2)
        self.assertEqual(len(patient1.missing_for_kawasaki), 5)

        self.assertEqual(patient2.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 2)
        self.assertEqual(len(patient2.missing_for_kawasaki), 5)

        self.assertEqual(patient3.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 2)
        self.assertEqual(len(patient3.missing_for_kawasaki), 5)

        self.assertEqual(patient4.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 2)
        self.assertEqual(len(patient4.missing_for_kawasaki), 5)

        self.assertEqual(patient5.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 2)
        self.assertEqual(len(patient5.missing_for_kawasaki), 5)

        # Add another condition per patient and repeat
        patient5.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient1.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient2.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient3.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient4.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts with two extra conditions
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient1.missing_for_kawasaki), 4)

        self.assertEqual(patient2.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient2.missing_for_kawasaki), 4)

        self.assertEqual(patient3.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient3.missing_for_kawasaki), 4)

        self.assertEqual(patient4.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient4.missing_for_kawasaki), 4)

        self.assertEqual(patient5.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient5.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 3)
        self.assertEqual(len(patient5.missing_for_kawasaki), 4)

        # Add another condition per patient and repeat
        patient4.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient5.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient1.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient2.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient3.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts with three extra conditions
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient1.missing_for_kawasaki), 3)

        self.assertEqual(patient2.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient2.missing_for_kawasaki), 3)

        self.assertEqual(patient3.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient3.missing_for_kawasaki), 3)

        self.assertEqual(patient4.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient4.missing_for_kawasaki), 3)

        self.assertEqual(patient5.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient5.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 4)
        self.assertEqual(len(patient5.missing_for_kawasaki), 3)

        # Add another condition per patient and repeat
        patient3.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient4.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient5.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient1.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient2.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts with four extra conditions
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient1.missing_for_kawasaki), 2)

        self.assertEqual(patient2.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient2.missing_for_kawasaki), 2)

        self.assertEqual(patient3.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient3.missing_for_kawasaki), 2)

        self.assertEqual(patient4.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient4.missing_for_kawasaki), 2)

        self.assertEqual(patient5.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient5.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 5)
        self.assertEqual(len(patient5.missing_for_kawasaki), 2)

        # Add another condition per patient and repeat
        patient2.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient3.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient4.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient5.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient1.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts with five extra conditions
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient1.reasons_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 6)
        self.assertEqual(len(patient1.missing_for_kawasaki), 1)

        self.assertEqual(patient2.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 6)
        self.assertEqual(len(patient2.missing_for_kawasaki), 1)

        self.assertEqual(patient3.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient3.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 6)
        self.assertEqual(len(patient3.missing_for_kawasaki), 1)

        self.assertEqual(patient4.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient4.reasons_for_kawasaki)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 6)
        self.assertEqual(len(patient4.missing_for_kawasaki), 1)

        self.assertEqual(patient5.calculate_kawasaki_score(), 0.5)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient5.reasons_for_kawasaki)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 6)
        self.assertEqual(len(patient5.missing_for_kawasaki), 1)

    def test_calculate_kawasaki_score_zeros(self):
        # Prepare
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")
        date_hundred = datetime.date.fromisoformat("1920-02-02")
        # Patient with no conditions and wrong age
        patient0: Patient = Patient(0, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        # Patient with no conditions and correct age
        patient1: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        # Patient with all (major) conditions and wrong age
        patient2: Patient = Patient(4, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        # Patient with one condition and wrong age
        patient3: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        # Patient with one condition and wrong age
        patient4: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        # Patient with one condition and wrong age
        patient5: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        # Patient with one condition and wrong age
        patient6: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        # Patient with one condition and wrong age
        patient7: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)
        # Patient with one condition and wrong age
        patient8: Patient = Patient(2, name=self.TEST_NAME, birthdate=date_hundred, case_date=case_date)

        patient2.add_condition(SnomedConcepts.FEVER.value)
        patient2.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient2.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient2.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient2.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient2.add_condition(SnomedConcepts.ERUPTION.value)

        patient3.add_condition(SnomedConcepts.FEVER.value)
        patient4.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient5.add_condition(SnomedConcepts.OTHER_CONJUNCTIVITIS.value)
        patient6.add_condition(SnomedConcepts.LYMPHADENOPATHY.value)
        patient7.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)
        patient8.add_condition(SnomedConcepts.ERUPTION.value)

        # Asserts for patient without conditions and wrong age
        self.assertEqual(patient0.calculate_kawasaki_score(), 0.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient0.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient0.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient0.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient0.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient0.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient0.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient0.missing_for_kawasaki)
        self.assertEqual(len(patient0.reasons_for_kawasaki), 0)
        self.assertEqual(len(patient0.missing_for_kawasaki), 7)

        # Asserts for patient without conditions, but right age
        self.assertEqual(patient1.calculate_kawasaki_score(), 0.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient1.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient1.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient1.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient1.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient1.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient1.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient1.missing_for_kawasaki)
        self.assertEqual(len(patient1.reasons_for_kawasaki), 1)
        self.assertEqual(len(patient1.missing_for_kawasaki), 6)

        # Asserts for patient with all conditions, but wrong age
        self.assertEqual(patient2.calculate_kawasaki_score(), 0.0)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient2.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient2.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient2.reasons_for_kawasaki)
        self.assertEqual(len(patient2.reasons_for_kawasaki), 6)
        self.assertEqual(len(patient2.missing_for_kawasaki), 1)

        # Asserts for patient with one condition, but wrong age
        self.assertEqual(patient3.calculate_kawasaki_score(), 0.0)
        self.assertEqual(patient4.calculate_kawasaki_score(), 0.0)
        self.assertEqual(patient5.calculate_kawasaki_score(), 0.0)
        self.assertEqual(patient6.calculate_kawasaki_score(), 0.0)
        self.assertEqual(patient7.calculate_kawasaki_score(), 0.0)
        self.assertEqual(patient8.calculate_kawasaki_score(), 0.0)

        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient3.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient4.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient5.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient6.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient7.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_YOUNGER_THAN_EIGHT in patient8.missing_for_kawasaki)
        self.assertTrue(Patient.REASON_FEVER in patient3.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_ENANTHEM in patient4.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_CONJUNCTIVITIS in patient5.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_LYMPHNODES in patient6.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_SWOLLEN_EXTREMITIES in patient7.reasons_for_kawasaki)
        self.assertTrue(Patient.REASON_EXANTHEM in patient8.reasons_for_kawasaki)
        self.assertEqual(len(patient3.reasons_for_kawasaki), 1)
        self.assertEqual(len(patient3.missing_for_kawasaki), 6)
        self.assertEqual(len(patient4.reasons_for_kawasaki), 1)
        self.assertEqual(len(patient4.missing_for_kawasaki), 6)
        self.assertEqual(len(patient5.reasons_for_kawasaki), 1)
        self.assertEqual(len(patient5.missing_for_kawasaki), 6)
        self.assertEqual(len(patient6.reasons_for_kawasaki), 1)
        self.assertEqual(len(patient6.missing_for_kawasaki), 6)
        self.assertEqual(len(patient7.reasons_for_kawasaki), 1)
        self.assertEqual(len(patient7.missing_for_kawasaki), 6)
        self.assertEqual(len(patient8.reasons_for_kawasaki), 1)
        self.assertEqual(len(patient8.missing_for_kawasaki), 6)

    def test_calculate_pims_score_full_diagnosis(self):
        # Prepare
        # Set correct age
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")
        date_two = datetime.date.fromisoformat("2012-07-08")
        date_three = datetime.date.fromisoformat("2002-05-11")

        # Case 1: Fever, Covid, Inflammation Lab (CRP high), Kawasaki-Symptoms, Cardial Symptoms
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_high_measurement(SnomedConcepts.CRP.value)
        patient.add_condition(SnomedConcepts.FEVER.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_condition(SnomedConcepts.ERUPTION.value)
        patient.add_condition(SnomedConcepts.PERICARDITIS.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 1.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertEqual(len(present), 6)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertEqual(len(missing), 1)

        # Case 2: Fever (implied by kawasaki), Covid, Inflammation Lab (CRP high), Kawasaki, Gastro-symptoms
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_two, case_date=case_date)
        patient.add_high_measurement(SnomedConcepts.CRP.value)
        patient.add_condition(SnomedConcepts.KAWASAKI.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_condition(SnomedConcepts.ERUPTION.value)
        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 1.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_HAS_KAWASAKI in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertEqual(len(present), 5)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertEqual(len(missing), 1)

        # Case 3: Fever, Covid, Inflammation Lab (CRP high), Gastro-symptoms, Cardial Symptoms
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_three, case_date=case_date)
        patient.add_high_measurement(SnomedConcepts.CRP.value)
        patient.add_condition(SnomedConcepts.FEVER.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)
        patient.add_condition(SnomedConcepts.PERICARDITIS.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 1.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertEqual(len(present), 6)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in missing)
        self.assertEqual(len(missing), 1)

    def test_calculate_pims_score_increased_prob(self):
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2019-01-03")

        # Case 1: Fever, Covid, Inflammation Lab (CRP high)
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_high_measurement(SnomedConcepts.CRP.value)
        patient.add_condition(SnomedConcepts.FEVER.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertEqual(len(present), 4)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in missing)
        self.assertEqual(len(missing), 3)

        # Case 2: Kawasaki (implies Fever and symptoms), Covid, Inflammation Lab (CRP high)
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_high_measurement(SnomedConcepts.CRP.value)
        patient.add_condition(SnomedConcepts.KAWASAKI.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_HAS_KAWASAKI in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertEqual(len(present), 4)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertEqual(len(missing), 2)

        # Case 3: Kawasaki (implies Fever and symptoms), Cardial and Gastrointestinal conditions
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_condition(SnomedConcepts.KAWASAKI.value)
        patient.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertTrue(patient.REASON_HAS_KAWASAKI in present)
        self.assertEqual(len(present), 4)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 2)

        # Case 4: Kawasaki symptoms, cardiac and gastrointestinal conditions, Inflammation in lab
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)
        patient.add_high_measurement(SnomedConcepts.CRP.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertEqual(len(present), 5)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertEqual(len(missing), 2)

        # Case 5: All symptoms but covid
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)
        patient.add_condition(SnomedConcepts.FEVER.value)
        patient.add_high_measurement(SnomedConcepts.CRP.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertEqual(len(present), 6)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertEqual(len(missing), 1)

        # Case 6: All symptoms but fever (no kawasaki)
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_high_measurement(SnomedConcepts.CRP.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertEqual(len(present), 6)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertEqual(len(missing), 1)

        # Case 7: All symptoms but inflammation lab
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient.add_condition(SnomedConcepts.PERICARDITIS.value)
        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_condition(SnomedConcepts.FEVER.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertEqual(len(present), 6)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 1)

        # Case 8: All symptoms including kawasaki but not cardiac or gastrointestinal
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_condition(SnomedConcepts.DISORDER_OF_LIP.value)
        patient.add_condition(SnomedConcepts.KAWASAKI.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_condition(SnomedConcepts.FEVER.value)
        patient.add_high_measurement(SnomedConcepts.CRP.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_HAS_KAWASAKI in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertEqual(len(present), 5)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertEqual(len(missing), 2)

        # case 9: covid + kawasaki
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_condition(SnomedConcepts.KAWASAKI.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.75)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_HAS_KAWASAKI in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertEqual(len(present), 3)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 3)

    def test_calculate_pims_score_low_prob(self):
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_one = datetime.date.fromisoformat("2014-11-11")

        # Case 1: Covid, Inflammation Lab (CRP high)
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_high_measurement(SnomedConcepts.CRP.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.5)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertEqual(len(present), 3)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in missing)
        self.assertEqual(len(missing), 4)

        # Case 2: Covid, Fever
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_one, case_date=case_date)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_condition(SnomedConcepts.FEVER.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.5)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertEqual(len(present), 3)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 4)

    def test_calculate_pims_score_zero(self):
        # Prepare
        # Set correct age
        case_date = datetime.date.fromisoformat("2020-02-02")
        date_valid = datetime.date.fromisoformat("2019-01-03")
        date_invalid = datetime.date.fromisoformat("1995-07-08")

        # Case 1:Patient with enough conditions, but too old
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_invalid, case_date=case_date)
        patient.add_high_measurement(SnomedConcepts.CRP.value)
        patient.add_condition(SnomedConcepts.FEVER.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_condition(SnomedConcepts.ERUPTION.value)
        patient.add_condition(SnomedConcepts.PERICARDITIS.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertEqual(len(present), 5)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in missing)
        self.assertEqual(len(missing), 2)

        # Case 2: Same age, but other condition combination (kawasaki)
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_invalid, case_date=case_date)
        patient.add_high_measurement(SnomedConcepts.CRP.value)
        patient.add_condition(SnomedConcepts.KAWASAKI.value)
        patient.add_condition(SnomedConcepts.COVID_19.value)
        patient.add_condition(SnomedConcepts.ERUPTION.value)
        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_COVID in present)
        self.assertTrue(patient.REASON_HAS_KAWASAKI in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertEqual(len(present), 4)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in missing)
        self.assertEqual(len(missing), 2)

        # Case 3: No conditions but correct age group
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_valid, case_date=case_date)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertEqual(len(present), 1)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in missing)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 6)

        # Case 4: just one condition
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_valid, case_date=case_date)

        patient.add_high_measurement(SnomedConcepts.CRP.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in present)
        self.assertEqual(len(present), 2)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in missing)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertEqual(len(missing), 5)

        # Case 5: just one condition
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_valid, case_date=case_date)

        patient.add_condition(SnomedConcepts.FEVER.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_FEVER in present)
        self.assertEqual(len(present), 2)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in missing)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 5)

        # Case 6: just one condition
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_valid, case_date=case_date)

        patient.add_condition(SnomedConcepts.COVID_19.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_COVID in present)
        self.assertEqual(len(present), 2)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in missing)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 5)

        # Case 7: just one condition
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_valid, case_date=case_date)

        patient.add_condition(SnomedConcepts.SWELLING_LOWER_LIMB.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_KAWASAKI_SYMPTOMS in present)
        self.assertEqual(len(present), 2)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 5)

        # Case 8: just one condition
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_valid, case_date=case_date)

        patient.add_condition(SnomedConcepts.MYOCARDITIS.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in present)
        self.assertEqual(len(present), 2)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in missing)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 5)

        # Case 9: just one condition
        patient: Patient = Patient(1, name=self.TEST_NAME, birthdate=date_valid, case_date=case_date)

        patient.add_condition(SnomedConcepts.NAUSEA_AND_VOMITING.value)

        patient.calculate_pims_score()
        self.assertEqual(patient.pims_score, 0.0)
        present = patient.reasons_for_pims
        missing = patient.missing_for_pims
        self.assertTrue(patient.REASON_YOUNGER_THAN_TWENTY in present)
        self.assertTrue(patient.REASON_GASTRO_INTESTINAL_CONDITION in present)
        self.assertEqual(len(present), 2)
        self.assertTrue(patient.REASON_CARDIAL_CONDITION in missing)
        self.assertTrue(patient.REASON_COVID in missing)
        self.assertTrue(patient.REASON_FEVER in missing)
        self.assertTrue(patient.REASON_INFLAMMATION_LAB in missing)
        self.assertEqual(len(missing), 5)

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
