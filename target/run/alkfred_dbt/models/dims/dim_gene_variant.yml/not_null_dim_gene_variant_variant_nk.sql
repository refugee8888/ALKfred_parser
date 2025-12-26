
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select variant_nk
from "alkfred"."public"."dim_gene_variant"
where variant_nk is null



  
  
      
    ) dbt_internal_test