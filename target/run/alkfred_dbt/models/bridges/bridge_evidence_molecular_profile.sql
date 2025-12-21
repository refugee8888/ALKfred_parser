
      
  
    

  create  table "alkfred"."public"."bridge_evidence_molecular_profile__dbt_tmp"
  
  
    as
  
  (
    

with base as (
    select
        smp.eid::int as eid,
        smp.molecular_profile_id::int as molecular_profile_id,
        smp.ingestion_run_id,
        smp.ingested_at_utc
    from "alkfred"."public"."stg_molecular_profile" smp
    where smp.molecular_profile_id is not null
),

dedup as (
    select
      *,
      row_number() over (
        partition by eid, molecular_profile_id
        order by ingested_at_utc desc, ingestion_run_id desc
      ) as rn
    from base
)

select
  eid, molecular_profile_id,
  ingestion_run_id,
  ingested_at_utc
from dedup
where rn = 1


  );
  
  