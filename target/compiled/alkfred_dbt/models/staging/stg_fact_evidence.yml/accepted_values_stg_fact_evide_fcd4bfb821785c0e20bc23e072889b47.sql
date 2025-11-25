
    
    

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


