# ALKfred

### Open Oncology Data Warehouse · Postgres · dbt-core

**ALKfred** is an open-source oncology analytics warehouse focused on **variant–therapy resistance evidence**.  
It ingests raw evidence from the **CIViC** knowledgebase, stores it in **Postgres**, and uses **dbt-core** to build a fully tested **star-schema analytics layer** for clinical and research analysis.

ALKfred is designed as a **real-world data engineering project**, emphasizing:

- clear grains
- explicit bridges
- reproducible transformations
- auditability over “magic” logic

---

## What ALKfred Does

**At a high level:**

- Pulls raw CIViC evidence via GraphQL
- Stores raw + lightly normalized staging tables
- Uses **dbt** to:
  - define grains
  - enforce constraints
  - build dimensions, bridges, and facts
  - produce clinician-friendly aggregates

No ML, no heuristics — **just clean, explainable data**.

---

## Architecture Overview

      CIViC GraphQL API
               ↓
    ┌────────────────────┐
    │ Raw JSON ingestion │  (Python)
    └────────────────────┘
               ↓
    Postgres Raw / Staging Tables
               ↓
    ┌────────────────────┐
    │     dbt-core       │
    │  (stg → dim →      │
    │   bridge → fact)   │
    └────────────────────┘
               ↓
     Analytics-ready fact tables

**Key principle:**  

**Python ingests dbt models. Postgres stores truth.**

---

## Features

### **Ingestion (Python)**

- CIViC GraphQL pagination
- Deterministic raw extraction
- `.env`-based API key handling
- Raw JSON persisted for replayability
- Minimal logic by design

Python **does not** build analytics tables.

---

### **Warehouse (Postgres)**

- Explicit star schema
- No hidden surrogate logic
- Idempotent loads
- Clear separation of:
  - staging
  - dimensions
  - bridges
  - facts

---

### **Transformation & Analytics (dbt-core)**

- Full dbt project
- Source freshness + schema tests
- Staging models normalize raw inputs
- Dimensions deduplicated with deterministic keys
- Bridges handle multi-valued relationships
- Facts built **only from bridges + dimensions**

#### Key analytics tables:

- `fact_evidence_assoc`  
  *Canonical evidence grain (eid-level)*

- `fact_therapy_disease`  
  *Therapy × Disease resistance vs sensitivity*

- `fact_variant_therapy_daily`  
  *Variant × Therapy × Disease daily aggregation*

All fact tables are:

- tested for grain correctness
- rebuildable via `dbt build`
- auditable down to raw evidence IDs

---

### **Developer Experience**

- VS Code / Cursor devcontainer
- Postgres on host
- dbt profiles mounted into container
- Zero local dependency pollution
- Fast iteration on SQL models

---

## Repository Structure

| Path | Purpose |
|-----|--------|
| `src/alkfred/api_calls.py` | CIViC GraphQL ingestion |
| `src/alkfred/civic_parser.py` | Light normalization utilities |
| `data/` | Raw CIViC JSON snapshots |
| `models/staging/` | dbt staging views |
| `models/dims/` | dbt dimension tables |
| `models/bridges/` | dbt bridge tables |
| `models/marts/facts/` | dbt fact tables |
| `models/sources.yml` | dbt source definitions |
| `.devcontainer/` | Reproducible dev environment |

---

## Postgres Schema

### **Raw tables (Python-loaded)**
| Table | Description |
|------|------------|
| `civic_raw_evidence` | Evidence IDs, significance, timestamps |
| `civic_raw_disease` | DOIDs per evidence |
| `civic_raw_therapy` | NCIT therapy references |
| `civic_raw_gene_variant` | Gene + variant strings |
| `civic_raw_molecular_profile` | Molecular profile IDs |

### **Staging (Python-loaded)**

| Table | Description |
|------|------------|
| `stg_evidence` | Evidence IDs, significance, timestamps |
| `stg_disease` | DOIDs per evidence |
| `stg_therapy` | NCIT therapy references |
| `stg_gene_variant` | Gene + variant strings |
| `stg_molecular_profile` | Molecular profile IDs |

---

### **Dimensions (dbt)**

| Table | Description |
|------|------------|
| `dim_disease` | Normalized disease identifiers |
| `dim_therapy` | Therapy normalization (NCIT) |
| `dim_gene_variant` | Canonical variant identity |
| `dim_molecular_profile` | Molecular profile lookup |
| `dim_evidence` | Evidence conceptual entity |

---

### **Bridges (dbt)**

| Table | Purpose |
|------|--------|
| `bridge_evidence_variant` | Evidence ↔ Variant |
| `bridge_evidence_therapy` | Evidence ↔ Therapy |

Bridges allow **one evidence → many variants / therapies**, exactly as CIViC models reality.

---

### **Facts (dbt)**

| Table | Description |
|------|------------|
| `fact_evidence_assoc` | Canonical evidence grain |
| `fact_therapy_disease` | Therapy × Disease aggregation |
| `fact_variant_therapy_daily` | Variant × Therapy × Disease × Date |

---

## Docker & Local Orchestration

ALKfred uses Docker to provide a **reproducible execution environment** for development, testing, and CI.

Docker is used to standardize the toolchain (Python, dbt, system deps), **not** to hide or abstract the data architecture.

---

### Docker Build

A Docker image is provided to run ALKfred in a clean, deterministic environment.

Typical use cases:
- Running dbt in CI
- Executing ETL jobs without local dependency conflicts
- Reproducing bugs reported by contributors

Build the image:

```bash
docker build -t alkfred .
```

## Running dbt

```bash
dbt debug
dbt build
dbt build -s fact_therapy_disease
dbt test
```

### Pytests for api calls, Postgres connection and CLI commands

```bash
pystest -v
```

### Roadmap

Short term
	•	dbt docs site (dbt docs generate)
	•	More validation queries for clinicians
	•	Parquet exports

Medium term
	•	CI with dbt + pytest
	•	Ontology enrichment (NCIT / MONDO / EFO)
	•	Time-aware resistance trajectories

Long term
	•	Resistance evolution modeling
	•	Variant-centric clinical dashboards
	•	Open research collaboration

⸻

### Maintainer

Paul Ostaci
Independent Data Engineer
Focus: healthcare data modeling, dbt analytics, real-world ETL design