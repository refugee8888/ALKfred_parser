

with ev as (
    select
        se.eid::int as eid,
        upper(trim(se.status)) as status,
        upper(trim(se.evidence_type)) as evidence_type,
        upper(trim(se.direction)) as direction,
        upper(trim(se.significance)) as significance,
        se.pub_year::int as pub_year,
        se.ingestion_run_id,
        se.ingested_at_utc
    from "alkfred"."public"."stg_evidence" se
),


dis as (
    select
        sd.eid::int as eid,
        sd.doid,
        sd.ingestion_run_id,
        sd.ingested_at_utc
    from "alkfred"."public"."stg_disease" sd
),


mp as (
    select
        smp.eid::int as eid,
        smp.molecular_profile_id::int as molecular_profile_id,
        smp.ingestion_run_id,
        smp.ingested_at_utc
    from "alkfred"."public"."stg_molecular_profile" smp
),

base as (
    select
        ev.eid,
        dis.doid,
        coalesce(mp.molecular_profile_id, -1) as molecular_profile_id,

        ev.direction,
        ev.status,
        ev.evidence_type,
        ev.significance,
        ev.pub_year,

        -- lineage
        greatest(
            ev.ingested_at_utc,
            dis.ingested_at_utc,
            coalesce(mp.ingested_at_utc, ev.ingested_at_utc)
        ) as ingested_at_utc,

        ev.ingestion_run_id
    from ev
    join dis on dis.eid = ev.eid
    left join mp on mp.eid = ev.eid
),

dedup as (
    select
        *,
        row_number() over (
            partition by eid, doid, molecular_profile_id
            order by ingested_at_utc desc, ingestion_run_id desc
        ) as rn
    from base
)

select
    eid,
    doid,
    molecular_profile_id,
    status,
    evidence_type,
    direction,
    significance,
    pub_year,
    ingestion_run_id,
    ingested_at_utc
from dedup
where rn = 1

