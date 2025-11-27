
    
    

with child as (
    select doid as from_field
    from "alkfred"."public"."fact_therapy_disease"
    where doid is not null
),

parent as (
    select doid as to_field
    from "alkfred"."public"."stg_disease"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


