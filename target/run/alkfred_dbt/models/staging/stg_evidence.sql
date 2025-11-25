
  create view "alkfred"."public"."stg_evidence__dbt_tmp"
    
    
  as (
    select *
from "alkfred"."public"."civic_dim_evidence"
  );