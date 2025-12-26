
    
    

select
    therapy_nk as unique_field,
    count(*) as n_records

from "alkfred"."public"."dim_therapy"
where therapy_nk is not null
group by therapy_nk
having count(*) > 1


