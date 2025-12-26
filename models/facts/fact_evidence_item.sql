{{ config(
    materialized='incremental',
    unique_key='eid',
    incremental_strategy='merge'
) }}

with base as (

    select
        se.eid::int as eid,

        upper(trim(se.direction)) as direction,
        
        upper(trim(se.significance)) as significance,
        se.pub_year::int as pub_year,

        se.ingestion_run_id,
        se.ingested_at_utc

    from {{ ref('stg_evidence') }} se

    {% if is_incremental() %}
      where se.ingested_at_utc >
        (select coalesce(max(ingested_at_utc), '1900-01-01') from {{ this }})
    {% endif %}
),

dedup as (
    select
        *,
        row_number() over (
          partition by eid
          order by ingested_at_utc desc, ingestion_run_id desc
        ) as rn
    from base
)

select
    eid,
    direction,
    significance,
    pub_year,
    ingestion_run_id,
    ingested_at_utc
from dedup
where rn = 1