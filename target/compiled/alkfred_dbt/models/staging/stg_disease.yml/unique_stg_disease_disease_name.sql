
    
    

select
    disease_name as unique_field,
    count(*) as n_records

from "alkfred"."public"."stg_disease"
where disease_name is not null
group by disease_name
having count(*) > 1


