
🧬 ALKfred

CIViC Oncology Evidence ETL + Query Engine (Dockerized)

ALKfred is a containerized, open-source pipeline that mirrors the CIViC cancer variant knowledgebase into a normalized SQLite schema.
It automates fetching, parsing, and loading of gene–variant–disease–therapy evidence, enabling local querying and variant resistance analysis without external dependencies.

⸻

📦 Features
	•	🔗 Automated CIViC API ingestion (GraphQL evidenceItems)
	•	🧹 Normalization and deduplication of variants, diseases, and therapies
	•	🗃️ Star-schema SQLite database for reproducible queries
	•	🧠 Variant-level resistance/sensitivity mapping
	•	🧪 Pytest coverage for ETL, schema, and CLI validation
	•	🐳 Full Docker support for isolated development

⸻

🧱 Project Architecture

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

🐳 Docker Setup

1. Build and launch container

docker-compose up --build -d

This starts a long-running container with:
	•	src/ mounted into /app/src
	•	data/ mounted into /app/data
	•	.env injected into /app/.env
	•	Python path automatically set to /app/src

To access the environment:

docker exec -it alkfred-alkfred-1 bash

2. Run ETL inside container

python -m alkfred.cli.build \
  --source civic \
  --raw data/civic_raw_evidence_db.json \
  --curated data/curated_resistance_db.json \
  --db data/alkfred.sqlite \
  --overwrite \
  --limit 500 \
  --verbose


⸻

🧪 Testing

Inside the container:

pytest -v

Tests cover:
	•	Fetch logic (test_civic_fetch.py)
	•	Schema creation (test_sql_dims.py)
	•	CLI smoke tests (test_smoke_cli.py)
	•	Utility normalization (test_utils.py)

⸻

⚙️ Schema Summary

Table	Description
dim_disease	Disease labels, DOIDs, NCIT, MONDO references
dim_gene_variant	Gene symbol, variant label, and aliases
dim_therapy	Therapy name and NCIT reference
dim_evidence	Evidence metadata (significance, direction, level)
evidence_link	Bridges evidence to its variant, therapy, and disease
fact_evidence	Aggregated analytic layer for resistance/sensitivity queries


⸻

🧠 Example Query

SELECT variant,
       resistant_therapies,
       sensitive_therapies
FROM fact_evidence_summary
WHERE doid = '3908';

Sample output:

variant         | resistant_therapies                | sensitive_therapies
----------------|------------------------------------|-----------------------------
eml4_alk_fusion | crizotinib,ceritinib,lorlatinib    | alectinib,brigatinib
alk_g1202r      | crizotinib,ceritinib               | tanespimycin


⸻

🧰 Development

Local environment (no Docker)

pip install -r requirements.txt
export PYTHONPATH=src
python -m alkfred.cli.build --source civic --overwrite

Linting & formatting

ruff check src
black src


⸻

📜 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
You may freely use, modify, and distribute ALKfred, provided all derived works remain open source under the same license.

See LICENSE for details.

⸻

🗺️ Roadmap
	•	Add MONDO + NCIT ontology enrichment (BioPortal API)
	•	CLI subcommands for query and filtering
	•	Export to parquet / CSV
	•	Add GitHub Actions for continuous testing
	•	Extend to multi-gene fetching

⸻

🧩 Maintainer

Independent Data Engineer Paul Ostaci
Maintains ETL, schema, and CLI stack for oncology data pipelines.

