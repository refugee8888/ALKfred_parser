
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        significance as value_field,
        count(*) as n_records

    from "alkfred"."public"."stg_fact_evidence"
    group by significance

)

select *
from all_values
where value_field not in (
    'RESISTANCE','SENSITIVITY'
)



  
  
      
    ) dbt_internal_test