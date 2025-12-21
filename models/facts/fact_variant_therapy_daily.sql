
{{ config(materialized='table') }}

with fe as (
  select
    eid::int as eid,
    doid,
    upper(trim(significance)) as significance,
    ingested_at_utc::date as activity_date
  from fact_evidence_assoc
),

b_t as (
  select distinct eid::int as eid, trim(ncit_id) as ncit_id
  from bridge_evidence_therapy
  where ncit_id is not null and trim(ncit_id) <> ''
),

b_v as (
  select distinct eid::int as eid, variant_sk
  from bridge_evidence_variant
),

base as (
  select
    bv.variant_sk,
    bt.ncit_id,
    fe.doid,
    fe.significance,
    fe.activity_date,
    fe.eid
  from fe
  join b_t bt on bt.eid = fe.eid
  join b_v bv on bv.eid = fe.eid
)

select
  variant_sk,
  ncit_id,
  doid,
  activity_date,
  count(distinct eid) filter (where significance='RESISTANCE')::int  as n_resistant,
  count(distinct eid) filter (where significance='SENSITIVITY')::int as n_sensitive,
  count(distinct eid)::int                                          as n_total,
  (count(distinct eid) filter (where significance='RESISTANCE'))::double precision
    / nullif(count(distinct eid),0)                                 as resistance_rate
from base
group by 1,2,3,4