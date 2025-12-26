
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select molecular_profile_id
from "alkfred"."public"."stg_gene_variant"
where molecular_profile_id is null



  
  
      
    ) dbt_internal_test