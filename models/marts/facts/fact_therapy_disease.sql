{{config(
		materialized = 'table'
)}}

with base as (
    select
        ncit_id,
        doid,
        variant_id,
        significance
    from {{ ref('stg_fact_evidence') }}
    where ncit_id is not null
),

agg as (
    select
        b.ncit_id,
        b.doid,

        -- evidence counts
        count(case when b.significance = 'RESISTANCE'  then 1 end)::int as n_resistant_evidence,
        count(case when b.significance = 'SENSITIVITY' then 1 end)::int as n_sensitive_evidence,
        count(*)::int                                      as n_total_evidence,

        -- distinct variant counts
        count(distinct case when b.significance = 'RESISTANCE'
                            then b.variant_id end)::int   as n_resistant_variants,
        count(distinct case when b.significance = 'SENSITIVITY'
                            then b.variant_id end)::int   as n_sensitive_variants
    from base as b
    group by
        b.ncit_id,
        b.doid
)

select
    agg.ncit_id,
    agg.doid,
    agg.n_resistant_evidence,
    agg.n_sensitive_evidence,
    agg.n_total_evidence,
    agg.n_resistant_variants,
    agg.n_sensitive_variants,
    case
        when agg.n_total_evidence > 0
            then agg.n_resistant_evidence::double precision
                 / nullif(agg.n_total_evidence, 0)
        else null
    end as resistance_rate
from agg
