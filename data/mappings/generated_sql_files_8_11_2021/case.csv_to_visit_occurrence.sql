
INSERT INTO visit_occurrence
(
    person_id,
    visit_occurrence_id,
    visit_source_value,
    visit_start_date,
    visit_start_datetime,
    visit_end_date,
    visit_end_datetime,
    provider_id,
    visit_type_concept_id, -- 32817? 
    visit_concept_id, -- 38004515 Hospital
    care_site_id,
    visit_source_concept_id,
    admitting_source_concept_id,
    admitting_source_value,
    discharge_to_concept_id,
    discharge_to_source_value,
    preceding_visit_occurrence_id
)
SELECT
    case.csv.patient_id AS person_id,

    case.csv.case_id AS visit_occurrence_id,

    case.csv.case_id AS visit_source_value,

    case.csv.start_date AS visit_start_date,

    case.csv.start_date AS visit_start_datetime,

    case.csv.end_date AS visit_end_date,

    case.csv.end_date AS visit_end_datetime,

    case.csv.provider_id AS provider_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_type_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS care_site_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_source_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS admitting_source_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS admitting_source_value,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS discharge_to_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS discharge_to_source_value,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS preceding_visit_occurrence_id

FROM case.csv
;