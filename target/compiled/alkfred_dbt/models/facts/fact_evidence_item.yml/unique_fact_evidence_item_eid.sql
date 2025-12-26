
    
    

select
    eid as unique_field,
    count(*) as n_records

from "alkfred"."public"."fact_evidence_item"
where eid is not null
group by eid
having count(*) > 1


