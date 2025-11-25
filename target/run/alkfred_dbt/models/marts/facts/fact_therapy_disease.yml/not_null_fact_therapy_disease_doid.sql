
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select doid
from "alkfred"."public"."fact_therapy_disease"
where doid is null



  
  
      
    ) dbt_internal_test