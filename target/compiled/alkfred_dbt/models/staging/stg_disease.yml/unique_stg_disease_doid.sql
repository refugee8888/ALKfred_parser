
    
    

select
    doid as unique_field,
    count(*) as n_records

from "alkfred"."public"."stg_disease"
where doid is not null
group by doid
having count(*) > 1


