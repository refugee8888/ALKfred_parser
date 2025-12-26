
    
    

select
    significance as unique_field,
    count(*) as n_records

from "alkfred"."public"."stg_evidence"
where significance is not null
group by significance
having count(*) > 1


