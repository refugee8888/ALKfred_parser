{{ config(materialized='view') }}

with base as (
  select
    t.therapy_name,
    t.therapy_sk,
    e.eid,
    v.variant_sk
  from {{ ref('fact_evidence_assoc') }} e
  join {{ ref('bridge_evidence_therapy') }} bt on e.eid = bt.eid
  join {{ ref('dim_therapy') }} t on bt.ncit_id = t.ncit_id
  join {{ ref('bridge_evidence_variant') }} bv on e.eid = bv.eid
  join {{ ref('dim_gene_variant') }} v on bv.variant_sk = v.variant_sk
  where 1=1
    and e.status = 'ACCEPTED'
    and e.significance = 'SENSITIVITY'
    and e.evidence_type = 'PREDICTIVE'
    and e.doid in ('DOID:3908','DOID:3910','DOID:7474','DOID:162')
)

select
  therapy_name,
  therapy_sk,
  count(distinct variant_sk) as variants,
  count(distinct eid) as eids,
  (count(distinct variant_sk)::numeric / nullif(count(distinct eid),0)) as diversity_density
from base
group by 1,2
order by diversity_density desc
