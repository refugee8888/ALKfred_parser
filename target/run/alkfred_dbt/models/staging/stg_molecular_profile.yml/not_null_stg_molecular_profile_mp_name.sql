
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select mp_name
from "alkfred"."public"."stg_molecular_profile"
where mp_name is null



  
  
      
    ) dbt_internal_test