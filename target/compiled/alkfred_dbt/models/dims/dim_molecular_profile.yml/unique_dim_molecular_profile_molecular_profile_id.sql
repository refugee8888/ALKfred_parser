
    
    

select
    molecular_profile_id as unique_field,
    count(*) as n_records

from "alkfred"."public"."dim_molecular_profile"
where molecular_profile_id is not null
group by molecular_profile_id
having count(*) > 1


