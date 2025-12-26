
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select therapy_name
from "alkfred"."public"."stg_therapy"
where therapy_name is null



  
  
      
    ) dbt_internal_test