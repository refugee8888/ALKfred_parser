{{ config(materialized='table') }}

/*
  mart_therapy_maturity
  ---------------------
  Unit of analysis : one row per therapy (ncit_id / therapy_sk)
  Maturity labels  : based on volume, temporal distribution, and peak concentration
  Thresholds (empirical, document if changed):
    LOW_SIGNAL               : total_eids < 5
    STALE_SINGLE_YEAR        : year_span <= 1 AND last_year < 2015  (abandoned burst)
    RECENT_BURST_OR_SINGLE_YEAR : year_span <= 1 AND last_year >= 2015
                               OR peak_year_share >= 0.70 (single-year dominance)
    MATURE_DISTRIBUTED       : total_eids >= 30
                               AND year_span >= 3
                               AND peak_year_share <= 0.35
    MID_SIGNAL               : everything else
  Conflict score: count of EIDs where both SUPPORTS and DOES_NOT_SUPPORT exist
                  for the same therapy — higher = more contested evidence base.
*/

with bet as (
    select
        eid::int    as eid,
        trim(ncit_id) as ncit_id
    from {{ ref('bridge_evidence_therapy') }}
    where ncit_id is not null
      and trim(ncit_id) <> ''
),

de as (
    select
        eid::int                        as eid,
        pub_year::int                   as pub_year,
        upper(trim(evidence_level))     as evidence_level,
        upper(trim(direction))          as direction,
        upper(trim(significance))       as significance
    from {{ ref('dim_evidence') }}
    where pub_year is not null
),

tey as (
    -- therapy × evidence × year base
    select
        bet.ncit_id,
        bet.eid,
        de.pub_year,
        de.evidence_level,
        de.direction,
        de.significance
    from bet
    join de using (eid)
),

therapy_year_counts as (
    select
        ncit_id,
        pub_year,
        count(distinct eid) as eids_in_year
    from tey
    group by 1, 2
),

peak as (
    select
        ncit_id,
        pub_year        as peak_year,
        eids_in_year    as peak_year_eids,
        row_number() over (
            partition by ncit_id
            order by eids_in_year desc, pub_year desc
        ) as rn
    from therapy_year_counts
),

therapy_unique_variants as (
    select
        bet.ncit_id,
        count(distinct bev.variant_sk) as unique_variants
    from bet
    join {{ ref('bridge_evidence_variant') }} bev
        on bet.eid = bev.eid
    group by 1
),

-- direction conflict: therapies where the same eid set contains both
-- SUPPORTS and DOES_NOT_SUPPORT — proxy for contested evidence
direction_by_therapy as (
    select
        ncit_id,
        eid,
        max(case when direction = 'SUPPORTS'          then 1 else 0 end) as has_supports,
        max(case when direction = 'DOES_NOT_SUPPORT'  then 1 else 0 end) as has_does_not_support
    from tey
    group by 1, 2
),

conflict as (
    select
        ncit_id,
        -- EIDs that individually carry a contradicting direction tag are rare;
        -- more meaningful: how many EIDs exist alongside at least one opposing EID
        -- for the same therapy. We count EIDs in therapies where both directions appear.
        sum(has_supports)           as supporting_eids,
        sum(has_does_not_support)   as opposing_eids,
        case
            when sum(has_supports) > 0 and sum(has_does_not_support) > 0
            then least(sum(has_supports), sum(has_does_not_support))
            else 0
        end as conflict_score
    from direction_by_therapy
    group by 1
),

therapy_rollup as (
    select
        ncit_id,

        -- volume
        count(distinct eid)                                                         as total_eids,

        -- temporal
        min(pub_year)                                                               as first_year,
        max(pub_year)                                                               as last_year,

        -- evidence level breakdown
        count(distinct case when evidence_level = 'A' then eid end)                as eids_level_a,
        count(distinct case when evidence_level = 'B' then eid end)                as eids_level_b,
        count(distinct case when evidence_level = 'C' then eid end)                as eids_level_c,
        count(distinct case when evidence_level not in ('A','B','C')
                             and evidence_level is not null then eid end)           as eids_level_other,

        -- direction breakdown
        count(distinct case when direction = 'SUPPORTS'         then eid end)      as eids_supports,
        count(distinct case when direction = 'DOES_NOT_SUPPORT' then eid end)      as eids_does_not_support,

        -- significance breakdown
        count(distinct case when significance = 'SENSITIVITY'   then eid end)      as eids_sensitivity,
        count(distinct case when significance = 'RESISTANCE'    then eid end)      as eids_resistance,
        count(distinct case when significance = 'POOR_OUTCOME'  then eid end)      as eids_poor_outcome,
        count(distinct case when significance = 'BETTER_OUTCOME' then eid end)     as eids_better_outcome,
        count(distinct case when significance = 'POSITIVE'      then eid end)      as eids_positive,
        count(distinct case when significance = 'NEGATIVE'      then eid end)      as eids_negative,
        count(distinct case when significance not in (
            'SENSITIVITY','RESISTANCE','POOR_OUTCOME',
            'BETTER_OUTCOME','POSITIVE','NEGATIVE'
        ) and significance is not null then eid end)                                as eids_significance_other

    from tey
    group by 1
),

final as (
    select
        dt.therapy_sk,
        dt.ncit_id,
        dt.therapy_name,

        -- volume
        tr.total_eids,
        coalesce(tuv.unique_variants, 0)                                    as unique_variants,

        -- temporal
        tr.first_year,
        tr.last_year,
        (tr.last_year - tr.first_year + 1)                                  as year_span,

        -- peak
        p.peak_year,
        p.peak_year_eids,
        round(
            p.peak_year_eids::numeric / nullif(tr.total_eids::numeric, 0),
            4
        )                                                                   as peak_year_share,

        -- evidence level
        tr.eids_level_a,
        tr.eids_level_b,
        tr.eids_level_c,
        tr.eids_level_other,
        round(
            tr.eids_level_a::numeric / nullif(tr.total_eids::numeric, 0),
            4
        )                                                                   as pct_level_a,

        -- direction
        tr.eids_supports,
        tr.eids_does_not_support,
        round(
            tr.eids_supports::numeric / nullif(tr.total_eids::numeric, 0),
            4
        )                                                                   as pct_supports,

        -- significance
        tr.eids_sensitivity,
        tr.eids_resistance,
        tr.eids_poor_outcome,
        tr.eids_better_outcome,
        tr.eids_positive,
        tr.eids_negative,
        tr.eids_significance_other,

        -- conflict
        coalesce(c.supporting_eids, 0)                                      as conflict_supporting_eids,
        coalesce(c.opposing_eids, 0)                                        as conflict_opposing_eids,
        coalesce(c.conflict_score, 0)                                       as conflict_score,

        -- maturity label
        -- evaluated top-to-bottom; first match wins
        case
            when tr.total_eids < 5
                then 'LOW_SIGNAL'

            when (tr.last_year - tr.first_year + 1) <= 1
                 and tr.last_year < 2015
                then 'STALE_SINGLE_YEAR'

            when (tr.last_year - tr.first_year + 1) <= 1
                 and tr.last_year >= 2015
                then 'RECENT_BURST_OR_SINGLE_YEAR'

            when (p.peak_year_eids::numeric / nullif(tr.total_eids::numeric, 0)) >= 0.70
                then 'RECENT_BURST_OR_SINGLE_YEAR'

            when tr.total_eids >= 30
                 and (tr.last_year - tr.first_year + 1) >= 3
                 and (p.peak_year_eids::numeric / nullif(tr.total_eids::numeric, 0)) <= 0.35
                then 'MATURE_DISTRIBUTED'

            else 'MID_SIGNAL'
        end                                                                 as maturity_label

    from therapy_rollup tr
    join (select * from peak where rn = 1) p
        on tr.ncit_id = p.ncit_id
    left join therapy_unique_variants tuv
        on tr.ncit_id = tuv.ncit_id
    left join {{ ref('dim_therapy') }} dt        -- left join: surface orphan ncit_ids
        on tr.ncit_id = dt.ncit_id
    left join conflict c
        on tr.ncit_id = c.ncit_id
)

select * from final
where therapy_sk is not null          -- log orphan ncit_ids separately if needed
order by total_eids desc, year_span desc