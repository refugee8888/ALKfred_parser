
  create view "alkfred"."public"."stg_variant__dbt_tmp"
    
    
  as (
    select *
from "alkfred"."public"."civic_dim_gene_variant"
  );