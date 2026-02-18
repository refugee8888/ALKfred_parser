{{ config(materialized='table') }}

with bet as (
    select
        eid::int as eid,
        trim(ncit_id) as ncit_id
    from {{ ref('bridge_evidence_therapy') }}
    where ncit_id is not null and trim(ncit_id) <> ''
),

bev as (
    select
        eid::int as eid,
        variant_sk
    from {{ ref('bridge_evidence_variant') }}
),

therapy_eid_variant as (
    select
        bet.ncit_id,
        bet.eid,
        bev.variant_sk
    from bet
    join bev using (eid)
),

per_eid as (
    select
        ncit_id,
        eid,
        count(distinct variant_sk) as variants_on_eid
    from therapy_eid_variant
    group by 1,2
),

rollup as (
    select
        ncit_id,
        count(distinct eid) as total_eids,
        count(distinct variant_sk) as unique_variants,
        round(
            count(distinct variant_sk)::numeric / nullif(count(distinct eid)::numeric, 0),
            4
        ) as variants_per_eid,
        round(avg(variants_on_eid)::numeric, 4) as avg_variants_per_eid,
        max(variants_on_eid) as max_variants_on_single_eid
    from (
        select
            tev.ncit_id,
            tev.eid,
            tev.variant_sk,
            pe.variants_on_eid
        from therapy_eid_variant tev
        join per_eid pe
          on tev.ncit_id = pe.ncit_id
         and tev.eid = pe.eid
    ) x
    group by 1
),

top_eid as (
    select
        ncit_id,
        eid as top_eid,
        variants_on_eid as top_eid_variants,
        row_number() over (
            partition by ncit_id
            order by variants_on_eid desc, eid
        ) as rn
    from per_eid
)

select
    dt.therapy_sk,
    r.ncit_id,
    dt.therapy_name,

    r.total_eids,
    r.unique_variants,
    r.variants_per_eid,
    r.avg_variants_per_eid,
    r.max_variants_on_single_eid,

    te.top_eid,
    te.top_eid_variants,

    case
        when r.unique_variants > 0 then round(te.top_eid_variants::numeric / r.unique_variants::numeric, 4)
        else null
    end as top_eid_share,

    case
        when r.total_eids < 5 then 'LOW_SIGNAL'
        when (te.top_eid_variants::numeric / nullif(r.unique_variants::numeric, 0)) >= 0.50 then 'CONCENTRATED'
        when r.avg_variants_per_eid >= 5 then 'DENSE'
        else 'DISTRIBUTED'
    end as dispersion_label

from rollup r
join (select * from top_eid where rn = 1) te
    on r.ncit_id = te.ncit_id
join {{ ref('dim_therapy') }} dt
    on r.ncit_id = dt.ncit_id

order by top_eid_share desc nulls last, r.unique_variants desc
