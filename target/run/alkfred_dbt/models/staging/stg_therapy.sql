
  create view "alkfred"."public"."stg_therapy__dbt_tmp"
    
    
  as (
    select *
from "alkfred"."public"."civic_dim_therapy"
  );