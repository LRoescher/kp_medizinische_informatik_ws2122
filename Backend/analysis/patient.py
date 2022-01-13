import datetime

from typing import Set

from Backend.common.omop_enums import SnomedConcepts


class Patient:
    """
    Representation of patient. Has an id as a unique identifier.
    A patient also has a birthdate (a combination of year, month and day of birth) and lists of conditions, measurements
    and procedures. New elements can be added to these lists using the setters.

    The has_X() methods return a boolean stating whether or not a patient has the type of condition described by 'X'.
    The methods calculate_pims_score() and calculate_kawasaki_score() can be used to calculate a likelihood for that
    disease, taking the patients condition, age, etc. into account.
    """

    # Static fields for Strings that detail a reason for an increased likelihood for PIMS or Kawasaki disease
    REASON_YOUNGER_THAN_EIGHT: str = "0-7 Jahre alt"
    REASON_YOUNGER_THAN_TWENTY: str = "0-19 Jahre alt"
    REASON_FEVER: str = "Fieber"
    REASON_EXANTHEM: str = "Exanthem"
    REASON_ENANTHEM: str = "Entzündung von Mund und/oder Zunge"
    REASON_SWOLLEN_EXTREMITIES: str = "Geschwollene Extremitäten"
    REASON_CONJUNCTIVITIS: str = "Konjunktivitis"
    REASON_SWOLLEN_LYMPHNODES: str = "Lymphadenopathie"
    REASON_CARDIAL_CONDITION: str = "Kardiale Erkrankung"
    REASON_GASTRO_INTESTINAL_CONDITION: str = "Übelkeit, Erbrechen, Bauchschmerzen und/oder Durchfall"
    REASON_INFLAMMATION_LAB: str = "Entzündungsparameter im Blut"
    REASON_EFFUSION: str = "Flüssigkeitsansammlungen"
    REASON_COVID: str = "Covid-19 Erkrankung"

    def __init__(self, patient_id: int, name: str, birthdate: datetime.date):
        """
        Creates a new patient.

        :param patient_id: unique identifier (Long)
        :param birthdate: date of birth
        :param name: name of the patient (firstname + lastname)
        """
        self.id = patient_id
        self.name = name
        self.birthdate = birthdate
        self.day = birthdate.day
        self.month = birthdate.month
        self.year = birthdate.year
        self.conditions = list()
        self.high_measurements = list()
        self.procedures = list()
        self.kawasaki_score: float = 0.0
        self.pims_score: float = 0.0
        self.reasons_for_kawasaki = list()
        self.reasons_for_pims = list()

    def __str__(self):
        return f"{self.id}: {self.day}-{self.month}-{self.year}, Kawsawki: {self.kawasaki_score}, " \
               f"Pims: {self.pims_score}"

    def add_condition(self, condition):
        """
        Adds the condition to the list of conditions for the patient.

        :param condition: condition to be added
        :return: void
        """
        self.conditions.append(condition)

    def add_high_measurement(self, measurement):
        """
        Adds the abnormally high measurement to the list of measurements for the patient.

        :param measurement: measurement to be added
        :return: void
        """
        self.high_measurements.append(measurement)

    def add_procedure(self, procedure):
        """
        Adds the procedure to the list of procedures of the patient.

        :param procedure: procedure to be added
        :return: void
        """
        self.procedures.append(procedure)

    def calculate_age(self) -> int:
        """
        Calculates the age of the patient in years.

        :return: age in years
        """
        current_date = datetime.date.today()
        return current_date.year - self.year - ((current_date.month, current_date.day) < (self.month, self.day))

    def has_fever(self) -> bool:
        """
        Returns True if the patient has condition that corresponds to or includes fever.
        :return: True if the patient has a fever
        """
        snomed_fever_ids = [SnomedConcepts.FEVER.value,
                            SnomedConcepts.FEVER_WITH_CHILLS.value,
                            SnomedConcepts.FEBRILE_CONVULSIONS.value,
                            SnomedConcepts.CONTINUOUS_FEVER.value]
        return any(x in snomed_fever_ids for x in self.conditions)

    def has_exanthem(self) -> bool:
        """
        Returns True if the patient has a condition that corresponds to an exanthem (rash).

        :return: True if the patient has an exanthem
        """
        snomed_exanthem_ids = [SnomedConcepts.ERUPTION.value,
                               SnomedConcepts.SKIN_OR_MUCOSA_FINDING_DUE_TO_VIRUS.value,
                               SnomedConcepts.SKIN_OR_MUCOSA_FINDING_DUE_TO_OTHER_VIRUSES.value]
        return any(x in snomed_exanthem_ids for x in self.conditions)

    def has_swollen_extremities(self) -> bool:
        """
        Returns True if the patient has a condition that corresponds to swollen extremities or lumps in the extremities.

        :return: True if the patient has swollen extremities
        """
        swollen_extremities_ids = [SnomedConcepts.SWELLING.value,
                                   SnomedConcepts.SWELLING_UPPER_LIMB.value,
                                   SnomedConcepts.SWELLING_LOWER_LIMB.value]
        return any(x in swollen_extremities_ids for x in self.conditions)

    def has_conjunctivitis(self):
        """
        Returns True if the patient has conjunctivitis. (Sickness that manifests in inflammation of the eye(s)).

        :return: True if the patient has conjunctivitis
        """
        conjunctivitis_ids = [SnomedConcepts.OTHER_CONJUNCTIVITIS.value,
                              SnomedConcepts.MUCOPURULENT_CONJUNCTIVITIS.value,
                              SnomedConcepts.ACUTE_CONJUNCTIVITIS.value]
        return any(x in conjunctivitis_ids for x in self.conditions)

    def has_lymphadenopathy(self):
        """
        Returns True if the patient has swollen lymph nodes.

        :return: True if the patient has lymphadenopathy
        """
        lymphadenopathy_ids = [SnomedConcepts.LYMPHADENOPATHY.value,
                               SnomedConcepts.LOCALIZED_ENLARGED_LYMPH_NODES.value,
                               SnomedConcepts.GENERALIZED_ENLARGED_LYMPH_NODES.value]
        return any(x in lymphadenopathy_ids for x in self.conditions)

    def has_mouth_or_mucosa_inflammation(self):
        """
        Returns True if the patient has a condition that corresponds to an inflammation of the mouth, tongue, lips are
        mucosa ("skin inside of the body").

        :return: True if the patient has an inflammation of the mouth or mucosa
        """
        snomed_enanthem_ids = [SnomedConcepts.DISORDER_OF_ORAL_SOFT_TISSUE.value,
                               SnomedConcepts.DISORDER_OF_LIP.value,
                               SnomedConcepts.LESION_OF_ORAL_MUCOSA.value,
                               SnomedConcepts.SKIN_OR_MUCOSA_FINDING_DUE_TO_VIRUS.value,
                               SnomedConcepts.SKIN_OR_MUCOSA_FINDING_DUE_TO_OTHER_VIRUSES.value]
        return any(x in snomed_enanthem_ids for x in self.conditions)

    def has_cardiac_condition(self):
        """
        Returns True if the patient has a condition that is a heart disease that occurs together with or is a
        complication of PIMS or Kawasaki-disease. Such diseases include myocarditis, pericarditis and others.

        :return: True if the patient has a heart condition
        """
        # Snomed ids for:
        # I30: Akute Perikarditis: .0 (315293) .1 (4217075) .8/.9 (320116)
        # I21: Akuter Myokardinfarkt: .0 (434376) .1 (438170) .2/.3 (312327) .4 (4270024) .9 (312327)
        # I40: Myokariditis: .0 (4331309) .1 (4143969) .8/.9 (312653)
        snomed_cor_ids = [SnomedConcepts.PERICARDITIS.value, 4217075, 320116,
                          SnomedConcepts.MYOCARDIAL_INFARCTION.value, 438170, 312327, 4270024, 312327,
                          SnomedConcepts.MYOCARDITIS.value, 4143969, 312653]
        return any(x in snomed_cor_ids for x in self.conditions)

    def has_gastro_intestinal_condition(self):
        """
        Returns True if the patient has a condition that comes with stomach pains, diarrhea, nausea and/or vomiting.

        :return: True if the patient has a gastro-intestinal condition
        """
        # Nausea and vomiting (ICD10GM R11 --> SNOMED-ID 27674)
        # (lower) Abdominal Pain (ICD10GM R10.3, R10.4, R10 --> SNOMED-ID 4182562, 200219, 4116811)
        # (Severe) Diarrhea (and vomiting) (SNOMED-ID 196523, 4091519, 4249551, 196151)
        snomed_gastro_ids = [SnomedConcepts.NAUSEA_AND_VOMITING.value,
                             4182562, 200219, 4116811, 196523, 4091519, 4249551, 196151]
        return any(x in snomed_gastro_ids for x in self.conditions)

    def has_inflammation_lab(self):
        """
        Returns True if the patient has parameters in his blood that indicate an inflammation. Such parameters are for
        example CRP (c-reactive protein), ESR (Erythrocyte sedimentation rate) or an increase of leukocytes.

        :return: True if the patient has an increase of inflammation parameters in his blood
        """
        # CRP (different methods): (LOINC 1988-5, 71426-1 -> LOINC-Ids 3020460, 42870365)
        # Erythrocyte sedimentation rate: (4537-7 -> 3013707)
        # Leukocytes: (6690-2 -> 3000905)
        loinc_ids = [3020460, 42870365, 3013707, 3000905]
        return any(x in loinc_ids for x in self.high_measurements)

    def has_effusion(self):
        """
        Returns True if the patient has some kind effusion (gathering of liquid in areas where none should be). Includes
        ascites, pleural and pericardial effusions.

        :return: True if the patient has effusions
        """
        snomed_oedema_ids = [SnomedConcepts.ASCITES.value,
                             SnomedConcepts.PLEURAL_EFFUSION.value,
                             SnomedConcepts.PERICARDIAL_EFFUSION.value]
        return any(x in snomed_oedema_ids for x in self.conditions)

    def has_covid(self):
        """
        Returns whether or not the patient has COVID-19. Includes cases where the virus has been identified and
        statements of the patient himself.

        :return: True if the patient has COVID-19
        """
        snomed_covid_ids = [SnomedConcepts.COVID_19.value,
                            SnomedConcepts.COVID_19_VIRUS_NOT_IDENTIFIED.value,
                            SnomedConcepts.COVID_19_IN_PERSONAL_HISTORY.value,
                            SnomedConcepts.POST_COVID.value,
                            SnomedConcepts.PIMS.value]
        return any(x in snomed_covid_ids for x in self.conditions)

    def calculate_kawasaki_score(self) -> (float, Set[str]):
        """
        Calculates a score (probability) for the patient having Kawasaki-Disease. The score will be between 0.0 and 1.0.
        The higher the score, the higher the probability that the patient has Kawasaki.
        The calculations takes the patients age (should be around 5 years old), his conditions (symptoms of kawasaki are
        fever, conjunctivitis, swollen/red extremities, lymphadenopathy, inflammation of mouth, lips, tongue or mucosa)
        into account. Additionally his measurements are checked for signs of inflammation in his blood. Lastly the
        patient is checked for heart conditions, which are a late stage complication for Kawasaki-Disease.

        :return: Tuple containing a float in the range of 0.0 and 1.0 indicate the probability for Kawasaki-Disease and
        a set of reasons for the decision
        """
        self.reasons_for_kawasaki.clear()

        score: float = 0.0
        max_score: float = 8.0 - 1.0

        # Return 0.0 if not in age range
        if self.calculate_age() > 8:
            self.kawasaki_score = 0.0
            return self.kawasaki_score
        self.reasons_for_kawasaki.append(self.REASON_YOUNGER_THAN_EIGHT)

        if self.has_fever():
            score += 2
            self.reasons_for_kawasaki.append(self.REASON_FEVER)
        if self.has_swollen_extremities():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_SWOLLEN_EXTREMITIES)
        if self.has_conjunctivitis():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_CONJUNCTIVITIS)
        if self.has_lymphadenopathy():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_SWOLLEN_LYMPHNODES)
        if self.has_mouth_or_mucosa_inflammation():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_ENANTHEM)
        if self.has_inflammation_lab():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_INFLAMMATION_LAB)
        if self.has_cardiac_condition():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_CARDIAL_CONDITION)

        if score >= max_score:
            self.kawasaki_score = 1.0
        else:
            self.kawasaki_score = score / max_score
        return self.kawasaki_score

    def calculate_pims_score(self) -> (float, Set[str]):
        """
        Calculates a score (probability) for the patient having PIMS. The score will be between 0.0 and 1.0.
        The higher the score, the higher the probability that the patient has PIMS.
        The calculations takes the patients age (should be 0 - 19 years old), his conditions (symptoms of PIMS are
        fever, conjunctivitis, swollen/red extremities, lymphadenopathy, inflammation of mouth, lips, tongue or mucosa,
        as well as gastro intestinal conditions or effusions) into account.
        Additionally his measurements are checked for signs of inflammation in his blood. Lastly the
        patient is checked for heart conditions, which are a late stage complication for PIMS.

        :return: Tuple containing a float in the range of 0.0 and 1.0 indicate the probability for PIMS and a set of
        reasons for the decision
        """
        self.reasons_for_pims.clear()

        score: float = 0.0
        max_score: float = 11.5 - 1.0

        if self.calculate_age() >= 20:
            self.pims_score = 0.0
            return self.pims_score
        self.reasons_for_pims.append(self.REASON_YOUNGER_THAN_TWENTY)

        if self.has_covid():
            score += 2
            self.reasons_for_pims.append(self.REASON_COVID)
        if self.has_fever():
            score += 2
            self.reasons_for_pims.append(self.REASON_FEVER)
        if self.has_swollen_extremities():
            score += 1
            self.reasons_for_pims.append(self.REASON_SWOLLEN_EXTREMITIES)
        if self.has_conjunctivitis():
            score += 1
            self.reasons_for_pims.append(self.REASON_CONJUNCTIVITIS)
        if self.has_lymphadenopathy():
            score += 1
            self.reasons_for_pims.append(self.REASON_SWOLLEN_LYMPHNODES)
        if self.has_mouth_or_mucosa_inflammation():
            score += 1
            self.reasons_for_pims.append(self.REASON_ENANTHEM)
        if self.has_inflammation_lab():
            score += 1
            self.reasons_for_pims.append(self.REASON_INFLAMMATION_LAB)
        if self.has_cardiac_condition():
            score += 1
            self.reasons_for_pims.append(self.REASON_CARDIAL_CONDITION)
        if self.has_gastro_intestinal_condition():
            score += 1
            self.reasons_for_pims.append(self.REASON_GASTRO_INTESTINAL_CONDITION)
        if self.has_effusion():
            score += 0.5
            self.reasons_for_pims.append(self.REASON_EFFUSION)

        if score >= max_score:
            self.pims_score = 1.0
        else:
            self.pims_score = score / max_score

        return self.pims_score

    def has_ascites(self):
        """
        Returns True if the patient has ascites as a condition.
        """
        return 200528 in self.conditions

    def has_pericardial_effusions(self):
        """
        Returns True if the patient has pericardial effusions as a condition.
        """
        return 4108814 in self.conditions

    def has_pleural_effusions(self):
        """
        Returns True if the patient has pleural effusions as a condition.
        """
        return 254061 in self.conditions

    def has_pericarditis(self):
        """
        Returns True if the patient has pericarditis as a condition.
        """
        return 315293 in self.conditions

    def has_myocarditis(self):
        """
        Returns True if the patient has myocarditis as a condition.
        """
        return 4331309 in self.conditions
