
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    ncit_id as unique_field,
    count(*) as n_records

from "alkfred"."public"."fact_therapy_disease"
where ncit_id is not null
group by ncit_id
having count(*) > 1



  
  
      
    ) dbt_internal_test