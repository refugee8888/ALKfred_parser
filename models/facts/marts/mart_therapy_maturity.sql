{{ config(materialized='table') }}

with bet as (
    -- bridge_evidence_therapy: (eid, ncit_id)
    select
        eid::int as eid,
        trim(ncit_id) as ncit_id
    from {{ ref('bridge_evidence_therapy') }}
    where ncit_id is not null and trim(ncit_id) <> ''
),

de as (
    -- dim_evidence: latest per eid
    select
        eid::int as eid,
        pub_year::int as pub_year
    from {{ ref('dim_evidence') }}
    where pub_year is not null
),

tey as (
    -- therapy-evidence-year
    select
        bet.ncit_id,
        de.pub_year,
        bet.eid
    from bet
    join de using (eid)
),

therapy_year_counts as (
    select
        ncit_id,
        pub_year,
        count(distinct eid) as eids_in_year
    from tey
    group by 1,2
),

therapy_rollup as (
    select
        ncit_id,
        count(distinct eid) as total_eids,
        min(pub_year) as first_year,
        max(pub_year) as last_year
    from tey
    group by 1
),

peak as (
    select
        ncit_id,
        pub_year as peak_year,
        eids_in_year as peak_year_eids,
        row_number() over (
            partition by ncit_id
            order by eids_in_year desc, pub_year desc
        ) as rn
    from therapy_year_counts
),

-- unique variants per therapy (via eid join)
therapy_unique_variants as (
    select
        bet.ncit_id,
        count(distinct bev.variant_sk) as unique_variants
    from bet
    join {{ ref('bridge_evidence_variant') }} bev
        on bet.eid = bev.eid
    group by 1
)

select
    dt.therapy_sk,
    dt.ncit_id,
    dt.therapy_name,

    tr.total_eids,
    tuv.unique_variants,

    tr.first_year,
    tr.last_year,
    (tr.last_year - tr.first_year + 1) as year_span,

    p.peak_year,
    p.peak_year_eids,

    case
        when tr.total_eids > 0 then round(p.peak_year_eids::numeric / tr.total_eids::numeric, 4)
        else null
    end as peak_year_share,

    case
        when tr.total_eids < 5 then 'LOW_SIGNAL'
        when (tr.last_year - tr.first_year + 1) <= 1 then 'RECENT_BURST_OR_SINGLE_YEAR'
        when (p.peak_year_eids::numeric / nullif(tr.total_eids::numeric, 0)) >= 0.70 then 'RECENT_BURST_OR_SINGLE_YEAR'
        when tr.total_eids >= 30 and (p.peak_year_eids::numeric / nullif(tr.total_eids::numeric, 0)) <= 0.35 then 'MATURE_DISTRIBUTED'
        else 'MID_SIGNAL'
    end as maturity_label

from therapy_rollup tr
join (select * from peak where rn = 1) p
    on tr.ncit_id = p.ncit_id
left join therapy_unique_variants tuv
    on tr.ncit_id = tuv.ncit_id
join {{ ref('dim_therapy') }} dt
    on tr.ncit_id = dt.ncit_id

order by tr.total_eids desc, year_span desc
