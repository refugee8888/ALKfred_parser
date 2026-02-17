

with src as(
    select 
        therapy_nk,
        eid, 
        molecular_profile_id, 
        ncit_id, 
        therapy_name,
        ingestion_run_id,
        ingested_at_utc

    from "alkfred"."public"."stg_therapy"
),

ranked as (
    select *,
    row_number() over (
        partition by therapy_nk
        order by ingested_at_utc desc, ingestion_run_id desc
    ) as rn
    from src
)

select
    md5(therapy_nk) as therapy_sk,
    therapy_nk,
    -- eid, 
    -- molecular_profile_id, 
    ncit_id, 
    therapy_name,
    ingestion_run_id,
    ingested_at_utc
from ranked
where rn=1