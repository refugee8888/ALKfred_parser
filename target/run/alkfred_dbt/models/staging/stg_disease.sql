
  create view "alkfred"."public"."stg_disease__dbt_tmp"
    
    
  as (
    select*
from "alkfred"."public"."civic_dim_disease"
  );