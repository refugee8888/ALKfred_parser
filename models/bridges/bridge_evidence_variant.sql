{{ config(
    materialized='incremental',
    unique_key=['eid','variant_sk'],
    incremental_strategy='merge'
) }}

with gv as (
  select
    eid::int as eid,
    variant_nk,
    ingestion_run_id,
    ingested_at_utc
  from {{ ref('stg_gene_variant') }}
),

mapped as (
  select
    gv.eid,
    d.variant_sk,
    gv.ingestion_run_id,
    gv.ingested_at_utc
  from gv
  join {{ ref('dim_gene_variant') }} d
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

{% if is_incremental() %}
  and ingested_at_utc >= (
    select coalesce(max(ingested_at_utc), '1900-01-01'::timestamp)
    from {{ this }}
  ) - interval '3 days'
{% endif %}