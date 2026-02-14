{{ config(materialized="table") }}

with src as (
    select
        eid,
        direction,
        significance,
        pmids_json,
        evidence_level,
        evidence_type,
        rating,
        status,
        pub_year,
        description,
        ingestion_run_id,
        ingested_at_utc
    from {{ ref("stg_evidence") }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by eid
            order by ingested_at_utc desc, ingestion_run_id desc
        ) as rn
    from src
)

select
    eid,
    direction,
    significance,
    evidence_level,
    evidence_type,
    rating,
    status,
    coalesce(nullif(pmids_json, '[]'), '[]') as pmids_json,
    pub_year,
    description,
    ingestion_run_id,
    ingested_at_utc
from ranked
where rn = 1