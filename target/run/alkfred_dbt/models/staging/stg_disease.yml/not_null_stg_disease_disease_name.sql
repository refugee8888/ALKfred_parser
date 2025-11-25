
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select disease_name
from "alkfred"."public"."stg_disease"
where disease_name is null



  
  
      
    ) dbt_internal_test