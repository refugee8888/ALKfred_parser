
# **ALKfred**

### *Open Oncology ETL + Postgres Warehouse + dbt Analytics*

ALKfred is a fully open-source oncology data pipeline that ingests, normalizes, and analyzes cancer variant–therapy resistance patterns. It pulls evidence from the **CIViC** knowledgebase (GraphQL), loads it into a **Postgres warehouse**, cleans it via **dbt-core**, and produces analytical **fact tables** used to study ALK+ NSCLC resistance dynamics.

ALKfred is built end-to-end:

* Python ETL (raw ingestion + normalization)
* Postgres database (warehouse)
* dbt-core project (staging + marts + tests)
* Devcontainer for reproducible development
* Future: automated CI/CD (GitHub Actions)

---

## Features

### **Ingestion**

* Automated CIViC GraphQL downloader (paginated)
* Deterministic, reproducible raw evidence extraction
* `.env`-based secure API key handling
* Raw → staging table population

### **Warehouse**

* Postgres star-schema warehouse (dims, facts, links)
* Idempotent SQL loaders
* UUID-based variant keys
* Analytic fact tables:

  * `fact_therapy_disease`
  * `fact_variant_therapy_daily` *(in progress)*

### **dbt Analytics**

* Full **dbt-core** project
* Sources + staging models for:

  * diseases
  * therapies
  * variants
  * molecular profiles
  * evidence
* Tests:

  * uniqueness constraints
  * not-null on key fields
  * accepted values for significance
* Materialized views + tables in Postgres
* Rebuildable with:

  ```bash
  dbt build
  ```

### **Developer experience**

* Remote devcontainer (VS Code / Cursor)
* Postgres running on host, mounted profile into container
* Reproducible environment with pinned Python + dbt versions
* No local dependency conflict

---

# Architecture Overview

```
     CIViC GraphQL API
              ↓
       ┌──────────────────┐
       │  Raw JSON fetch  │  (api_calls.py / civic_fetch.py)
       └──────────────────┘
              ↓
    /data/civic_raw_evidence.json
              ↓
       ┌──────────────────┐
       │ Python ETL Load  │  (stg/dim/link/fact loaders)
       └──────────────────┘
              ↓
        Postgres Warehouse
              ↓
       ┌──────────────────┐
       │     dbt-core     │  (staging → marts)
       └──────────────────┘
              ↓
       Cleaned analytic tables
```

---

# Repository Structure

| Component                     | Purpose                                  |
| ----------------------------- | ---------------------------------------- |
| `src/alkfred/api_calls.py`    | CIViC GraphQL pagination + HTTP layer    |
| `src/alkfred/etl/*`           | Raw → staging → dim → fact table loaders |
| `src/alkfred/civic_parser.py` | Molecular profile & ontology cleanup     |
| `src/alkfred/cli/*`           | Command-line ETL & querying tools        |
| `src/alkfred/utils.py`        | Normalization utilities                  |
| `dbt_project.yml`             | dbt-core project config                  |
| `models/staging/*`            | dbt staging models (views)               |
| `models/marts/facts/*`        | dbt fact tables (tables)                 |
| `models/sources.yml`          | Source definitions for Postgres tables   |
| `tests/`                      | pytest integration tests                 |
| `.devcontainer/`              | full dev environment config              |

---

# Postgres Schema (Warehouse)

### **Staging Tables (loaded by Python)**

| Table                   | Description                                  |
| ----------------------- | -------------------------------------------- |
| `stg_disease`           | Raw DOID + normalized disease names          |
| `stg_evidence`          | Raw evidence (eid, significance, timestamps) |
| `stg_molecular_profile` | MP identifiers                               |
| `stg_therapy`           | Raw therapy strings                          |
| `stg_gene_variant`           | Gene + variant info                          |

### **Dimension Tables**

| Table                   | Description                        |
| ----------------------- | ---------------------------------- |
| `dim_disease`           | DOID, NCIT, MONDO cross-links      |
| `dim_therapy`           | NCIT IDs, normalized therapy names |
| `dim_gene_variant`      | Gene symbol + variant name         |
| `dim_molecular_profile` | Molecular profile lookup           |
| `dim_evidence	`         | Evidence conceptulization         |

### **Link**

| Table           | Purpose                                        |
| --------------- | ---------------------------------------------- |
| `evidence_link` | Bridges evidence → variant → therapy → disease |

### **Facts**

| Fact Table                   | Description                                             |
| ---------------------------- | ------------------------------------------------------- |
| `fact_evidence`              | Granular evidence-level table                           |
| `fact_therapy_disease`       | Therapy × Disease aggregate (resistance vs sensitivity) |
| `fact_variant_therapy_daily` | Daily variant × therapy × disease rates *(in dbt)*      |

---

# 🔧 Devcontainer + dbt Setup

### Devcontainer mounts your host `~/.dbt/`:

```json
"mounts": [
  "source=${localEnv:HOME}/.dbt,target=/home/appuser/.dbt,type=bind"
]
```

### Debug dbt connection:

```bash
dbt debug
```

### Run the full transformation layer:

```bash
dbt build
```

### Run only one model:

```bash
dbt build -s fact_therapy_disease
```

---

# Docker (Legacy ETL Mode)
---

# Testing

### Run pytest:

```bash
pytest -v
```

### Run dbt tests:

```bash
dbt test
```

Covers:

* source freshness
* not-null constraints
* uniqueness on fact grains
* accepted values (RESISTANCE / SENSITIVITY)

---


# Roadmap

### Short term

* Add `fact_variant_therapy_daily` to dbt (daily rates)
* Create `dim_variant_therapy` lookup table
* Add dbt docs site (`dbt docs generate`)

### Medium term

* GitHub Actions CI for:

  * pytest
  * dbt build
  * SQL formatting
* Ontology enrichment (NCIT, MONDO, EFO)
* Export facts to Parquet

### Long term

* Mutation evolution modeling (ALK resistance timelines)
* Add embeddings for disease normalization
* Build ALKfred web UI for variant search

---

# Maintainer

**Paul Ostaci**
Independent Data Engineer & Creator of ALKfred
Focused on oncology data pipelines, ETL design, and mutation resistance analytics.

