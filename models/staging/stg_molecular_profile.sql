{{config(materialized = 'view')}}

with source as (
    select
        molecular_profile_count, 
        molecular_profile_id, 
        eid, 
        mp_name
    from {{source('alkfred', 'civic_raw_molecular_profile')}}
),

norm as (
    select
        molecular_profile_count, 
        molecular_profile_id::int as molecular_profile_id, 
        eid::int as eid, 
        trim(mp_name) as mp_name
    from source
)

select
    molecular_profile_count, 
    molecular_profile_id, 
    eid, 
    mp_name
from norm