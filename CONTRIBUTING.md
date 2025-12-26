# Contributing to ALKfred

Thank you for your interest in contributing to **ALKfred** — an open-source oncology data engineering project focused on **CIViC-based evidence**, **Postgres warehousing**, and **dbt analytics**.

ALKfred is not a demo or tutorial repo. It is intentionally designed to model **real-world clinical data engineering constraints**: explicit grains, bridge tables, auditability, and reproducibility.

Please read this document carefully before contributing.

---

## Project Philosophy

ALKfred follows a few non-negotiable principles:

- **Explicit grains** — every table must have a clearly defined grain
- **No hidden fan-out** — joins must be intentional and explainable
- **Bridges over shortcuts** — many-to-many relationships are modeled explicitly
- **Auditability** — every analytic result must trace back to CIViC evidence
- **Clarity over cleverness** — SQL should be readable, not impressive

If a model cannot be explained on a whiteboard, it does not belong here.

For major design changes, open a **Discussion** before writing code.

---

## Project Setup

1. Clone the repository

```bash
git clone https://github.com/<your-username>/ALKfred.git
cd ALKfred
```

⸻

2. Development Environment

ALKfred is designed to be developed using a devcontainer (recommended).

For limited local Python-only work (ETL utilities):

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

dbt models are expected to be run inside the containerized environment.

⸻

3. Environment Variables

Create a .env file in the project root:

```bash
BIOPORTAL_API_KEY=your_key_here
PG_DSN="dbname=your_dbname user=your_dbpostgres_user password=user_password host=host.docker.internal port=5432"
```
Never commit .env files.

⸻

4. Verify Setup

Before contributing, confirm everything works:
```bash
pytest -v
```

All tests must pass before opening a pull request.

⸻

Repository Structure

src/alkfred/
├── api_calls.py           # CIViC GraphQL ingestion
├── civic_parser.py        # Evidence normalization utilities
├── cli/                   # CLI entry points
├── utils.py               # Shared helpers
├── config.py              # Env, paths, connections
├── tests/                 # pytest suite

models/
├── staging/               # dbt staging models
├── dims/                  # dbt dimension tables
├── bridges/               # dbt bridge tables
├── marts/facts/           # dbt fact tables

⸻
Coding logic

SQL / dbt
	•	One grain per model
	•	No implicit joins
	•	No denormalized shortcuts
	•	Bridges are mandatory for M:N relationships
	•	Facts must be explainable from bridges
	•	Incremental logic must be deterministic

If you are unsure about a grain, stop and ask.

⸻

Testing Rules

Python Testing
	•	Tests live under tests/
	•	Use pytest
	•	Mock all external APIs
	•	Never hit CIViC in tests
	•	Use tmp_path for file I/O

Example:
```python
def test_normalize_label(monkeypatch):
    monkeypatch.setattr(utils, "normalize_label", lambda x: "alk")
    assert utils.normalize_label("ALK") == "alk"
```
Run:
```bash
pytest -v
```


⸻

dbt Testing
	•	Use schema tests (not_null, unique, accepted_values)
	•	Explicitly test grains
	•	Validate bridge cardinality
	•	No silent test skips

Run:

```bash
dbt test
```


⸻

Git & Commit Conventions

Branch Naming

```bash
feature/<short-description>
fix/<short-description>
test/<short-description>
```


⸻

Commit Messages

```bash
feat: add fact_variant_therapy_daily
fix: correct bridge_evidence_variant grain
test: add dbt uniqueness test for fact_evidence
```

One commit = one purpose
No bundled refactors

⸻

Pull Request Guidelines

Before opening a PR:
	1.	Fork the repository
	2.	Create a feature branch
	3.	Add or update tests
	4.	Run:
```bash
pytest -v
dbt build
```


Your PR description must include:
	•	What changed
	•	Why it changed
	•	What grain is affected
	•	Any trade-offs or limitations

⸻

Anti-Patterns (Hard No)

NO Hardcoded file paths
NO Print() inside ETL or dbt models
NO Silent exception handling
NO Committing raw JSON, databases, or large files
NO Live CIViC API calls in tests
NO Facts that hide dimensional logic

⸻

Suggested Contribution Areas

Meaningful ways to help:
	•	Ontology enrichment (NCIT / MONDO / EFO)
	•	Additional analytic marts
	•	dbt documentation & lineage improvements
	•	Performance tuning (indexes, partitions)
	•	Validation queries and data quality checks

Open a Discussion before large changes.

⸻

License

ALKfred is released under the GNU General Public License v3.0 (GPL-3.0).

By contributing, you agree that your code will be distributed under the same license.

⸻

Final Note

ALKfred values correctness, traceability, and clarity over speed.

If you are here to learn real-world data engineering — welcome.
If you are here to cut corners — this repository will push back.

