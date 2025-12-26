select
  fei.eid,
  bed.doid,
  bem.molecular_profile_id,
  bev.variant_sk,
  bet.ncit_id,
  fei.direction,
  fei.significance,
  fei.pub_year
from "alkfred"."public"."fact_evidence_item" fei
left join "alkfred"."public"."bridge_evidence_disease" bed using (eid)
left join "alkfred"."public"."bridge_evidence_molecular_profile" bem using (eid)
left join "alkfred"."public"."bridge_evidence_variant" bev using (eid)
left join "alkfred"."public"."bridge_evidence_therapy" bet using (eid)