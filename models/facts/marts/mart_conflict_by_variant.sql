{{ config(materialized='table') }}

/*
  mart_conflict_by_variant
  ------------------------
  Unit of analysis : one row per variant × therapy pair that has at least one EID
  Purpose          : surface variant-therapy combinations where the evidence base
                     actively contradicts itself — EIDs claiming SENSITIVITY alongside
                     EIDs claiming RESISTANCE, or SUPPORTS alongside DOES_NOT_SUPPORT.

  Conflict is defined at two levels:
    1. significance_conflict : same variant × therapy has both SENSITIVITY and RESISTANCE EIDs
    2. direction_conflict     : same variant × therapy has both SUPPORTS and DOES_NOT_SUPPORT EIDs

  conflict_tier (evaluated top-to-bottom):
    HARD_CONFLICT   : both significance and direction conflict present
    SIG_CONFLICT    : significance conflict only (SENSITIVITY + RESISTANCE)
    DIR_CONFLICT    : direction conflict only (SUPPORTS + DOES_NOT_SUPPORT)
    MIXED_SIGNAL    : single direction but mixed significance (e.g. sensitivity + poor_outcome)
    CLEAN           : no conflict detected

  Clinical framing:
    HARD_CONFLICT pairs are the most dangerous to act on — the literature is
    actively split on whether this variant responds to or resists this therapy.
    CLEAN pairs with high EID counts and high pct_level_a are the most trustworthy.

  Thresholds:
    min 2 EIDs per variant×therapy pair to appear in this mart
    (single-EID pairs are noise, not conflict)
*/

with bev as (
    select
        eid::int       as eid,
        variant_sk
    from {{ ref('bridge_evidence_variant') }}
),

bet as (
    select
        eid::int          as eid,
        trim(ncit_id)     as ncit_id
    from {{ ref('bridge_evidence_therapy') }}
    where ncit_id is not null
      and trim(ncit_id) <> ''
),

de as (
    select
        eid::int                        as eid,
        upper(trim(evidence_level))     as evidence_level,
        upper(trim(direction))          as direction,
        upper(trim(significance))       as significance,
        pub_year::int                   as pub_year
    from {{ ref('dim_evidence') }}
    where pub_year is not null
),

dv as (
    select
        variant_sk,
        variant_name,
        gene_symbol
    from {{ ref('dim_gene_variant') }}
),

dt as (
    select
        ncit_id,
        therapy_sk,
        therapy_name
    from {{ ref('dim_therapy') }}
),

-- join everything to variant × therapy × evidence grain
base as (
    select
        bev.variant_sk,
        bet.ncit_id,
        de.eid,
        de.evidence_level,
        de.direction,
        de.significance,
        de.pub_year
    from bev
    join bet  on bev.eid = bet.eid
    join de   on bev.eid = de.eid
),

-- rollup to variant × therapy grain
rollup as (
    select
        variant_sk,
        ncit_id,

        count(distinct eid)                                                             as total_eids,
        min(pub_year)                                                                   as first_year,
        max(pub_year)                                                                   as last_year,

        -- evidence level
        count(distinct case when evidence_level = 'A' then eid end)                    as eids_level_a,
        count(distinct case when evidence_level = 'B' then eid end)                    as eids_level_b,
        count(distinct case when evidence_level = 'C' then eid end)                    as eids_level_c,
        count(distinct case when evidence_level not in ('A','B','C')
                             and evidence_level is not null then eid end)               as eids_level_other,

        -- direction
        count(distinct case when direction = 'SUPPORTS'          then eid end)         as eids_supports,
        count(distinct case when direction = 'DOES_NOT_SUPPORT'  then eid end)         as eids_does_not_support,

        -- significance
        count(distinct case when significance = 'SENSITIVITY'    then eid end)         as eids_sensitivity,
        count(distinct case when significance = 'RESISTANCE'     then eid end)         as eids_resistance,
        count(distinct case when significance = 'POOR_OUTCOME'   then eid end)         as eids_poor_outcome,
        count(distinct case when significance = 'BETTER_OUTCOME' then eid end)         as eids_better_outcome,
        count(distinct case when significance = 'POSITIVE'       then eid end)         as eids_positive,
        count(distinct case when significance = 'NEGATIVE'       then eid end)         as eids_negative

    from base
    group by 1, 2
),

-- compute conflict flags
flagged as (
    select
        *,

        -- significance conflict: evidence claims both sensitivity AND resistance
        case when eids_sensitivity > 0 and eids_resistance > 0 then true else false end
            as has_sig_conflict,

        -- direction conflict: evidence both supports AND does not support
        case when eids_supports > 0 and eids_does_not_support > 0 then true else false end
            as has_dir_conflict,

        -- mixed significance: more than one non-zero significance category
        -- (excludes pure sensitivity or pure resistance)
        case when (
            (case when eids_sensitivity   > 0 then 1 else 0 end) +
            (case when eids_resistance    > 0 then 1 else 0 end) +
            (case when eids_poor_outcome  > 0 then 1 else 0 end) +
            (case when eids_better_outcome > 0 then 1 else 0 end) +
            (case when eids_positive      > 0 then 1 else 0 end) +
            (case when eids_negative      > 0 then 1 else 0 end)
        ) > 1 then true else false end
            as has_mixed_significance,

        -- conflict magnitude: how many EIDs are on the minority side
        -- (higher = more evenly split = more dangerous)
        least(
            coalesce(nullif(eids_sensitivity, 0), 0),
            coalesce(nullif(eids_resistance,  0), 0)
        )                                                       as sig_conflict_minority_eids,

        least(
            coalesce(nullif(eids_supports,         0), 0),
            coalesce(nullif(eids_does_not_support, 0), 0)
        )                                                       as dir_conflict_minority_eids

    from rollup
    where total_eids >= 2   -- filter noise: single-EID pairs can't conflict
),

final as (
    select
        dv.gene_symbol,
        dv.variant_name,
        f.variant_sk,
        dt.therapy_name,
        dt.therapy_sk,
        f.ncit_id,

        f.total_eids,
        f.first_year,
        f.last_year,
        (f.last_year - f.first_year + 1)                        as year_span,

        -- evidence level
        f.eids_level_a,
        f.eids_level_b,
        f.eids_level_c,
        f.eids_level_other,
        round(f.eids_level_a::numeric / nullif(f.total_eids::numeric, 0), 4)
                                                                as pct_level_a,

        -- direction
        f.eids_supports,
        f.eids_does_not_support,
        round(f.eids_supports::numeric / nullif(f.total_eids::numeric, 0), 4)
                                                                as pct_supports,

        -- significance
        f.eids_sensitivity,
        f.eids_resistance,
        f.eids_poor_outcome,
        f.eids_better_outcome,
        f.eids_positive,
        f.eids_negative,

        -- conflict flags and magnitude
        f.has_sig_conflict,
        f.has_dir_conflict,
        f.has_mixed_significance,
        f.sig_conflict_minority_eids,
        f.dir_conflict_minority_eids,

        -- combined conflict score: sum of minority sides
        -- higher = more evenly split = more clinically dangerous
        (f.sig_conflict_minority_eids + f.dir_conflict_minority_eids)
                                                                as total_conflict_score,

        -- conflict tier
        case
            when f.has_sig_conflict and f.has_dir_conflict
                then 'HARD_CONFLICT'
            when f.has_sig_conflict
                then 'SIG_CONFLICT'
            when f.has_dir_conflict
                then 'DIR_CONFLICT'
            when f.has_mixed_significance
                then 'MIXED_SIGNAL'
            else 'CLEAN'
        end                                                     as conflict_tier

    from flagged f
    left join dv on f.variant_sk = dv.variant_sk
    left join dt on f.ncit_id    = dt.ncit_id
)

select * from final
where therapy_sk is not null    -- drop orphan ncit_ids
order by
    total_conflict_score desc,
    total_eids desc,
    gene_symbol,
    variant_name
