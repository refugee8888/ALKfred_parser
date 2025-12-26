
    
    

select
    therapy_sk as unique_field,
    count(*) as n_records

from "alkfred"."public"."dim_therapy"
where therapy_sk is not null
group by therapy_sk
having count(*) > 1


