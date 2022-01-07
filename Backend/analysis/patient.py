import datetime

from typing import Set

import pandas as pd


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

    def __init__(self, patient_id, day, month, year, name):
        """
        Creates a new patient.

        :param patient_id: unique identifier (Long)
        :param day: day of birth
        :param month: month of birth
        :param year: year of birth
        :param name: name of the patient (firstname + lastname)
        """
        self.id = patient_id
        self.day = day
        self.month = month
        self.year = year
        self.name = name
        self.conditions = list()
        self.high_measurements = list()
        self.procedures = list()
        self.kawasaki_score: float = 0.0
        self.pims_score: float = 0.0
        self.reasons_for_kawasaki = list()
        self.reasons_for_pims = list()

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
        # Snomed ids for fever, fever with chills, febrile convulsions, continuous fever
        snomed_fever_ids = [437663, 4164645, 444413, 4158330]
        return any(x in snomed_fever_ids for x in self.conditions)

    def has_exanthem(self) -> bool:
        """
        Returns True if the patient has a condition that corresponds to an exanthem (rash).

        :return: True if the patient has an exanthem
        """
        # Snomed id for Eruption (R21: Exanthem maps to this): 140214
        # Snomed id for Skin AND/OR mucosa finding (B.09 'Nicht näher bezeichnete Virusinfektion, die durch Haut- und
        # Schleimhautläsionen gekennzeichnet ist' maps to this): 4212577
        # Snomed id for Disease due to Orthopoxvirus (B08.0: Sonstige näher bezeichnete Virusinfektionen, die durch
        # Haut- und Schleimhautläsionen gekennzeichnet sind): 443724
        snomed_exanthem_ids = [140214, 4212577, 443724]
        return any(x in snomed_exanthem_ids for x in self.conditions)

    def has_swollen_extremities(self) -> bool:
        """
        Returns True if the patient has a condition that corresponds to swollen extremities or lumps in the extremities.

        :return: True if the patient has swollen extremities
        """
        # Snomed id for Swelling/Lump finding: 443257 (R22)
        # Swelling upper limb: 4168701 (R22.3)
        # Swelling lower limb: 4171919 (R22.4)
        swollen_extremities_ids = [443257, 4168701, 4171919]
        return any(x in swollen_extremities_ids for x in self.conditions)

    def has_conjunctivitis(self):
        """
        Returns True if the patient has conjunctivitis. (Sickness that manifests in inflammation of the eye(s)).

        :return: True if the patient has conjunctivitis
        """
        # Snomed id for (other/unspecified) conjunctivitis: 379019
        # Mucopurulent conjunctivitis: 376422
        # Acute conjunctivitis: 376707
        conjunctivitis_ids = [379019, 376422, 376707]
        return any(x in conjunctivitis_ids for x in self.conditions)

    def has_lymphadenopathy(self):
        """
        Returns True if the patient has swollen lymph nodes.

        :return: True if the patient has lymphadenopathy
        """
        # Snomed id for Lymphadenopathy: 315085
        # Localized enlarged lymph nodes: 4168700
        # Generalized enlarged lymph nodes: 4165998
        lymphadenopathy_ids = [315085, 4168700, 4165998]
        return any(x in lymphadenopathy_ids for x in self.conditions)

    def has_mouth_or_mucosa_inflammation(self):
        """
        Returns True if the patient has a condition that corresponds to an inflammation of the mouth, tongue, lips are
        mucosa ("skin inside of the body").

        :return: True if the patient has an inflammation of the mouth or mucosa
        """
        # Snomed if for Disorder of oral soft tissues: 139057
        # Disorder of lip: 135858
        # Lesion of oral mucosa: 37016130
        # Duplicate codes with exanthem
        # Snomed id for Skin AND/OR mucosa finding (B.09 'Nicht näher bezeichnete Virusinfektion, die durch Haut- und
        # Schleimhautläsionen gekennzeichnet ist' maps to this): 4212577
        # Snomed id for Disease due to Orthopoxvirus (B08.0: Sonstige näher bezeichnete Virusinfektionen, die durch
        # Haut- und Schleimhautläsionen gekennzeichnet sind): 443724
        snomed_enanthem_ids = [139057, 135858, 37016130, 4212577, 443724]
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
        snomed_cor_ids = [315293, 4217075, 320116, 434376, 438170, 312327, 4270024, 312327, 4331309, 4143969, 312653]
        return any(x in snomed_cor_ids for x in self.conditions)

    def has_gastro_intestinal_condition(self):
        """
        Returns True if the patient has a condition that comes with stomach pains, diarrhea, nausea and/or vomiting.

        :return: True if the patient has a gastro-intestinal condition
        """
        # Nausea and vomiting (ICD10GM R11 --> SNOMED-ID 27674)
        # (lower) Abdominal Pain (ICD10GM R10.3, R10.4, R10 --> SNOMED-ID 4182562, 200219, 4116811)
        # (Severe) Diarrhea (and vomiting) (SNOMED-ID 196523, 4091519, 4249551, 196151)
        snomed_gastro_ids = [27674, 4182562, 200219, 4116811, 196523, 4091519, 4249551, 196151]
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
        # Ascites (R18 -> 200528)
        # Pleural Effusion (J90 -> 254061)
        # Pericardial Effusion (I31.3 -> 4108814)
        snomed_oedema_ids = [200528, 254061, 4108814]
        return any(x in snomed_oedema_ids for x in self.conditions)

    def has_covid(self):
        """
        Returns whether or not the patient has COVID-19. Includes cases where the virus has been identified and
        statements of the patient himself.

        :return: True if the patient has COVID-19
        """
        # Snomed ifs for:
        # U07.1 Emergency use of U07.1 | COVID-19, virus identified -> 37311061
        # U07.2 Emergency use of U07.2 | COVID-19, virus not identified -> 37311060
        #
        # ToDo: ETL-Job anpassen. Hier werden icd codes verwendet nicht icd 10 gm codes, omop nicht aktuell
        # U08.9 Covid in der Eigenanamnese (ICD10 nicht GM!)-> 4214956, 37311061
        # U09.9 Post-Covid (ICD10 nicht GM!)-> 4214956, 37311061
        # U10.9 Multisystemisches Entzündungssyndrom in Verbindung mit COVID-19 (Pims) -> 703578
        snomed_covid_ids = [37311061, 37311060, 4214956, 703578]
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

        # Return 0.0 if not in age range
        if self.calculate_age() > 8:
            self.kawasaki_score = 0.0
        else:
            self.reasons_for_kawasaki.append(self.REASON_YOUNGER_THAN_EIGHT)
            score, max_score = self.calculate_shared_score()
            self.kawasaki_score = score / max_score

    def calculate_shared_score(self) -> (float, float):
        """
        Returns a tuple containing the score for symptoms that PIMS and Kawasaki share and the maximum score.

        :return: Tuple of floats (score, max_score)
        """
        score: float = 0.0
        max_score: float = 8.0

        if self.has_fever():
            score += 2
            self.reasons_for_kawasaki.append(self.REASON_FEVER)
            self.reasons_for_pims.append(self.REASON_FEVER)
        if self.has_swollen_extremities():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_SWOLLEN_EXTREMITIES)
            self.reasons_for_pims.append(self.REASON_SWOLLEN_EXTREMITIES)
        if self.has_conjunctivitis():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_CONJUNCTIVITIS)
            self.reasons_for_pims.append(self.REASON_CONJUNCTIVITIS)
        if self.has_lymphadenopathy():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_SWOLLEN_LYMPHNODES)
            self.reasons_for_pims.append(self.REASON_SWOLLEN_LYMPHNODES)
        if self.has_mouth_or_mucosa_inflammation():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_ENANTHEM)
            self.reasons_for_pims.append(self.REASON_ENANTHEM)
        if self.has_inflammation_lab():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_INFLAMMATION_LAB)
            self.reasons_for_pims.append(self.REASON_INFLAMMATION_LAB)
        if self.has_cardiac_condition():
            score += 1
            self.reasons_for_kawasaki.append(self.REASON_CARDIAL_CONDITION)
            self.reasons_for_pims.append(self.REASON_CARDIAL_CONDITION)

        return score, max_score

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

        if not self.has_covid():
            self.pims_score = 0.0

        self.reasons_for_pims.append(self.REASON_COVID)

        if not self.calculate_age() < 20:
            self.pims_score = 0.0

        self.reasons_for_pims.append(self.REASON_YOUNGER_THAN_TWENTY)

        score, max_score = self.calculate_shared_score()
        max_score += 1.5

        if self.has_gastro_intestinal_condition():
            score += 1
            self.reasons_for_pims.append(self.REASON_GASTRO_INTESTINAL_CONDITION)

        if self.has_effusion():
            score += 0.5
            self.reasons_for_pims.append(self.REASON_EFFUSION)

        self.pims_score = score / max_score
