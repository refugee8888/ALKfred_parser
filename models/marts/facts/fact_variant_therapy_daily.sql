{{ config (materialized = 'table') }}

with base as (

    select variant_id,
           ncit_id, 
           doid,
           created_at_utc::date as activity_date,
           significance
    from {{ ref('stg_fact_evidence') }}
    where ncit_id is not null
),
agg as (
    select
        b.variant_id,
        b.ncit_id,
        b.doid,
        b.activity_date,
        count(case when b.significance = 'RESISTANCE' then 1 end) as n_resistant,
        count(case when b.significance = 'SENSITIVITY' then 1 end) as n_sensitive,
        count(*)::int as n_total
    from base as b
    group by b.variant_id, b.ncit_id, b.doid, b.activity_date
)

select 
    agg.variant_id,
    agg.ncit_id,
    agg.doid,
    agg.activity_date,
    agg.n_resistant,
    agg.n_sensitive,
    agg.n_total,
    case 
        when agg.n_total>0
            then agg.n_resistant::double precision / agg.n_total
        else null
    end as resistance_rate
from agg 