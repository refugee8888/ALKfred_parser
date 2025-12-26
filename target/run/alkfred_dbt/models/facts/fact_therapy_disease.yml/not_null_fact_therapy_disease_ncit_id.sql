
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select ncit_id
from "alkfred"."public"."fact_therapy_disease"
where ncit_id is null



  
  
      
    ) dbt_internal_test