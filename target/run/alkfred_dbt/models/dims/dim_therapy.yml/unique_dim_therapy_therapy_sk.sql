
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    therapy_sk as unique_field,
    count(*) as n_records

from "alkfred"."public"."dim_therapy"
where therapy_sk is not null
group by therapy_sk
having count(*) > 1



  
  
      
    ) dbt_internal_test