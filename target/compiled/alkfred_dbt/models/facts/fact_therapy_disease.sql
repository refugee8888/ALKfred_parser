

with fe as (
    select
        eid::int as eid,
        doid,
        upper(trim(significance)) as significance
    from "alkfred"."public"."fact_evidence_assoc"
),

bt as (
    -- one row per (eid, ncit_id)
    select distinct
        eid::int as eid,
        trim(ncit_id) as ncit_id
    from "alkfred"."public"."bridge_evidence_therapy"
    where ncit_id is not null and trim(ncit_id) <> ''
),

bv as (
    -- one row per (eid, variant_sk)
    select distinct
        eid::int as eid,
        variant_sk
    from "alkfred"."public"."bridge_evidence_variant"
),

base_eid_therapy as (
    -- grain: (eid, ncit_id, doid) + evidence-level significance
    select distinct
        fe.eid,
        bt.ncit_id,
        fe.doid,
        fe.significance
    from fe
    join bt on bt.eid = fe.eid
),

agg_evidence as (
    select
        ncit_id,
        doid,

        count(*) filter (where significance = 'RESISTANCE')::int  as n_resistant_evidence,
        count(*) filter (where significance = 'SENSITIVITY')::int as n_sensitive_evidence,
        count(*)::int                                            as n_total_evidence
    from base_eid_therapy
    group by 1, 2
),

agg_variants as (
    select
        b.ncit_id,
        b.doid,

        count(distinct case when b.significance = 'RESISTANCE'  then v.variant_sk end)::int as n_resistant_variants,
        count(distinct case when b.significance = 'SENSITIVITY' then v.variant_sk end)::int as n_sensitive_variants
    from base_eid_therapy b
    left join bv v
      on v.eid = b.eid
    group by 1, 2
)

select
    e.ncit_id,
    e.doid,
    e.n_resistant_evidence,
    e.n_sensitive_evidence,
    e.n_total_evidence,
    v.n_resistant_variants,
    v.n_sensitive_variants,
    (e.n_resistant_evidence::double precision / nullif(e.n_total_evidence, 0)) as resistance_rate
from agg_evidence e
left join agg_variants v
  on v.ncit_id = e.ncit_id
 and v.doid    = e.doid