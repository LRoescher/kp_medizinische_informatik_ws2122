
INSERT INTO death
(
    person_id,
    death_date,
    death_datetime,
    death_type_concept_id, -- 32817 EHR
    cause_concept_id,
    cause_source_value,
    cause_source_concept_id
)
SELECT
    person.csv.patient_id AS person_id,

 -- [MAPPING COMMENT] Format? 
    person.csv.death_date AS death_date,

 -- [MAPPING COMMENT] Format? 
    person.csv.death_date AS death_datetime,

 -- [VALUE   COMMENT] Nur mappen wenn hier "JA", dann concept EHR 
    person.csv.death AS death_type_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS cause_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS cause_source_value,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS cause_source_concept_id

FROM person.csv
;