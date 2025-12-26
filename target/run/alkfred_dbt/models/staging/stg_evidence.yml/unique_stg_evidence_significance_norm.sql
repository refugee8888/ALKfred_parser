
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    significance_norm as unique_field,
    count(*) as n_records

from "alkfred"."public"."stg_evidence"
where significance_norm is not null
group by significance_norm
having count(*) > 1



  
  
      
    ) dbt_internal_test