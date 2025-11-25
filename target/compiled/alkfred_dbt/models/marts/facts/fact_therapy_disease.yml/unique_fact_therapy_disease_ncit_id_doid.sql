
    
    

select
    ncit_id || '-' || doid as unique_field,
    count(*) as n_records

from "alkfred"."public"."fact_therapy_disease"
where ncit_id || '-' || doid is not null
group by ncit_id || '-' || doid
having count(*) > 1


