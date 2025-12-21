{{ config(materialized='view') }}

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
        created_at_utc,
        updated_at_utc
    from {{ source('alkfred', 'civic_raw_evidence') }}
),

norm as (
    select
        evidence_count,
        eid::int as eid,
        upper(trim(significance)) as significance_norm,
        evidence_level,
        evidence_type,
        rating,
        status,
        pmids_json,
        pub_year,
        description,
        created_at_utc::timestamp as created_at_utc,
        updated_at_utc::timestamp as updated_at_utc
    from source
)

select
    evidence_count,
    eid,
    significance_norm,
    evidence_level,
    evidence_type,
    rating,
    status,
    pmids_json,
    pub_year,
    description,
    created_at_utc,
    updated_at_utc
    
from norm