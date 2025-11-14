
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
schema.sql       →  database structure
  ↓
stg_load/*.py    →  staging population
  ↓
dim_load/*.py    →  dimension population
  ↓
evidence_link.py → 	evidence link population
  ↓
fact_evidence.py → 	fact population
  ↓
SQLite           →  queryable DB

Component	Purpose
api_calls.py	GraphQL pagination and CIViC API interaction
civic_fetch.py	Downloads evidence by gene symbol and writes raw JSON
civic_parser.py	Internal helper for molecular profile parsing
config.py	Manages paths, environment, DB connection, and schema application
sql/	Contains schema definition and loaders for stg/dim/link/fact tables
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
  --civic data/civic_raw_evidence_db.json \
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
civic_stg_disease
civic_stg_evidence
civic_stg_molecular_profile
civic_stg_therapy
civic_stg_gene_variant
civic_dim_disease	Disease labels, DOIDs, NCIT, MONDO references
civic_dim_gene_variant	Gene symbol, variant label
civic_dim_molecular_profile Molecular profile id and name
civic_dim_therapy		Therapy name and NCIT reference
civic_dim_evidence	Evidence metadata (significance, direction, level)
evidence_link	Bridges evidence to its variant, therapy, and disease
fact_evidence	Aggregated analytic layer for resistance/sensitivity queries


⸻

CLI example queries:

```bash
python -m alkfred.cli.query query --variant "g1202r" --significance all --disease all 
```

Output:
```bash

2025-11-14 12:17:08,738 [INFO] Final query input: g1202r
2025-11-14 12:17:08,748 [INFO] Connected to database: /app/data/alkfred.sqlite
{'eid': 1350, 'doid': 'DOID:162', 'ncit_id': 'C101790', 'variant_id': '2033c796-5872-55d0-9926-461cbe6fecc0', 'therapy_name': 'Alectinib', 'disease_name_norm': 'cancer', 'significance': 'RESISTANCE'}
{'eid': 1351, 'doid': 'DOID:162', 'ncit_id': 'C98831', 'variant_id': 'ec2812b6-323f-573b-a420-c2096e337dbb', 'therapy_name': 'Brigatinib', 'disease_name_norm': 'cancer', 'significance': 'RESISTANCE'}
{'eid': 1345, 'doid': 'DOID:3908', 'ncit_id': 'C115112', 'variant_id': 'c45d3671-1a30-534a-875d-b90ec7cb320e', 'therapy_name': 'Ceritinib', 'disease_name_norm': 'lung_non_small_cell_carcinoma', 'significance': 'RESISTANCE'}
{'eid': 441, 'doid': 'DOID:3908', 'ncit_id': 'C74061', 'variant_id': '288f41bc-6962-59a9-b72f-6eb27f8837ab', 'therapy_name': 'Crizotinib', 'disease_name_norm': 'lung_non_small_cell_carcinoma', 'significance': 'RESISTANCE'}
{'eid': 1357, 'doid': 'DOID:3910', 'ncit_id': 'C74061', 'variant_id': '964dbb9c-22d0-52e5-bafa-bd886f23e5a4', 'therapy_name': 'Crizotinib', 'disease_name_norm': 'lung_adenocarcinoma', 'significance': 'RESISTANCE'}
{'eid': 11114, 'doid': 'DOID:7474', 'ncit_id': 'C113655', 'variant_id': '67d2d0fa-d2f1-5f1e-af48-0c6e88ea45f4', 'therapy_name': 'Lorlatinib', 'disease_name_norm': 'malignant_pleural_mesothelioma', 'significance': 'RESISTANCE'}
{'eid': 1352, 'doid': 'DOID:3908', 'ncit_id': 'C37899', 'variant_id': '0063fafd-4845-502c-a83d-1ce31a7d17aa', 'therapy_name': 'Tanespimycin', 'disease_name_norm': 'lung_non_small_cell_carcinoma', 'significance': 'SENSITIVITY'}
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

