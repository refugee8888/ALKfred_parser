
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select ncit_id as from_field
    from "alkfred"."public"."fact_therapy_disease"
    where ncit_id is not null
),

parent as (
    select ncit_id as to_field
    from "alkfred"."public"."civic_dim_therapy"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test