
  create view "alkfred"."public"."stg_molecular_profile__dbt_tmp"
    
    
  as (
    

with source as (
    select
        molecular_profile_count, 
        molecular_profile_id, 
        eid, 
        mp_name,
        ingestion_run_id,
        ingested_at_utc
    from "alkfred"."public"."civic_raw_molecular_profile"
),

norm as (
    select
        molecular_profile_count, 
        molecular_profile_id::int as molecular_profile_id, 
        eid::int as eid, 
        trim(mp_name) as mp_name,
        ingestion_run_id,
        ingested_at_utc
    from source
)

select
    molecular_profile_count, 
    molecular_profile_id, 
    eid, 
    mp_name,
    ingestion_run_id,
    ingested_at_utc
from norm
  );