
  
    

  create  table "alkfred"."public"."dim_disease__dbt_tmp"
  
  
    as
  
  (
    

with src as (
    select
        eid,
        doid,
        disease_name,
        synonyms_json,
        ingestion_run_id,
        ingested_at_utc
    from "alkfred"."public"."stg_disease"
),

ranked as (
    select
        *,
        row_number() over (
            partition by doid
            order by ingested_at_utc desc, ingestion_run_id desc
        ) as rn
    from src
)

select
    eid,
    doid,
    disease_name,
    coalesce(nullif(synonyms_json, '[]'), '[]') as synonyms_json,
    ingestion_run_id,
    ingested_at_utc
from ranked
where rn = 1
  );
  