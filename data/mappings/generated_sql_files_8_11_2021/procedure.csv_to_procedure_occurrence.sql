
INSERT INTO procedure_occurrence
(
    procedure_occurrence_id,
    person_id,
    procedure_concept_id,
    procedure_source_value,
    procedure_date,
    procedure_datetime,
    procedure_source_concept_id,
    procedure_type_concept_id, -- 32817 EHR?
    modifier_concept_id,
    quantity,
    provider_id,
    visit_occurrence_id,
    visit_detail_id,
    modifier_source_value
)
SELECT
    procedure.csv.id AS procedure_occurrence_id,

    procedure.csv.patient_id AS person_id,

 -- [VALUE   COMMENT] FROM Procedure  WHERE Concept code = ops_code  --> maps_to SNOMED.ConceptId  
 -- [MAPPING COMMENT] FROM Procedure  WHERE Concept code = ops_code  --> maps_to SNOMED.ConceptId 
    procedure.csv.ops_code AS procedure_concept_id,

 -- [VALUE   COMMENT] FROM Procedure  WHERE Concept code = ops_code  --> maps_to SNOMED.ConceptId  
    procedure.csv.ops_code AS procedure_source_value,

    procedure.csv.execution_date AS procedure_date,

    procedure.csv.execution_date AS procedure_datetime,

    procedure.csv.ops_version AS procedure_source_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS procedure_type_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS modifier_concept_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS quantity,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS provider_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_occurrence_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS visit_detail_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS modifier_source_value

FROM procedure.csv
;