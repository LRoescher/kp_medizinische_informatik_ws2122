
INSERT INTO measurement
(
    measurement_id,
    person_id,
    measurement_date,
    measurement_datetime,
    measurement_time,
    value_as_number,
    value_source_value,
    measurement_concept_id,
    measurement_source_value,
    unit_source_value,
    unit_source_value, -- [!#WARNING!#] THIS TARGET FIELD WAS ALREADY USED
    unit_concept_id,
    unit_concept_id, -- [!#WARNING!#] THIS TARGET FIELD WAS ALREADY USED
    range_high,
    range_low,
    measurement_type_concept_id, -- 32856 Lab
    operator_concept_id,
    value_as_concept_id,
    measurement_source_concept_id,
    provider_id,
    visit_occurrence_id,
    visit_detail_id
)
SELECT
    lab.csv.identifier AS measurement_id,

    lab.csv.patient_id AS person_id,

    lab.csv.test_date AS measurement_date,

    lab.csv.test_date AS measurement_datetime,

    lab.csv.test_date AS measurement_time,

    lab.csv.numeric_value AS value_as_number,

    lab.csv.textual_value AS value_source_value,

    lab.csv.parameter_loinc AS measurement_concept_id,

    lab.csv.parameter_name AS measurement_source_value,

    lab.csv.ucum_unit AS unit_source_value,

    lab.csv.unit AS unit_source_value,

 -- [MAPPING COMMENT] Falls nicht vorhanden, normale Unit, dann wegschmeissen 
    lab.csv.ucum_unit AS unit_concept_id,

    lab.csv.unit AS unit_concept_id,

    lab.csv.normal_values AS range_high,

    lab.csv.normal_values AS range_low,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS measurement_type_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS operator_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS value_as_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS measurement_source_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS provider_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_occurrence_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_detail_id

FROM lab.csv
;