
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    variant_sk as unique_field,
    count(*) as n_records

from "alkfred"."public"."dim_gene_variant"
where variant_sk is not null
group by variant_sk
having count(*) > 1



  
  
      
    ) dbt_internal_test