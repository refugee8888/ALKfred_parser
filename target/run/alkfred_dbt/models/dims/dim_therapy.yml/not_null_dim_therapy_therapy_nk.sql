
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select therapy_nk
from "alkfred"."public"."dim_therapy"
where therapy_nk is null



  
  
      
    ) dbt_internal_test