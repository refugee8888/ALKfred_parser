
  create view "alkfred"."public"."stg_gene_variant__dbt_tmp"
    
    
  as (
    

with source as(
    select
        variant_id,
        eid,
        molecular_profile_id,
        civic_ca_id,
        gene_symbol,
        variant_name
    from "alkfred"."public"."civic_raw_gene_variant"
),

norm as(
    select
        variant_id,
        eid::int as eid,
        molecular_profile_id::int as molecular_profile_id,
        trim(civic_ca_id) as civic_ca_id,
        trim(gene_symbol) as gene_symbol,
        trim(variant_name) as variant_name
    from source
)

select
    variant_id,
    eid,
    molecular_profile_id,
    civic_ca_id,
    gene_symbol,
    variant_name
from norm
  );