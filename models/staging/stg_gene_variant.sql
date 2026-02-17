{{ config(materialized='view') }}

with source as (
    select
        variant_id,
        eid,
        molecular_profile_id,
        civic_ca_id,
        gene_symbol,
        variant_name,
        ingestion_run_id,
        ingested_at_utc
    from {{ source('alkfred', 'civic_raw_gene_variant') }}
),

prep as (
    select
        variant_id,
        eid::int as eid,
        molecular_profile_id::int as molecular_profile_id,
        nullif(trim(civic_ca_id), '') as civic_ca_id,
        nullif(trim(gene_symbol), '') as gene_symbol,
        nullif(trim(variant_name), '') as variant_name,
        ingestion_run_id,
        ingested_at_utc
    from source
),

split as (
    select
        *,
        case
            when gene_symbol like '%::%' then regexp_split_to_array(gene_symbol, '::')
            else null
        end as gene_parts
    from prep
),

norm as (
    select
        variant_id,

        case
            when civic_ca_id is not null then civic_ca_id
            else 'NOCA|' || coalesce(gene_symbol, '?') || '|' || coalesce(variant_name, '?')
        end as variant_nk,

        eid,
        molecular_profile_id,
        civic_ca_id,
        gene_symbol,
        variant_name,

        /* driver_gene rules:
           - if gene_symbol contains '::' then pick side that matches driver list
           - prefer RIGHT side if it matches
           - else LEFT side if it matches
           - else fall back to gene_symbol
        */
        case
            when gene_symbol like '%::%' and gene_parts is not null then
                case
                    when (gene_parts[array_length(gene_parts, 1)]) in ('ALK','ROS1','RET','NTRK1','NTRK2','NTRK3','EGFR','TFCP2')
                        then (gene_parts[array_length(gene_parts, 1)])
                    when (gene_parts[1]) in ('ALK','ROS1','RET','NTRK1','NTRK2','NTRK3','EGFR','TFCP2')
                        then (gene_parts[1])
                    else gene_symbol
                end
            else gene_symbol
        end as driver_gene,

        ingestion_run_id,
        ingested_at_utc
    from split
)

select
    variant_id,
    variant_nk,
    eid,
    molecular_profile_id,
    civic_ca_id,
    driver_gene,
    gene_symbol,
    variant_name,
    ingestion_run_id,
    ingested_at_utc
from norm
