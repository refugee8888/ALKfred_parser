
  create view "alkfred"."public"."stg_fact_evidence__dbt_tmp"
    
    
  as (
    select *
from "alkfred"."public"."fact_evidence"
  );