
INSERT INTO location
(
    city,
    location_source_value,
    location_source_value, -- [!#WARNING!#] THIS TARGET FIELD WAS ALREADY USED
    zip,
    location_id, -- Autogenerate, zurückspiegeln in person
    address_1,
    address_2,
    county,
    state
)
SELECT
    person.csv.city AS city,

    person.csv.city AS location_source_value,

    person.csv.zip AS location_source_value,

    person.csv.zip AS zip,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS location_id,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS address_1,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS address_2,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS county,

 -- [!WARNING!] no source column found. See possible comment at the INSERT INTO
    NULL AS state

FROM person.csv
;