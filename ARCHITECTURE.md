# ALKfred – Architecture

## Overview

ALKfred is a **Postgres-backed analytical warehouse** for oncology evidence data, modeled and transformed using **dbt-core**.

Python is used **only for raw ingestion and initial normalization**.  
All **business logic, modeling, constraints, and analytics live in dbt**.

The system follows a **modern ELT architecture**:

- **Extract + Load**: Python → Postgres (raw/staging-ready tables)
- **Transform**: dbt → star schema + bridges + analytical marts
- **Analyze**: SQL-first facts designed for clinical interpretation

---

## High-Level Data Flow

CIViC GraphQL API
↓
Python ingestion (ETL)
↓
Postgres (raw / staging tables)
↓
dbt-core transformations
↓
Dims • Bridges • Facts • Analytics

---
Key principle:  
> **Postgres is the warehouse. dbt is the modeling layer.**

---

## Responsibilities by Layer

### 1. Python (Ingestion Only)

Python is responsible for:

- Fetching CIViC data (GraphQL, paginated)
- Writing **raw, reproducible records**
- Minimal normalization (types, trimming, timestamps)
- Loading data into **staging-compatible tables**

Python **does NOT**:
- Join tables
- Enforce analytics grain
- Compute metrics
- Encode domain logic

Those responsibilities belong to dbt.

---

### 2. Postgres (Warehouse)

Postgres is the **single source of truth**.

It stores:

- Staging tables populated by Python
- All dbt models (views + tables)
- Constraints validated by dbt tests
- Incremental analytical facts

There is **no separate analytics DB**.

---

### 3. dbt-core (Modeling & Analytics)

dbt handles:

- Staging cleanup
- Dimensional modeling
- Bridge tables
- Fact tables
- Aggregations
- Data tests
- Incremental logic

Everything analysts and clinicians query is produced by dbt.

---

## dbt Project Structure

models/
├── sources.yml
├── staging/
│   ├── stg_disease.sql
│   ├── stg_evidence.sql
│   ├── stg_gene_variant.sql
│   ├── stg_molecular_profile.sql
│   └── stg_therapy.sql
│
├── dims/
│   ├── dim_disease.sql
│   ├── dim_evidence.sql
│   ├── dim_gene_variant.sql
│   ├── dim_molecular_profile.sql
│   └── dim_therapy.sql
│
├── bridges/
│   ├── bridge_evidence_disease.sql
│   ├── bridge_evidence_variant.sql
│   ├── bridge_evidence_therapy.sql
│   └── bridge_evidence_molecular_profile.sql
│
├── facts/
│   ├── fact_evidence_item.sql
│   ├── fact_evidence_assoc.sql
│   ├── fact_therapy_disease.sql
│   └── fact_variant_therapy_daily.sql
│
└── marts/
└── analytics-ready views

---

## Modeling Philosophy

### Evidence Is the Atomic Grain

The **only truly atomic entity** in CIViC is:
evidence_id (eid)

Everything else (diseases, variants, therapies, molecular profiles) is **many-to-many** relative to evidence.

Therefore:

- `eid` is the **fact root**
- All associations are handled via **bridge tables**

---

## Staging Models (`stg_*`)

Purpose:

- Light cleanup only
- Type casting
- Trimming strings
- Renaming columns
- No joins across entities

Example:

```sql
select
  eid::int,
  upper(trim(significance)) as significance,
  ingested_at_utc
from source('alkfred', 'stg_evidence')
```

Dimension Models (dim_*)

Dimensions provide stable lookup entities, not facts.

Examples:
	•	dim_gene_variant
	•	Deterministic variant_sk
	•	Natural key (variant_nk) derived from CIViC CA ID or gene+variant
	•	dim_therapy
	•	NCIT identifiers
	•	dim_disease
	•	DOID-based disease entities

Dimensions are deduplicated, slowly changing by replacement, and tested for uniqueness.

⸻

Bridge Tables (bridge_*)

Bridges resolve many-to-many relationships between evidence and dimensions.

Pattern:

eid ↔ dimension key


Examples:
	•	bridge_evidence_variant (eid, variant_sk)
	•	bridge_evidence_therapy (eid, ncit_id)
	

Rules:
	•	One row per (eid, dimension_key)
	•	Deduplicated via window functions
	•	Incremental with safety overlap
	•	No aggregation

Bridges intentionally duplicate rows when evidence references multiple entities — this is correct and required.

⸻

Fact Tables

1. fact_evidence_item

Grain: one row per eid

Contains intrinsic evidence attributes:
	•	direction
	•	significance
	•	publication year
	•	ingestion metadata

No foreign keys to dimensions.

⸻

2. fact_evidence_assoc

Grain: one row per (eid, doid, therapy, variant, molecular_profile)

This is the exploded fact, produced by joining bridges.

Purpose:
	•	Preserve full combinatorial meaning of CIViC evidence
	•	Enable downstream aggregation without losing signal

⸻

3. fact_therapy_disease

Grain: (therapy, disease)

Metrics:
	•	resistant evidence count
	•	sensitive evidence count
	•	resistance rate

Clinician-facing aggregate.

⸻

4. fact_variant_therapy_daily

Grain: (variant, therapy, disease, activity_date)


Purpose:
	•	Time-aware resistance trends
	•	Multi-variant, multi-therapy evidence propagation
	•	Clinically meaningful counting:
	•	If an evidence item links to multiple variants and therapies,
each combination is counted

This is intentional and correct.

⸻

Incremental Strategy

Facts and bridges use incremental merge with:
	•	Deduplication via window functions
	•	Time-based guards using ingested_at_utc
	•	Safety overlap windows where needed
```sql
{% if is_incremental() %}
  and ingested_at_utc >= (
    select coalesce(max(ingested_at_utc), timestamp '1900-01-01')
    from {{ this }}
  ) - interval '3 days'
{% endif %}
```

Testing Strategy

dbt tests enforce:
	•	Uniqueness of dimension keys
	•	Not-null constraints on fact grains
	•	Accepted values for significance
	•	Grain correctness (composite keys)

Tests reflect real-world analytical expectations, not artificial normalization.

⸻

Key Design Decisions (Intentional)
	•	Evidence is not flattened prematurely
	•	Multi-therapy / multi-variant evidence is fully propagated
	•	No snowflaking inside facts
	•	dbt is the single transformation authority
	•	Postgres is the only warehouse

Summary

ALKfred is:
	•	SQL-first
	•	dbt-native
	•	Clinically interpretable
	•	Correctly denormalized where needed
	•	Built for evolution toward temporal mutation modeling

This architecture intentionally favors truth preservation over convenience, which is essential for oncology analytics.