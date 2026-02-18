{{ config(materialized='table') }}

with bev as (
    select
        eid::int as eid,
        variant_sk
    from {{ ref('bridge_evidence_variant') }}
),

bet as (
    select
        eid::int as eid,
        trim(ncit_id) as ncit_id
    from {{ ref('bridge_evidence_therapy') }}
    where ncit_id is not null and trim(ncit_id) <> ''
),

gv as (
    select
        variant_sk,
        driver_gene,
        gene_symbol,
        variant_name
    from {{ ref('dim_gene_variant') }}
),

therapy as (
    select
        therapy_sk,
        ncit_id,
        therapy_name
    from {{ ref('dim_therapy') }}
),

joined as (
    select
        bet.ncit_id,
        bev.variant_sk,
        gv.driver_gene,
        gv.gene_symbol,
        gv.variant_name,
        case
            when gv.gene_symbol like '%::%' then 'FUSION'
            when gv.variant_name is null or trim(gv.variant_name) = '' then 'OTHER'
            when gv.variant_name ilike '%exon 20%' and gv.variant_name ilike '%ins%' then 'EXON20_INS_FAMILY'
            when gv.variant_name ilike '%ins%' then 'INSERTION'
            when gv.variant_name ilike '%delins%' then 'DELINS'
            when gv.variant_name ilike '%del%' then 'DELETION'
            when gv.variant_name ilike '%dup%' then 'DUPLICATION'
            when gv.variant_name ilike '%amp%' or gv.variant_name ilike '%amplif%' or gv.variant_name ilike '%copy number%' then 'AMPLIFICATION_OR_CNV'
            when gv.variant_name ilike '%expression%' then 'EXPRESSION'
            when gv.variant_name ilike '%wild%type%' or gv.variant_name ilike 'wt' then 'WILDTYPE'
            -- simple SNV-ish patterns: contains a digit (e.g., G1202R, L858R)
            when gv.variant_name ~ '[0-9]' then 'SNV_OR_POSITIONAL'
            else 'OTHER'
        end as rule_based_variant_class
    from bet
    join bev using (eid)
    join gv using (variant_sk)
),

class_counts as (
    select
        ncit_id,
        rule_based_variant_class,
        count(distinct variant_sk) as unique_variants
    from joined
    group by 1,2
),

totals as (
    select
        ncit_id,
        sum(unique_variants) as total_unique_variants
    from class_counts
    group by 1
)

select
    t.therapy_sk,
    t.ncit_id,
    t.therapy_name,
    c.rule_based_variant_class as variant_class,
    c.unique_variants,
    round(c.unique_variants::numeric / nullif(tt.total_unique_variants::numeric, 0), 4) as variant_class_share
from class_counts c
join totals tt using (ncit_id)
join therapy t using (ncit_id)
order by tt.total_unique_variants desc, c.unique_variants desc
