{{ config(materialized='incremental',
          unique_key=['eid','doid'],
          incremental_strategy='merge') }}

with base as (
    select
        sd.eid::int as eid,
        sd.doid,
        sd.ingestion_run_id,
        sd.ingested_at_utc
    from {{ ref('stg_disease') }} sd
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

{% if is_incremental() %}
  and ingested_at_utc > (select coalesce(max(ingested_at_utc), '1900-01-01') from {{ this }})
{% endif %}