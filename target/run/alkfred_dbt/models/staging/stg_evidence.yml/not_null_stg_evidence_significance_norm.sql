
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select significance_norm
from "alkfred"."public"."stg_evidence"
where significance_norm is null



  
  
      
    ) dbt_internal_test