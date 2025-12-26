
      
  
    

  create  table "alkfred"."public"."bridge_evidence_disease__dbt_tmp"
  
  
    as
  
  (
    

with base as (
    select
        sd.eid::int as eid,
        sd.doid,
        sd.ingestion_run_id,
        sd.ingested_at_utc
    from "alkfred"."public"."stg_disease" sd
),

dedup as (
    select
      *,
      row_number() over (
        partition by eid, doid
        order by ingested_at_utc desc, ingestion_run_id desc
      ) as rn
    from base
)

select
  eid, doid,
  ingestion_run_id,
  ingested_at_utc
from dedup
where rn = 1


  );
  
  