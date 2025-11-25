
  create view "alkfred"."public"."stg_molecular_profile__dbt_tmp"
    
    
  as (
    select *
from "alkfred"."public"."civic_dim_molecular_profile"
  );