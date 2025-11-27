
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    disease_name_norm as unique_field,
    count(*) as n_records

from "alkfred"."public"."stg_disease"
where disease_name_norm is not null
group by disease_name_norm
having count(*) > 1



  
  
      
    ) dbt_internal_test