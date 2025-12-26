
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select therapy_sk
from "alkfred"."public"."dim_therapy"
where therapy_sk is null



  
  
      
    ) dbt_internal_test