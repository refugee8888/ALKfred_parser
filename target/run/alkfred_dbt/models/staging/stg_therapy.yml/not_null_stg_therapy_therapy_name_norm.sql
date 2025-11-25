
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select therapy_name_norm
from "alkfred"."public"."stg_therapy"
where therapy_name_norm is null



  
  
      
    ) dbt_internal_test