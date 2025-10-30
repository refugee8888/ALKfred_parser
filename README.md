
ALKfred

CIViC Oncology Evidence ETL + Query Engine (Dockerized)

ALKfred is a containerized, open-source pipeline that mirrors the CIViC cancer variant knowledgebase into a normalized SQLite schema.
It automates fetching, parsing, and loading of gene–variant–disease–therapy evidence, enabling local querying and variant resistance analysis without external dependencies.

⸻

Features
	•	Automated CIViC API ingestion (GraphQL evidenceItems)
	•	Normalization and deduplication of variants, diseases, and therapies
	•	Star-schema SQLite database for reproducible queries
	•	Variant-level resistance/sensitivity mapping
	•	Pytest coverage for ETL, schema, and CLI validation
	•	Full Docker support for isolated development

⸻

Project Architecture

CIViC API
  ↓
civic_fetch.py   →  raw JSON
  ↓
civic_curate.py  →  curated JSON
  ↓
schema.sql       →  database structure
  ↓
dim_load/*.py    →  dimension & fact population
  ↓
SQLite           →  queryable DB

Component	Purpose
api_calls.py	GraphQL pagination and CIViC API interaction
civic_fetch.py	Downloads evidence by gene symbol and writes raw JSON
civic_curate.py	Normalizes, deduplicates, and aggregates variant data
civic_parser.py	Internal helpers for molecular profile parsing
config.py	Manages paths, environment, DB connection, and schema application
sql/	Contains schema definition and loaders for dim/fact tables
cli/build.py	Main pipeline entry point (--source, --overwrite, --limit)
cli/query.py	Prototype CLI query runner
bioportal_parser.py, bioportal_query_mini.py	Experimental modules for ontology enrichment
utils.py	Normalization, I/O, and JSON utilities
tests/	pytest unit and integration tests


⸻

Docker Setup

1. Build and launch container

```bash
docker-compose up --build -d
```

This starts a long-running container with:
	•	src/ mounted into /app/src
	•	data/ mounted into /app/data
	•	.env injected into /app/.env
	•	Python path automatically set to /app/src

To access the environment:

''' docker exec -it alkfred-alkfred-1 bash '''

2. Run ETL inside container

```bash
python -m alkfred.cli.build \
  --source civic \
  --raw data/civic_raw_evidence_db.json \
  --curated data/curated_resistance_db.json \
  --db data/alkfred.sqlite \
  --overwrite \
  --limit 500 \
  --verbose 
```



⸻

3. Testing

Inside the container:

``` pytest -v ```

Tests cover:
	•	Fetch logic (test_civic_fetch.py)
	•	Schema creation (test_sql_dims.py)
	•	CLI smoke tests (test_smoke_cli.py)
	•	Utility normalization (test_utils.py)

⸻

4. Schema Summary

Table	Description
dim_disease	Disease labels, DOIDs, NCIT, MONDO references
dim_gene_variant	Gene symbol, variant label, and aliases
dim_therapy		Therapy name and NCIT reference
dim_evidence	Evidence metadata (significance, direction, level)
evidence_link	Bridges evidence to its variant, therapy, and disease
fact_evidence	Aggregated analytic layer for resistance/sensitivity queries


⸻

CLI example queries:

```bash
python -m alkfred.cli.query query --variant "g1202r" --significance all --disease all 
```

Output:
```bash

2025-10-29 12:58:35,440 [INFO] Final query input: alk_g1202r
2025-10-29 12:58:35,453 [INFO] Connected to database: /app/data/alkfred.sqlite
{'eid': 1350, 'doid': '162', 'therapy_id': '217925c3-fecd-55d8-939a-bb3e0e6771b1', 'variant_id': 'CA16602592', 'label_display': 'alectinib', 'label_disease_norm': 'cancer', 'significance': 'RESISTANCE'}
{'eid': 1351, 'doid': '162', 'therapy_id': '3563f716-82a6-5e59-b5e5-eaed446b01e4', 'variant_id': 'CA16602592', 'label_display': 'brigatinib', 'label_disease_norm': 'cancer', 'significance': 'RESISTANCE'}
{'eid': 1345, 'doid': '3908', 'therapy_id': '08557006-b6a9-5db4-95fd-eb7a64d17a75', 'variant_id': 'CA16602592', 'label_display': 'ceritinib', 'label_disease_norm': 'lung_non_small_cell_carcinoma', 'significance': 'RESISTANCE'}
{'eid': 441, 'doid': '3908', 'therapy_id': 'dfdc51ba-63cd-5b9a-a09d-97276ae69538', 'variant_id': 'CA16602592', 'label_display': 'crizotinib', 'label_disease_norm': 'lung_non_small_cell_carcinoma', 'significance': 'RESISTANCE'}
{'eid': 1357, 'doid': '3910', 'therapy_id': 'dfdc51ba-63cd-5b9a-a09d-97276ae69538', 'variant_id': 'CA16602592', 'label_display': 'crizotinib', 'label_disease_norm': 'lung_adenocarcinoma', 'significance': 'RESISTANCE'}
{'eid': 11114, 'doid': '7474', 'therapy_id': 'def3400c-ada4-522f-9045-568f229d11f0', 'variant_id': 'CA16602592', 'label_display': 'lorlatinib', 'label_disease_norm': 'malignant_pleural_mesothelioma', 'significance': 'RESISTANCE'}
{'eid': 1352, 'doid': '3908', 'therapy_id': '3e17d968-3e24-5c0a-9369-fecc47533807', 'variant_id': 'CA16602592', 'label_display': 'tanespimycin', 'label_disease_norm': 'lung_non_small_cell_carcinoma', 'significance': 'SENSITIVITY'}
Number of rows: 7
```


5. Development

Local environment (no Docker)

```bash
pip install -r requirements.txt
export PYTHONPATH=src
python -m alkfred.cli.build --source civic --overwrite 
```

6. Linting & formatting

```bash
ruff check src
black src 

```


⸻

7. License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
You may freely use, modify, and distribute ALKfred, provided all derived works remain open source under the same license.

See LICENSE for details.

⸻

8. Roadmap
	•	Add MONDO + NCIT ontology enrichment (BioPortal API)
	•	CLI subcommands for query and filtering
	•	Export to parquet / CSV
	•	Add GitHub Actions for continuous testing
	•	Extend to multi-gene fetching

⸻

9. Maintainer

Independent Data Engineer Paul Ostaci
Maintains ETL, schema, and CLI stack for oncology data pipelines.

