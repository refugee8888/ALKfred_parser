
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select variant_id
from "alkfred"."public"."stg_variant"
where variant_id is null



  
  
      
    ) dbt_internal_test