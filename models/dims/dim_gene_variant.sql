with src as (
  select *
  from {{ ref('stg_gene_variant') }}
),

ranked as (
  select
    *,
    row_number() over (
      partition by variant_nk
      order by ingested_at_utc desc, ingestion_run_id desc
    ) as rn
  from src
)

select
  md5(variant_nk) as variant_sk,
  variant_nk,
  molecular_profile_id,
  civic_ca_id,
  gene_symbol,
  variant_name,
  ingested_at_utc,
  ingestion_run_id
from ranked
where rn = 1