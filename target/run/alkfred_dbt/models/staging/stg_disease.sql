
  create view "alkfred"."public"."stg_disease__dbt_tmp"
    
    
  as (
    

with source as (
    select
        disease_count,
        eid,
        doid,
        disease_name,
        synonyms_json
    from "alkfred"."public"."civic_raw_disease"
),

norm as (
    select
        disease_count,
        eid::int as eid,
        upper(trim(doid)) as doid_raw_norm,
        nullif(trim(disease_name), '') as disease_name,
        synonyms_json
    from source
)

select
    disease_count,
    eid,
    case
        when doid_raw_norm like 'DOID:%' then doid_raw_norm
        when doid_raw_norm is null or doid_raw_norm = '' then null
        else 'DOID:' || doid_raw_norm
    end as doid,
    disease_name,
    synonyms_json
from norm
  );