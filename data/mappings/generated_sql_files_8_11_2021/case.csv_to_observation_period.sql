
INSERT INTO observation_period
(
    person_id,
    observation_period_id,
    observation_period_start_date,
    observation_period_end_date,
    period_type_concept_id -- 32817?
)
SELECT
    case.csv.patient_id AS person_id,

    case.csv.case_id AS observation_period_id,

 -- [MAPPING COMMENT] Format 
    case.csv.start_date AS observation_period_start_date,

    case.csv.end_date AS observation_period_end_date,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS period_type_concept_id

FROM case.csv
;