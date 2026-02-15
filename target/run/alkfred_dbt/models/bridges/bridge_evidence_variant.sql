
      
  
    

  create  table "alkfred"."public"."bridge_evidence_variant"
  
  
    as
  
  (
    

with gv as (
  select
    eid::int as eid,
    variant_nk,
    ingestion_run_id,
    ingested_at_utc::timestamp as ingested_at_utc
  from "alkfred"."public"."stg_gene_variant"
),

mapped as (
  select
    gv.eid,
    d.variant_sk,
    gv.ingestion_run_id,
    gv.ingested_at_utc
  from gv
  join "alkfred"."public"."dim_gene_variant" d
    on d.variant_nk = gv.variant_nk
),

dedup as (
  select
    *,
    row_number() over (
      partition by eid, variant_sk
      order by ingested_at_utc desc, ingestion_run_id desc
    ) as rn
  from mapped
)

select
  eid,
  variant_sk,
  ingestion_run_id,
  ingested_at_utc
from dedup
where rn = 1


  );
  
  