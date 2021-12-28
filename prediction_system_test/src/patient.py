import datetime


class Patient:

    younger_than_eight: str: "0-7 Jahre alt"
    younger_than_twenty: str: "0-7 Jahre alt"
    fever: str = "Fieber"
    exanthem: str = "Exanthem"
    enanthem: str = "Entzündung von Mund oder Zunge"
    swollen_extremities: str = "Geschwollene Extremitäten"
    conjuncitivitis: str = "Konjunktivitis"
    lymphadenopathy: str = "Lymphadenopathie"
    cardial_component: str = "Kardiale Erkrankung"
    gastro_intestinal_component: str = "Übelkeit, Erbrechen, Bauchschmerzen und/oder Durchfall"
    inflammation_lab: str = "Entzündungsparameter im Blut"
    oedema: str = "Aszites, Pleuraergüsse oder Perikardergüsse"
    covid: str = "Covid-19"

    def __init__(self, id, day, month, year):
        self.id = id
        self.day = day
        self.month = month
        self.year = year
        self.conditions = list()
        self.measurements = list()
        self.procedures = list()
        self.reasons_for_kawasaki = list()
        self.reasons_for_pims = list()

    def add_condition(self, condition):
        self.conditions.append(condition)

    def add_measurement(self, measurement):
        self.measurements.append(measurement)

    def add_procedure(self, procedure):
        self.procedures.append(procedure)

    def calculate_age(self):
        current_date = datetime.date.today()
        return current_date.year - self.year - ((current_date.month, current_date.day) < (self.month, self.day))

    def has_fever(self) -> bool:
        # Snomed ids for fever, fever with chills, febrile convulsions, continuous fever
        snomed_fever_ids = [437663, 4164645, 444413, 4158330]
        return any(x in snomed_fever_ids for x in self.conditions)

    def has_exanthem(self) -> bool:
        # Snomed id for Eruption (R21: Exanthem maps to this): 140214
        # Snomed id for Skin AND/OR mucosa finding (B.09 'Nicht näher bezeichnete Virusinfektion, die durch Haut- und
        # Schleimhautläsionen gekennzeichnet ist' maps to this): 4212577
        # Snomed id for Disease due to Orthopoxvirus (B08.0: Sonstige näher bezeichnete Virusinfektionen, die durch
        # Haut- und Schleimhautläsionen gekennzeichnet sind): 443724
        snomed_exanthem_ids = [140214, 4212577, 443724]
        return any(x in snomed_exanthem_ids for x in self.conditions)

    def has_swollen_extremities(self) -> bool:
        # Snomed id for Swelling/Lump finding: 443257 (R22)
        # Swelling upper limb: 4168701 (R22.3)
        # Swelling lower limb: 4171919 (R22.4)
        swollen_extremities_ids = [443257, 4168701, 4171919]
        return any(x in swollen_extremities_ids for x in self.conditions)

    def has_conjunctivitis(self):
        # Snomed id for (other/unspecified) conjunctivitis: 379019
        # Mucopurulent conjunctivitis: 376422
        # Acute conjunctivitis: 376707
        conjunctivitis_ids = [379019, 376422, 376707]
        return any(x in conjunctivitis_ids for x in self.conditions)

    def has_lymphadenopathy(self):
        # Snomed id for Lymphadenopathy: 315085
        # Localized enlarged lymph nodes: 4168700
        # Generalized enlarged lymph nodes: 4165998
        lymphadenopathy_ids = [315085, 4168700, 4165998]
        return any(x in lymphadenopathy_ids for x in self.conditions)

    def has_mouth_or_mucosa_inflammation(self):
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

    def has_cardial_condition(self):
        # Snomed ids for:
        # I30: Akute Perikarditis: .0 (315293) .1 (4217075) .8/.9 (320116)
        # I21: Akuter Myokardinfarkt: .0 (434376) .1 (438170) .2/.3 (312327) .4 (4270024) .9 (312327)
        # I40: Myokariditis: .0 (4331309) .1 (4143969) .8/.9 (312653)
        snomed_cor_ids = [315293, 4217075, 320116, 434376, 438170, 312327, 4270024, 312327, 4331309, 4143969, 312653]
        return any(x in snomed_cor_ids for x in self.conditions)

    def has_gastro_intestinal_component(self):
        # Nausea and vomiting (ICD10GM R11 --> SNOMED-ID 27674)
        # (lower) Abdominal Pain (ICD10GM R10.3, R10.4, R10 --> SNOMED-ID 4182562, 200219, 4116811)
        # (Severe) Diarrhea (and vomiting) (SNOMED-ID 196523, 4091519, 4249551, 196151)
        snomed_gastro_ids = [27674, 4182562, 200219, 4116811, 196523, 4091519, 4249551, 196151]
        return any(x in snomed_gastro_ids for x in self.conditions)

    def has_inflammation_lab(self):
        # Todo Measurement-Auswertung nach zB CRP, BSG, etc
        return False

    def has_oedema(self):
        # Todo Test auf Asziztis, Pleura oder Perikardergüsse - Diagnosen
        return False

    def has_covid(self):
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

    def calculate_kawasaki_score(self) -> float:
        score = 0
        max_score = 9.0
        if self.calculate_age() < 8:
            score += self.calculate_shared_score()

        return score / max_score

    def calculate_shared_score(self) -> int:
        score: int = 0

        if self.has_fever():
            score += 3
            self.reasons_for_kawasaki.append(self.fever)
        if self.has_swollen_extremities():
            score += 1
        if self.has_conjunctivitis():
            score += 1
        if self.has_lymphadenopathy():
            score += 1
        if self.has_mouth_or_mucosa_inflammation():
            score += 1
        if self.has_inflammation_lab():
            score += 1
        if self.has_cardial_condition():
            score += 1

        return score

    def calculate_pims_score(self) -> float:
        score: int = 0
        max_score = 9.0 + 1.0

        if not self.has_covid():
            return score

        if self.calculate_age() < 20:
            score += self.calculate_shared_score()

        if self.has_gastro_intestinal_component():
            score += 1

        return score / max_score
