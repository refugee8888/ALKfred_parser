
      
  
    

  create  table "alkfred"."public"."fact_evidence__dbt_tmp"
  
  
    as
  
  (
    

with base as (
    select
        se.eid::int as eid,
        sd.doid,
        smp.molecular_profile_id::int as molecular_profile_id,
        dgv.variant_sk,
        dt.ncit_id,

        upper(trim(se.direction)) as direction,
        significance,
        se.pub_year::int as pub_year,

        -- lineage
        greatest(
          se.ingested_at_utc,
          sd.ingested_at_utc,
          coalesce(smp.ingested_at_utc, se.ingested_at_utc),
          coalesce(dgv.ingested_at_utc, se.ingested_at_utc),
          coalesce(dt.ingested_at_utc, se.ingested_at_utc)
        ) as ingested_at_utc
    from "alkfred"."public"."stg_evidence" se
    join "alkfred"."public"."stg_disease" sd on sd.eid = se.eid
    left join "alkfred"."public"."stg_molecular_profile" smp on smp.eid = se.eid
    left join "alkfred"."public"."stg_gene_variant" sgv on sgv.eid = se.eid
    left join "alkfred"."public"."dim_gene_variant" dgv on dgv.variant_nk = sgv.variant_nk
    left join "alkfred"."public"."dim_therapy" dt on dt.eid = se.eid
),

dedup as (
    select
      *,
      row_number() over (
        partition by eid, doid, molecular_profile_id, variant_sk, ncit_id
        order by ingested_at_utc desc
      ) as rn
    from base
)

select
  eid, doid, molecular_profile_id, variant_sk, ncit_id,
  direction, significance, pub_year,
  ingested_at_utc
from dedup
where rn = 1


  );
  
  