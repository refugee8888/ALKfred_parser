{{ config(materialized='incremental',
          unique_key=['eid','ncit_id'],
          incremental_strategy='merge') }}

with base as (
  select
    st.eid::int as eid,
    trim(st.ncit_id) as ncit_id,
    st.ingestion_run_id,
    st.ingested_at_utc
  from {{ ref('stg_therapy') }} st
  where st.ncit_id is not null and trim(st.ncit_id) <> ''
),

dedup as (
  select
    *,
    row_number() over (
      partition by eid, ncit_id
      order by ingested_at_utc desc, ingestion_run_id desc
    ) as rn
  from base
)

select
  eid, ncit_id,
  ingestion_run_id,
  ingested_at_utc
from dedup
where rn = 1

{% if is_incremental() %}
  and ingested_at_utc > (select coalesce(max(ingested_at_utc), '1900-01-01') from {{ this }})
{% endif %}