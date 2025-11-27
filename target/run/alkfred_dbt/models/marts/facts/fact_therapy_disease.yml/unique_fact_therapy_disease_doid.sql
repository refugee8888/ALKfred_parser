
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    doid as unique_field,
    count(*) as n_records

from "alkfred"."public"."fact_therapy_disease"
where doid is not null
group by doid
having count(*) > 1



  
  
      
    ) dbt_internal_test