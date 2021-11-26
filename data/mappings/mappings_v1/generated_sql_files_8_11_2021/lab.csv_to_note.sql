
INSERT INTO note
(
    note_id,
    person_id,
    note_date,
    note_datetime,
    note_type_concept_id,
    note_class_concept_id,
    note_title,
    note_text,
    encoding_concept_id,
    language_concept_id,
    provider_id,
    visit_occurrence_id,
    visit_detail_id,
    note_source_value
)
SELECT
 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS note_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS person_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS note_date,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS note_datetime,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS note_type_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS note_class_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS note_title,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS note_text,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS encoding_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS language_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS provider_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_occurrence_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_detail_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS note_source_value

FROM lab.csv
;