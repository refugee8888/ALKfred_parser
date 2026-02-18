# ALKfred – Architecture

## What this is (and what it is not)

**ALKfred** is a **Postgres-backed ELT analytics warehouse** for CIViC variant–therapy evidence.

- It is a reproducible *curation-analytics* warehouse: it models **how CIViC evidence is structured and distributed**.
- It is **not** a clinical decision support system.
- It is **not** patient-grade, outcome-grade, or predictive modeling infrastructure.
- It does **not** infer biology; it preserves and summarizes curated assertions.

**Python loads raw data; dbt models data; Postgres stores truth.**

---

## High-level data flow

```
CIViC GraphQL API
        ↓
Python ingestion (fetch → snapshot → load)
        ↓
Postgres raw tables (civic_raw_*)
        ↓
dbt models (stg → dim → bridge → fact → mart)
        ↓
Analytics-ready facts + marts
```

**Key principle:** Postgres is the warehouse. dbt is the modeling layer.  
There is no separate “analytics DB”.

---

## Responsibilities by layer

### Python: ingestion + replayability (not analytics)

Python is responsible for:

- GraphQL pagination + fetch of CIViC evidence
- Writing a **raw JSON snapshot** (replayable input)
- Loading raw tables into Postgres (append/overwrite behavior is deliberate)
- Minimal normalization only (type casts, trimming, ingestion metadata)

Python intentionally does **not**:

- Join entities into analytics grains
- Define dimension keys
- Build bridges/facts/marts
- Compute curation metrics

If an output looks “analytical”, it should live in dbt.

---

### Postgres: single source of truth

Postgres stores:

- Raw ingested sources (`civic_raw_*`)
- dbt-produced models (views/tables)
- Incremental bridge/fact tables (merge strategy)
- Everything queryable by analysts

There is no hidden state outside Postgres.

---

### dbt-core: modeling, constraints, analytics

dbt is the **only** place where:

- grains are defined
- relationships are resolved (bridges)
- entities are deduplicated (dimensions)
- facts are constructed
- marts are computed
- tests enforce correctness

---

## dbt project structure

This is the intended structure (folder names may vary slightly by repo layout):

```
models/
  staging/         -- stg_* views: light cleanup, typing, trimming
  dims/            -- dim_* tables: stable lookup entities
  bridges/         -- bridge_* tables: many-to-many resolution from evidence
  facts/     -- fact_* tables: analytics grains
  facts/marts/          -- mart_* tables: clinician/analyst-facing summaries
```

---

## Modeling philosophy

### Evidence is the only true atomic grain

In CIViC, the only reliably atomic unit is **evidence item id (`eid`)**.

Everything else is many-to-many relative to evidence:

- one evidence item can reference multiple therapies
- multiple variants
- one disease (often), but still handled as an association
- a molecular profile that can include multiple variants

Therefore:

- **`eid` is the fact root**
- all associations are resolved via **bridges**
- facts are built by joining bridges + dims (not by flattening early)

This prevents premature flattening and preserves CIViC’s combinatorial meaning.

---

## Layer details

### Raw tables (`civic_raw_*`) — loaded by Python

Raw tables represent CIViC data as ingested.

Typical raw entities:

- `civic_raw_evidence`
- `civic_raw_disease`
- `civic_raw_molecular_profile`
- `civic_raw_gene_variant`
- `civic_raw_therapy`

Raw tables can be “wide” and repetitive by design. Downstream models deduplicate.

---

### Staging models (`stg_*`) — light cleanup only

Staging is intentionally boring:

- type casts (`eid::int`)
- trimming/uppercase normalization
- schema alignment across runs
- ingestion metadata retained (`ingestion_run_id`, `ingested_at_utc`)

**No cross-entity joins.**  
If staging starts looking “smart”, it’s usually a smell.

---

### Dimensions (`dim_*`) — stable lookup entities

Dimensions provide **stable identifiers** and canonical attributes.

Examples:

- `dim_gene_variant`
  - deterministic `variant_sk = md5(variant_nk)`
  - `variant_nk` derived from CIViC allele registry id when available, else fallback
  - includes `driver_gene` normalization for fusions (rule-based, explicit)

- `dim_therapy`
  - deterministic `therapy_sk = md5(therapy_nk)`
  - `therapy_nk` prefers NCIT id; fallback to name-based key

- `dim_disease`
  - DOID-based disease identity

- `dim_evidence`
  - one row per `eid` with intrinsic attributes (direction, significance, pub_year, etc.)

Dimensions are deduped by windowing and treated as replacement-style “latest row wins”.

---

### Bridges (`bridge_*`) — resolve many-to-many associations

Bridges represent relationships at the correct grain:

- one row per `(eid, dimension_key)`
- deduped via window functions
- incremental merge with overlap windows where needed
- **no aggregation**

Examples:

- `bridge_evidence_variant (eid, variant_sk)`
- `bridge_evidence_therapy (eid, ncit_id)`

Bridges *intentionally* multiply rows because CIViC evidence is multi-valued.

That is not bloat — that’s correctness.

---

### Fact tables (`fact_*`) — analytics grains

Facts are built from **dims + bridges**.

Typical patterns:

1) `fact_evidence_item`
- **Grain:** one row per `eid`
- intrinsic evidence attributes only
- no combinatorial explosion

2) `fact_evidence_assoc`
- **Grain:** exploded associations (e.g., `eid × disease × variant × therapy × molecular_profile` depending on model)
- preserves CIViC’s combinatorial linkage so downstream aggregation doesn’t lose signal

3) `fact_therapy_disease`
- **Grain:** `(therapy, disease)`
- counts resistance vs sensitivity evidence + variants
- clinician-friendly summary

4) `fact_variant_therapy_daily`
- **Grain:** `(variant, therapy, disease, activity_date)`
- time-aware aggregation for trend-style analysis
- combinatorial counting is intentional: if one evidence item links multiple variants/therapies, each combination is represented

---

### Marts (`mart_*`) — curation-structure summaries

Marts summarize **how CIViC curation behaves structurally**, not biological truth.

Examples (if present in the repo):

- `mart_therapy_maturity`
  - first/last year, year span, peak-year share
  - maturity labels (distributed vs burst vs low-signal)

- `mart_therapy_dispersion`
  - detects “inflated breadth” where many variants come from few evidence items

- `mart_variant_abstraction_profile`
  - classifies variant strings into allele-level vs family-level/state-level buckets
  - exposes abstraction heterogeneity (important for interpreting counts)

These marts are meant as diagnostics so analysts don’t over-interpret raw counts.

---

## Incremental strategy (bridges/facts)

Incremental models typically use:

- `incremental_strategy='merge'`
- deterministic unique keys (composite where needed)
- time guards based on `ingested_at_utc`
- overlap windows (e.g., 3 days) to avoid late-arriving duplicates

Example pattern:

```sql
{% if is_incremental() %}
  and ingested_at_utc >= (
    select coalesce(max(ingested_at_utc), timestamp '1900-01-01')
    from {{ this }}
  ) - interval '3 days'
{% endif %}
```

This is a pragmatic compromise: correctness over minimal writes.

---

## Testing strategy (dbt)

dbt tests are used to enforce real constraints:

- uniqueness of dimension keys (`*_sk`, natural keys)
- not-null constraints on grains
- accepted values (e.g., significance categories)
- relationship integrity where appropriate
- composite-grain correctness in bridges/facts

Tests reflect the warehouse’s analytical guarantees — not just “nice to have” validation.

---

## Orchestration (Prefect + CLI)

The end-to-end pipeline is designed to be runnable as a single command:

1. Apply idempotent Postgres schema
2. Fetch CIViC evidence (paginated)
3. Filter by oncogene(s)
4. Load raw tables into Postgres
5. Run `dbt build` (or `dbt run`, with optional `--full-refresh`)

Prefect provides task structure, logging, retries (if configured), and a clean future path to scheduled runs.

---

## Summary

ALKfred is:

- **SQL-first**
- **dbt-native**
- **warehouse-correct** for CIViC’s evidence model
- **truth-preserving** (bridges/facts avoid premature flattening)
- built for *curation-structure analytics* and future extension


