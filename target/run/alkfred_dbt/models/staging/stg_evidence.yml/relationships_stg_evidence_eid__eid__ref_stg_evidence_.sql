
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select eid as from_field
    from "alkfred"."public"."stg_evidence"
    where eid is not null
),

parent as (
    select eid as to_field
    from "alkfred"."public"."stg_evidence"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test