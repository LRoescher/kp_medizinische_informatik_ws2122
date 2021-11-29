
INSERT INTO condition_occurrence
(
    person_id,
    provider_id,
    condition_concept_id,
    condition_concept_id, -- [!#WARNING!#] THIS TARGET FIELD WAS ALREADY USED
    condition_source_value,
    condition_source_value, -- [!#WARNING!#] THIS TARGET FIELD WAS ALREADY USED
    condition_type_concept_id, -- 32817 EHR
    condition_source_concept_id,
    condition_status_concept_id,
    condition_start_date,
    condition_start_datetime,
    condition_occurrence_id, -- Auto generate UNIQUE
    condition_end_date,
    condition_end_datetime,
    stop_reason,
    visit_occurrence_id,
    visit_detail_id,
    condition_status_source_value
)
SELECT
    diagnosis.csv.patient_id AS person_id,

    diagnosis.csv.provider_id AS provider_id,

 -- [MAPPING COMMENT] Get from condition concept_id as concept_id_1 WHERE concept_code = icd-primary_code AND WHERE VocabularyId = "ICD10GM"  concept_relationship = „Maps to“ condition_concept_id (SNOMED) = concept_id2 
    diagnosis.csv.icd_primary_code AS condition_concept_id,

    diagnosis.csv.icd_secondary_code AS condition_concept_id,

    diagnosis.csv.icd_primary_code AS condition_source_value,

    diagnosis.csv.icd_secondary_code AS condition_source_value,

    diagnosis.csv.diagnosis_type AS condition_type_concept_id,

    diagnosis.csv.icd_version AS condition_source_concept_id,

    diagnosis.csv.clinical_status AS condition_status_concept_id,

    diagnosis.csv.admission_date AS condition_start_date,

    diagnosis.csv.admission_date AS condition_start_datetime,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS condition_occurrence_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS condition_end_date,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS condition_end_datetime,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS stop_reason,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_occurrence_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_detail_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS condition_status_source_value

FROM diagnosis.csv
;