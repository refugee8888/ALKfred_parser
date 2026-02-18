# ALKfred

### Open Oncology Data Warehouse · Postgres · dbt-core · Prefect

**ALKfred** is an open-source oncology analytics warehouse focused on
variant--therapy evidence.
It ingests raw evidence from the **CIViC** knowledgebase, stores it in
**Postgres**, and uses **dbt-core** to build a tested star-schema
analytics layer for research and clinical analytics-style exploration.

ALKfred is designed as a **real-world data engineering project**,
emphasizing:

-   clear grains
-   explicit bridges
-   reproducible transformations
-   auditability over "magic" logic

------------------------------------------------------------------------

## What ALKfred Does

-   Pulls raw CIViC evidence via GraphQL (paginated)
-   Persists a raw JSON snapshot for replayability
-   Loads raw tables into Postgres (Python loaders)
-   Uses **dbt** to:
    -   define grains
    -   enforce constraints/tests
    -   build dimensions, bridges, and facts
    -   produce analyst/clinician-friendly marts



------------------------------------------------------------------------

## Architecture Overview

      CIViC GraphQL API
               ↓
    ┌────────────────────┐
    │ Raw JSON ingestion │  (Python)
    └────────────────────┘
               ↓
     Postgres raw tables (civic_raw_*)
               ↓
    ┌────────────────────┐
    │     dbt-core       │
    │  (stg → dim →      │
    │   bridge → fact)   │
    └────────────────────┘
               ↓
     Analytics-ready facts + marts



Python ingests raw data. dbt builds models. Postgres stores clean data.

------------------------------------------------------------------------

## Features

### Ingestion (Python)

-   CIViC GraphQL pagination
-   Deterministic raw extraction
-   Raw JSON persisted for replayability
-   Minimal logic by design

Python **does not** build analytics tables.

------------------------------------------------------------------------

### Warehouse (Postgres)

-   Explicit star schema via dbt models
-   Clear separation of:
    -   raw sources (`civic_raw_*`)
    -   staging (`stg_*`)
    -   dimensions (`dim_*`)
    -   bridges (`bridge_*`)
    -   facts/marts (`fact_*`, `mart_*`)

------------------------------------------------------------------------

### Transformation & Analytics (dbt-core)

-   Full dbt project
-   Schema + relationship tests
-   Staging models normalize raw inputs
-   Dimensions deduplicated with deterministic keys
-   Bridges handle multi-valued relationships
-   Facts built **only from bridges + dimensions**

#### Key analytics layer (facts)

-   `fact_evidence_assoc`
    Canonical evidence grain (EID-level, bridge-resolved)

    **First 10 rows (sample):**
    ```text    
    "eid"	"doid"	"molecular_profile_id"	"status"	"evidence_type"	"direction"	"significance"	"pub_year"	"ingestion_run_id"	"ingested_at_utc"
    32	"DOID:0050905"	8	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"RESISTANCE"	2010	"f1fca942-d156-4ad6-b1ed-6002c76b0e33"	"2026-02-18T08:16:09Z"
    33	"DOID:3908"	8	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"RESISTANCE"	2010	"eaee8028-b561-44b6-bebd-71c0b6da7d50"	"2026-02-18T08:16:09Z"
    37	"DOID:769"	8	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"SENSITIVITY"	2011	"c2f6a2f3-5414-48c5-b4a0-5b87744964ef"	"2026-02-18T08:16:09Z"
    38	"DOID:769"	8	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"SENSITIVITY"	2011	"d8e90218-8672-4e62-a428-c1f9b4d1c2fb"	"2026-02-18T08:16:09Z"
    39	"DOID:162"	9	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"SENSITIVITY"	2008	"f0b60567-b2a5-4a52-91e2-70176b693fa9"	"2026-02-18T08:16:09Z"
    48	"DOID:769"	9	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"RESISTANCE"	2008	"ef5da051-33fe-4ecb-8717-46a8527cc55c"	"2026-02-18T08:16:09Z"
    125	"DOID:769"	8	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"RESISTANCE"	2011	"f38b43d1-d80b-43c3-bef1-c8da10911907"	"2026-02-18T08:16:09Z"
    141	"DOID:3908"	4230	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"SENSITIVITY"	2011	"b32ee1bb-4023-4c99-bb32-3dafb9ed7334"	"2026-02-18T08:16:09Z"
    142	"DOID:769"	8	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"SENSITIVITY"	2008	"bb7b7dc8-8499-44c2-b4ab-e98b461c5bbd"	"2026-02-18T08:16:09Z"
    143	"DOID:769"	9	"ACCEPTED"	"PREDICTIVE"	"SUPPORTS"	"SENSITIVITY"	2011	"f0f6e72f-480e-4ca0-9d85-94c7b19a3d3c"	"2026-02-18T08:16:09Z"
   ``` 

-   `fact_therapy_disease`
    Therapy × Disease aggregates (e.g., resistance vs sensitivity
    coverage)
    
    **First 10 rows (sample):**
    ```text 
    "ncit_id"	"doid"	"n_resistant_evidence"	"n_sensitive_evidence"	"n_total_evidence"	"n_resistant_variants"	"n_sensitive_variants"	"resistance_rate"
    "C101790"	"DOID:162"	2	0	2	4	0	1
    "C101790"	"DOID:3260"	0	1	1	0	2	0
    "C101790"	"DOID:3908"	6	9	15	7	3	0.4
    "C101790"	"DOID:3910"	1	0	1	2	0	1
    "C101790"	"DOID:5742"	0	1	1	0	1	0
    "C101790"	"DOID:7474"	1	1	2	3	1	0.5
    "C101790"	"DOID:769"	0	1	1	0	1	0
    "C113655"	"DOID:3908"	1	3	4	3	3	0.25
    "C113655"	"DOID:3910"	1	0	1	2	0	1
    "C113655"	"DOID:7474"	1	1	2	4	3	0.5
    ```



All fact tables are:

-   tested for grain correctness
-   rebuildable via `dbt build`
-   auditable down to raw evidence IDs

## Curation-Structure Marts (Materialized)

ALKfred includes three marts that summarize how CIViC curation behaves structurally (distribution over time, concentration effects, and abstraction level).  
These outputs are diagnostics on the *shape and density* of curated evidence.

- `mart_therapy_variant_coverage`
  diversity_density = unique_variants / total_eids
  Interpreted as the average number of distinct resistant variants per curated evidence item for that therapy.

  **First 10 rows (sample):**
  ```text 
  "therapy_name"	"therapy_sk"	"variants"	"eids"	"diversity_density"
  "Lorlatinib"	"35d0070816161ef18f72cb97f002583a"	7	3	2.3333333333333333
  "Luminespib"	"70797d436e891db0095c96cc044cb3d0"	2	1	2.0000000000000000
  "ALK Inhibitor TAE684"	"127c2f5a039038a64a370bc2c5082f2f"	2	1	2.0000000000000000
  "Brigatinib"	"0b55b1a2febecd6c96abe94c697c5448"	2	1	2.0000000000000000
  "Osimertinib"	"fe0fedf8af79693d9d0598ba100e617e"	4	3	1.3333333333333333
  "Ceritinib"	"1e06a4f0b19574527b56aeffda8345a0"	4	3	1.3333333333333333
  "Alectinib"	"31f62dcf80b82341b725367c2f52090f"	12	10	1.2000000000000000
  "Afatinib"	"1699e0d1488f90386a0781ffc019c462"	2	2	1.00000000000000000000
  "Anti-PD-L1 Monoclonal Antibody"	"1343afeb1aa1249daa99a7d5bdee05b1"	1	1	1.00000000000000000000
  "Anti-PD1 Monoclonal Antibody"	"72b86cbf97fd1616bd4a8202a305996f"	1	1	1.00000000000000000000
  ```

- `mart_therapy_maturity`
Therapy-level lifecycle/maturity signals derived from evidence publication years.

Metrics include:
- `first_year`, `last_year`, `year_span`
- `total_eids`
- `peak_year`, `peak_year_eids`, `peak_year_share`
- `maturity_label` (e.g., `MATURE_DISTRIBUTED`, `RECENT_BURST_OR_SINGLE_YEAR`, `LOW_SIGNAL`)

**First 10 rows (sample):**
```text
"therapy_sk"	"ncit_id"	"therapy_name"	"total_eids"	"unique_variants"	"first_year"	"last_year"	"year_span"	"peak_year"	"peak_year_eids"	"peak_year_share"	"maturity_label"
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	105	61	2004	2022	19	2013	18	0.1714	"MATURE_DISTRIBUTED"
"991f2d544f52d7945103df9c68db116c"	"C74061"	"Crizotinib"	74	29	2007	2022	16	2012	13	0.1757	"MATURE_DISTRIBUTED"
"975fc91ddd4772891706f699601f802c"	"C1855"	"Gefitinib"	70	37	2003	2022	20	2011	19	0.2714	"MATURE_DISTRIBUTED"
"1699e0d1488f90386a0781ffc019c462"	"C66940"	"Afatinib"	24	13	2008	2021	14	2015	6	0.2500	"MID_SIGNAL"
"fe0fedf8af79693d9d0598ba100e617e"	"C116377"	"Osimertinib"	24	12	2014	2024	11	2019	6	0.2500	"MID_SIGNAL"
"31f62dcf80b82341b725367c2f52090f"	"C101790"	"Alectinib"	23	16	2011	2024	14	2014	5	0.2174	"MID_SIGNAL"
"a5fef84bd99cd7a061b55decfbd1cff1"	"C1723"	"Cetuximab"	18	13	2004	2018	15	2016	6	0.3333	"MID_SIGNAL"
"1e06a4f0b19574527b56aeffda8345a0"	"C115112"	"Ceritinib"	18	15	2014	2018	5	2014	9	0.5000	"MID_SIGNAL"
"35d0070816161ef18f72cb97f002583a"	"C113655"	"Lorlatinib"	10	11	2016	2020	5	2016	7	0.7000	"RECENT_BURST_OR_SINGLE_YEAR"
"127c2f5a039038a64a370bc2c5082f2f"	"C171615"	"ALK Inhibitor TAE684"	9	8	2008	2014	7	2008	5	0.5556	"MID_SIGNAL"
```

---

- `mart_therapy_dispersion`
Therapy-level dispersion / concentration diagnostics to detect “inflated breadth” (many variants driven by few evidence items).

Metrics include:
- `unique_variants`, `total_eids`
- `avg_variants_per_eid`, `variants_per_eid`
- `max_variants_on_single_eid`
- `top_eid_share`
- `dispersion_label` (e.g., `DISTRIBUTED`, `CONCENTRATED`, `DENSE`, `LOW_SIGNAL`)

**First 10 rows (sample):**
```text
"therapy_sk"	"ncit_id"	"therapy_name"	"total_eids"	"unique_variants"	"variants_per_eid"	"avg_variants_per_eid"	"max_variants_on_single_eid"	"top_eid"	"top_eid_variants"	"top_eid_share"	"dispersion_label"
"bf3fe6ec3be7e4642016ff1e6ef3f823"	"C70792"	"Ramucirumab"	1	2	2.0000	2.0000	2	11240	2	1.0000	"LOW_SIGNAL"
"09670f93411bd49bf8c4eef3c4796364"	"C148147"	"Lazertinib"	1	2	2.0000	2.0000	2	12131	2	1.0000	"LOW_SIGNAL"
"fa6e93472629ebc992fecd21acd7e32f"	"C1282"	"Carboplatin"	1	2	2.0000	2.0000	2	12156	2	1.0000	"LOW_SIGNAL"
"70797d436e891db0095c96cc044cb3d0"	"C71467"	"Luminespib"	1	2	2.0000	2.0000	2	841	2	1.0000	"LOW_SIGNAL"
"b48825147282cad754dbf816a60d563e"	"C1212"	"Sirolimus"	1	1	1.0000	1.0000	1	1089	1	1.0000	"LOW_SIGNAL"
"b8de310c03245459110eee6dfe43bcd5"	"C1237"	"Staurosporine"	1	1	1.0000	1.0000	1	278	1	1.0000	"LOW_SIGNAL"
"ab89d367dfe894572ad74f90464074be"	"C91835"	"Hyperthermic Intraperitoneal Chemotherapy"	1	1	1.0000	1.0000	1	5923	1	1.0000	"LOW_SIGNAL"
"9bbcc4eeca3afc8e764780692ebc6cf9"	"C126752"	"Mobocertinib"	1	1	1.0000	1.0000	1	11228	1	1.0000	"LOW_SIGNAL"
"72b86cbf97fd1616bd4a8202a305996f"	"C128037"	"Anti-PD1 Monoclonal Antibody"	1	1	1.0000	1.0000	1	7586	1	1.0000	"LOW_SIGNAL"
"1343afeb1aa1249daa99a7d5bdee05b1"	"C128057"	"Anti-PD-L1 Monoclonal Antibody"	1	1	1.0000	1.0000	1	7587	1	1.0000	"LOW_SIGNAL"
```


---

- `mart_variant_abstraction_profile`
Variant abstraction distribution by therapy, using deterministic rule-based classification from CIViC variant strings.

Outputs include:
- `variant_class`
- `unique_variants`
- `variant_class_share`

**First 10 rows (sample):**
```text
"therapy_sk"	"ncit_id"	"therapy_name"	"variant_class"	"unique_variants"	"variant_class_share"
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"SNV_OR_POSITIONAL"	34	0.5574
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"INSERTION"	14	0.2295
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"FUSION"	5	0.0820
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"DELETION"	2	0.0328
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"OTHER"	2	0.0328
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"EXPRESSION"	1	0.0164
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"EXON20_INS_FAMILY"	1	0.0164
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"DUPLICATION"	1	0.0164
"ee651c67835f6a98e4d0c3d8238f04d0"	"C65530"	"Erlotinib"	"AMPLIFICATION_OR_CNV"	1	0.0164
"74ba9b3130451a555d2effe8b3b4701f"	"C167205"	"Sunvozertinib"	"INSERTION"	44	0.9167
```
------------------------------------------------------------------------

## Run the Pipeline (End-to-End)

ALKfred runs as a single pipeline:

1)  Apply idempotent Postgres schema\
2)  Fetch CIViC GraphQL evidence\
3)  Filter evidence by oncogene(s)\
4)  Load raw tables into Postgres\
5)  Build + test analytics layer (`dbt build`)

### Environment Variable

``` bash
export PG_DSN="dbname=databasename user=you_username password=password host=host.docker.internal port=5432"
```

### Run

``` bash
python -m alkfred.cli.build \ 
  --oncogene ALK,EGFR \ 
  --source civic \ 
  --build-dbt \ 
  --verbose \
  --overwrite \
```

### Full Refresh (when needed)

``` bash
python -m alkfred.cli.build \ 
  --oncogene ALK,EGFR \ 
  --source civic \ 
  --build-dbt \ 
  --full-refresh \  
  --verbose \ 
  --overwrite \
```

------------------------------------------------------------------------

## Repository Structure

  Path                            Purpose
  ------------------------------- --------------------------
  `src/alkfred/api_calls.py`      CIViC GraphQL pagination
  `src/alkfred/civic_parser.py`   Normalization utilities
  `src/alkfred/cli/`              CLI pipeline
  `models/staging/`               dbt staging models
  `models/dims/`                  dbt dimension tables
  `models/bridges/`               dbt bridge tables
  `models/marts/`                 dbt facts + marts

------------------------------------------------------------------------

## Running dbt Directly (Development)

``` bash
dbt debug
dbt build
dbt build -s fact_therapy_disease
dbt test
```

------------------------------------------------------------------------

## Maintainer

Paul Ostaci
Independent Data Engineer
Focus: healthcare data modeling, dbt analytics, real-world ETL design
