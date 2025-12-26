

with source as (
    select
        disease_count,
        eid,
        doid,
        disease_name,
        synonyms_json,
        ingestion_run_id,
        ingested_at_utc
    from "alkfred"."public"."civic_raw_disease"
),

norm as (
    select
        disease_count,
        eid::int as eid,
        upper(trim(doid)) as doid_raw_norm,
        nullif(trim(disease_name), '') as disease_name,
        synonyms_json,
        ingestion_run_id,
        ingested_at_utc
    from source
)

select
    disease_count,
    eid,
    case
        when doid_raw_norm like 'DOID:%' then doid_raw_norm
        when doid_raw_norm is null or doid_raw_norm = '' then null
        else 'DOID:' || doid_raw_norm
    end as doid,
    disease_name,
    synonyms_json,
    ingestion_run_id,
    ingested_at_utc
from norm