
INSERT INTO person
(
    person_id,
    person_source_value,
    year_of_birth,
    month_of_birth,
    day_of_birth,
    birth_datetime,
    birth_datetime, -- [!#WARNING!#] THIS TARGET FIELD WAS ALREADY USED
    gender_concept_id, -- 8532 FEMALE 8507 MALE
    gender_source_value,
    provider_id,
    race_concept_id, -- set 4218674 Unknown racial group
    ethnicity_concept_id, -- 0? 38003563 (Hispanic?), 38003564 (Not hispanic?)
    location_id, -- Zurückspiegeln aus location table
    care_site_id,
    race_source_value,
    race_source_concept_id,
    ethnicity_source_value,
    gender_source_concept_id,
    ethnicity_source_concept_id
)
SELECT
    person.csv.patient_id AS person_id,

    person.csv.patient_id AS person_source_value,

 -- [MAPPING COMMENT] year 
    person.csv.birthdate AS year_of_birth,

 -- [MAPPING COMMENT] month 
    person.csv.birthdate AS month_of_birth,

 -- [MAPPING COMMENT] day 
    person.csv.birthdate AS day_of_birth,

 -- [MAPPING COMMENT] Tag 
    person.csv.birthdate AS birth_datetime,

 -- [MAPPING COMMENT] Uhrzeit? oder 0:00 
    person.csv.date_of_life AS birth_datetime,

 -- [MAPPING COMMENT] w -> 8532 FEMALE m -> 8507 MALE 
    person.csv.gender AS gender_concept_id,

    person.csv.gender AS gender_source_value,

    person.csv.provider_id AS provider_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS race_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS ethnicity_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS location_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS care_site_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS race_source_value,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS race_source_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS ethnicity_source_value,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS gender_source_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS ethnicity_source_concept_id

FROM person.csv
;