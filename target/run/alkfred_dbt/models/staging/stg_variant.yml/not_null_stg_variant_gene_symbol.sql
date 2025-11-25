
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select gene_symbol
from "alkfred"."public"."stg_variant"
where gene_symbol is null



  
  
      
    ) dbt_internal_test