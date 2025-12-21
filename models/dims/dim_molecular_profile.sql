{{config(materialized = 'table')}}

with src as(
    select
        molecular_profile_id, 
        eid, 
        mp_name,
        ingestion_run_id,
        ingested_at_utc

    from {{ref('stg_molecular_profile')}}
),

ranked as (
    select *,
    row_number() over (
        partition by molecular_profile_id
        order by ingested_at_utc desc, ingestion_run_id desc
    ) as rn
    from src
)

select
    molecular_profile_id, 
    eid, 
    mp_name,
    ingestion_run_id,
    ingested_at_utc
from ranked
where rn=1