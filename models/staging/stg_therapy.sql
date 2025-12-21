{{ config(materialized='view') }}

with source as (
    select
        therapy_id, 
        eid, 
        molecular_profile_id, 
        ncit_id, 
        therapy_name
    from {{ source('alkfred', 'civic_raw_therapy') }}
),

norm as (
    select
        therapy_id, 
        eid::int as eid, 
        molecular_profile_id::int as molecular_profile_id, 
        trim(ncit_id) as ncit_id, 
        therapy_name
    from source
)

select
    therapy_id, 
    eid::int as eid, 
    molecular_profile_id::int as molecular_profile_id, 
    trim(ncit_id) as ncit_id, 
    therapy_name   
from norm