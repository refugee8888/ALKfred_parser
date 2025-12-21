

with source as (
    select
        evidence_count,
        eid,
        direction,
        significance,
        evidence_level,
        evidence_type,
        rating,
        status,
        pmids_json,
        pub_year,
        description,
        ingestion_run_id,
        ingested_at_utc
    from "alkfred"."public"."civic_raw_evidence"
),

norm as (
    select
        evidence_count,
        eid::int as eid,
        direction,
        upper(trim(significance)) as significance,
        evidence_level,
        evidence_type,
        rating,
        status,
        pmids_json,
        pub_year,
        description,
        ingestion_run_id,
        ingested_at_utc
    from source
)

select
    evidence_count,
    eid,
    direction,
    significance,
    evidence_level,
    evidence_type,
    rating,
    status,
    pmids_json,
    pub_year,
    description,
    ingestion_run_id,
    ingested_at_utc
    
from norm