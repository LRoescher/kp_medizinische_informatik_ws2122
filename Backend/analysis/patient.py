import datetime

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
    REASON_ENANTHEM: str = "Enanthem"
    REASON_SWOLLEN_EXTREMITIES: str = "Geschwollene Extremitäten"
    REASON_CONJUNCTIVITIS: str = "Konjunktivitis"
    REASON_SWOLLEN_LYMPHNODES: str = "Lymphadenopathie"
    REASON_CARDIAL_CONDITION: str = "Kardiale Erkrankung"
    REASON_GASTRO_INTESTINAL_CONDITION: str = "Übelkeit, Erbrechen, Bauchschmerzen und/oder Durchfall"
    REASON_INFLAMMATION_LAB: str = "Entzündungsparameter im Blut"
    REASON_COVID: str = "Covid-19 Erkrankung"
    REASON_KAWASAKI: str = "Kawasaki-Syndrom"
    REASON_PIMS: str = "Pediatric Inflammatory Multisystem Syndrome (PIMS)"
    REASON_KAWASAKI_SYMPTOMS: str = "Exanthem, Enanthem, Konjunktivitis oder geschwollene, gerötete Extremitäten"
    REASON_COAGULOPATHY = "Gerinnungsstörung"

    def __init__(self, patient_id: int, name: str, birthdate: datetime.date, case_date: datetime.date):
        """
        Creates a new patient.

        :param patient_id: unique identifier (Long)
        :param name: name of the patient (firstname + lastname)
        :param birthdate: date of birth
        :param case_date: date the data set for this patient was created
        """
        self.id: int = patient_id
        self.name: str = name
        self.birthdate: datetime.date = birthdate
        self.day: int = birthdate.day
        self.month: int = birthdate.month
        self.year: int = birthdate.year
        self.case_date: datetime.date = case_date
        self.conditions = list()
        self.high_measurements = list()
        self.procedures = list()
        self.kawasaki_score: float = 0.0
        self.pims_score: float = 0.0
        self.reasons_for_kawasaki = list()
        self.missing_for_kawasaki = list()
        self.reasons_for_pims = list()
        self.missing_for_pims = list()

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
        return self.case_date.year - self.year - ((self.case_date.month, self.case_date.day) < (self.month, self.day))

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

    def has_enanthem(self):
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
                          SnomedConcepts.MYOCARDITIS.value, 4143969, 312653,
                          SnomedConcepts.PERICARDIAL_EFFUSION]
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
        # Procalictonin (33959-8 -> 3046279)
        loinc_ids = [3020460, 42870365, 3013707, 3000905, 3046279]
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
                            SnomedConcepts.POST_COVID.value]
        return any(x in snomed_covid_ids for x in self.conditions)

    def has_kawasaki(self):
        snomed_kawasaki_id = SnomedConcepts.KAWASAKI.value
        return snomed_kawasaki_id in self.conditions

    def has_pims(self):
        snomed_pims_id = SnomedConcepts.PIMS.value
        return snomed_pims_id in self.conditions

    def calculate_kawasaki_score(self) -> float:
        """
        Calculates a score of the patient having Kawasaki-Disease. The score will be between 0.0 and 1.0.
        A score of 1.0 means that a patient either has the diagnosis Kawasaki-Syndrome or has all symptoms and the
        correct age. The criteria are fever and 4 of the 5 following symptoms: Conjunctivitis, Lymphadenopathy, Exanthem,
        Enanthem and swollen extremities.
        0.75 means incomplete kawasaki-disease (fever and less than four of the mentioned symptoms, but at least one).
        0.5 means that there is at least one of the symptoms present. 0.0 means that there are no symptoms present or
        the patient has the wrong age.

        At the same time the pro/con-lists for the kawasaki-disease are updated.

        :return: The score as a float
        """
        self.reasons_for_kawasaki.clear()
        self.missing_for_kawasaki.clear()

        # Count number of present symptoms and update reason/missing lists
        num_of_symptoms = self._count_kawasaki_symptoms()

        # Kawasaki is already registered as a condition -> Return 100%
        if self.has_kawasaki():
            self.reasons_for_kawasaki.append(self.REASON_KAWASAKI)
            self.kawasaki_score = 1.0

        # Too old -> Not Kawasaki -> Return 0%
        elif self.calculate_age() >= 8:
            self.kawasaki_score = 0.0

        # Correct age
        else:

            # Fever is needed for complete and incomplete kawasaki
            if self.has_fever():
                # Fever and at least four other symptoms for complete kawasaki
                if num_of_symptoms >= 5:
                    self.kawasaki_score = 1.0
                # Fever and at least on more symptom for incomplete kawasaki
                elif num_of_symptoms >= 2:
                    self.kawasaki_score = 0.75
                # Might be kawasaki with missing data
                else:
                    self.kawasaki_score = 0.5

            # No Fever -> might be incomplete data
            else:
                # At least one kawasaki symptom
                if num_of_symptoms > 0:
                    self.kawasaki_score = 0.5
                # No kawasaki symptoms -> Return 0%
                else:
                    self.kawasaki_score = 0.0

        return self.kawasaki_score

    def _count_kawasaki_symptoms(self) -> int:
        """
        Calculates the number of side symptoms of a patient. Also edits the lists reasons-for-kawasaki and
        missing-for-kawasaki.
        The 5 side conditions (enanthem, exanthem, swollen extremities, conjunctivitis and lymphadenopathy) are checked.
        If they are present they are added to the pro-kawasaki-list. If not, they are added to the missing list.
        The number of side symptoms is returned.
        :return: number of side symptoms the patient has
        """
        num_of_symptoms = 0

        if self.calculate_age() < 8:
            self.reasons_for_kawasaki.append(self.REASON_YOUNGER_THAN_EIGHT)
        else:
            self.missing_for_kawasaki.append(self.REASON_YOUNGER_THAN_EIGHT)

        if self.has_fever():
            num_of_symptoms += 1
            self.reasons_for_kawasaki.append(self.REASON_FEVER)
        else:
            self.missing_for_kawasaki.append(self.REASON_FEVER)

        if self.has_exanthem():
            num_of_symptoms += 1
            self.reasons_for_kawasaki.append(self.REASON_EXANTHEM)
        else:
            self.missing_for_kawasaki.append(self.REASON_EXANTHEM)

        if self.has_swollen_extremities():
            num_of_symptoms += 1
            self.reasons_for_kawasaki.append(self.REASON_SWOLLEN_EXTREMITIES)
        else:
            self.missing_for_kawasaki.append(self.REASON_SWOLLEN_EXTREMITIES)

        if self.has_conjunctivitis():
            num_of_symptoms += 1
            self.reasons_for_kawasaki.append(self.REASON_CONJUNCTIVITIS)
        else:
            self.missing_for_kawasaki.append(self.REASON_CONJUNCTIVITIS)

        if self.has_lymphadenopathy():
            num_of_symptoms += 1
            self.reasons_for_kawasaki.append(self.REASON_SWOLLEN_LYMPHNODES)
        else:
            self.missing_for_kawasaki.append(self.REASON_SWOLLEN_LYMPHNODES)

        if self.has_enanthem():
            num_of_symptoms += 1
            self.reasons_for_kawasaki.append(self.REASON_ENANTHEM)
        else:
            self.missing_for_kawasaki.append(self.REASON_ENANTHEM)

        return num_of_symptoms

    def calculate_pims_score(self) -> float:
        """
        Calculates a score for the patient having PIMS. The score will be between 0.0 and 1.0.
        A score of 1.0 means that the patient has all symptoms or conditions for a diagnosis with PIMS. A score of 0.75
        means that at least half of the parameters are present and the patient has the correct age. 0.5 means that at
        least one symptom is present and the patient has the correct age. Lastly, a score of 0.0 means that the patient
        has either no symptoms colliding with PIMS or is in the wrong age range.
        For a diagnosis with PIMS the patient has to either have an already existing PIMS-diagnosis or meet all criteria
        specified by the WHO.
        According to that, the patient has to be between 0 - 19 years old and has to have the following conditions:
        Covid-19, Fever, Inflammation markers and two of the following: a heart condition, a gastro-intestinal condition
        or a kawasaki-symptom (conjunctivitis, swollen/red extremities, lymphadenopathy, inflammation of mouth, lips,
        tongue or mucosa).

        At the same time the patients list for reasons and missing reasons for PIMS are updated.

        :return: The calculated score as a float
        """
        self.reasons_for_pims.clear()
        self.missing_for_pims.clear()

        # Count number of present symptoms and update reason/missing lists
        num_of_symptoms = self._count_pims_symptoms()

        # PIMS is already registered as a condition -> Return 100%
        if self.has_pims():
            self.reasons_for_pims.append(self.REASON_PIMS)
            self.pims_score = 1.0

        elif self.calculate_age() >= 20:
            self.pims_score = 0.0

        # PIMS needs age < 20, fever (can be implied by kawasaki), inflammation markers, covid-19
        elif (self.has_fever() or self.has_kawasaki()) and self.has_covid() and self.has_inflammation_lab():
            # Need two of either kawasaki or kawasaki symptoms, caridal condition, gastro-intestinal condition
            num_of_side_symptoms: int = 0
            if self.has_kawasaki():
                num_of_side_symptoms += 1
            elif self.has_exanthem() or self.has_enanthem() or self.has_conjunctivitis() or self.has_swollen_extremities():
                num_of_side_symptoms += 1

            if self.has_cardiac_condition():
                num_of_side_symptoms += 1

            if self.has_gastro_intestinal_condition():
                num_of_side_symptoms += 1

            if self.has_coagulopathy():
                num_of_side_symptoms += 1

            if num_of_side_symptoms >= 2:
                # "Complete" PIMS
                self.pims_score = 1.0
            else:
                # Not enough symptoms for PIMS
                self.pims_score = 0.75

        # Can't be PIMS -> Count parameters
        else:
            if num_of_symptoms >= 3:
                # many conditions, but not the right combination:
                self.pims_score = 0.75
            elif num_of_symptoms >= 1:
                # some conditions
                self.pims_score = 0.5
            else:
                # not enough conditions
                self.pims_score = 0.0

        return self.pims_score

    def _count_pims_symptoms(self) -> int:
        """
        Updates the pro/con lists for the PIMS-condition. Returns the number of symptoms present.
        """
        num_of_symptoms: int = 0

        if self.calculate_age() < 20:
            self.reasons_for_pims.append(self.REASON_YOUNGER_THAN_TWENTY)
        else:
            self.missing_for_pims.append(self.REASON_YOUNGER_THAN_TWENTY)

        if self.has_fever():
            self.reasons_for_pims.append(self.REASON_FEVER)
            num_of_symptoms += 1
        else:
            self.missing_for_pims.append(self.REASON_FEVER)

        if self.has_kawasaki():
            self.reasons_for_pims.append(self.REASON_KAWASAKI)
            num_of_symptoms += 1
            # Fever is implied with kawasaki diagnosis
            if not self.has_fever():
                num_of_symptoms += 1
        elif self.has_exanthem() or self.has_enanthem() or self.has_conjunctivitis() or self.has_swollen_extremities():
            self.reasons_for_pims.append(self.REASON_KAWASAKI_SYMPTOMS)
            num_of_symptoms += 1
        else:
            self.missing_for_pims.append(self.REASON_KAWASAKI_SYMPTOMS)

        if self.has_cardiac_condition():
            self.reasons_for_pims.append(self.REASON_CARDIAL_CONDITION)
            num_of_symptoms += 1
        else:
            self.missing_for_pims.append(self.REASON_CARDIAL_CONDITION)

        if self.has_coagulopathy():
            self.reasons_for_pims.append(self.REASON_COAGULOPATHY)
            num_of_symptoms += 1
        else:
            self.missing_for_pims.append(self.REASON_COAGULOPATHY)

        if self.has_gastro_intestinal_condition():
            self.reasons_for_pims.append(self.REASON_GASTRO_INTESTINAL_CONDITION)
            num_of_symptoms += 1
        else:
            self.missing_for_pims.append(self.REASON_GASTRO_INTESTINAL_CONDITION)

        if self.has_covid():
            self.reasons_for_pims.append(self.REASON_COVID)
            num_of_symptoms += 1
        else:
            self.missing_for_pims.append(self.REASON_COVID)

        if self.has_inflammation_lab():
            self.reasons_for_pims.append(self.REASON_INFLAMMATION_LAB)
            num_of_symptoms += 1
        else:
            self.missing_for_pims.append(self.REASON_INFLAMMATION_LAB)

        return num_of_symptoms

    def has_pericardial_effusions(self):
        """
        Returns True if the patient has pericardial effusions as a condition.
        """
        return 4108814 in self.conditions

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

    def has_coagulopathy(self):
        """
        Returns True if the patient has markers for coagulopathy in his/her blood.
        """
        ids = [SnomedConcepts.PTT_BLOOD.value,
               SnomedConcepts.PTT_PLASMA.value,
               SnomedConcepts.D_DIMER.value,
               SnomedConcepts.PT.value]
        return any(x in ids for x in self.high_measurements)
