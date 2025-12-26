
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select eid
from "alkfred"."public"."dim_evidence"
where eid is null



  
  
      
    ) dbt_internal_test