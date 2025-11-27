
    
    

select
    ncit_id as unique_field,
    count(*) as n_records

from "alkfred"."public"."fact_therapy_disease"
where ncit_id is not null
group by ncit_id
having count(*) > 1


