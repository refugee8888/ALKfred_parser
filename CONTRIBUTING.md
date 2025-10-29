Contributing to ALKfred

Thank you for your interest in improving ALKfred, a CIViC-based oncology data engineering project.
This guide explains how to set up your environment, follow code conventions, and contribute responsibly.

Project Setup
1. Clone the repository
```bash
git clone https://github.com/<your-username>/ALKfred.git
cd ALKfred
``` 

2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```


3. Environment variables

Create a .env file in the project root:

OPENAI_API_KEY=your_key
BIOPORTAL_API_KEY=your_key

4. Run tests to confirm setup
```
pytest -v
```

All tests should pass before submitting a pull request.

Code Structure
src/alkfred/
├── etl/                 # Fetch, curate, and normalize CIViC data
├── sql/dim_load/        # SQLite dimension and fact loaders
├── cli/                 # Command-line entry points
├── utils.py             # Helper functions (normalization, I/O)
├── config.py            # Paths, connections, env management
└── tests/               # Pytest suite

Coding Standards
Rule	Example
Follow PEP8 style	use 4 spaces, lowercase function names
Use type hints	def fetch_data(symbol: str) -> list[dict]:
Prefer f-strings	f"Loading table {table_name}"
Keep functions short	one clear responsibility
Use logging over print	logger.info("Task complete")
Avoid silent failures	raise or log every exception

All ETL modules must include a clear docstring:

"""
Fetch and filter CIViC evidence items for a given gene symbol.

Args:
    symbol (str): Target gene symbol, e.g., "ALK".
    limit (int | None): Max evidence items to retrieve.
"""

Testing Rules

Place tests under tests/ with filenames like test_<module>.py

Use pytest fixtures for setup/cleanup

Mock API calls using monkeypatch (no live CIViC hits during tests)

Avoid touching real data paths; use tmp_path for all file I/O

Example:

```python
def test_normalize_label(monkeypatch):
    monkeypatch.setattr(utils, "normalize_label", lambda x: "alk")
    assert utilss.normalize_label("ALK") == "alk" 
```


Run the full suite:

```bash
pytest -v 
```

Git & Commit Conventions

Branch naming

feature/<short-description>
fix/<short-description>
test/<short-description>


Commit style

feat: add dim_gene_variant loader
fix: handle null therapies in evidence_link
test: add unit test for normalize_label


Every commit should be atomic — one change, one purpose.

Pull Requests

Fork the repository

Create a feature branch

Add or update tests

Run pytest -v and ensure all pass

Open a pull request with:

A short description of the change

Before/after behavior summary

Any new dependencies introduced

Anti-Patterns

❌ Hardcoding paths (use config.data_dir() or config.default_db_path())

❌ Direct print() calls inside ETL or SQL modules

❌ Committing .env, .sqlite, or large JSON files

❌ Running pytest on live CIViC API endpoints


Roadmap Contributions

If you want to help expand ALKfred:

Add BioPortal MONDO/NCIT cross-reference ingestion

Extend to multi-gene CIViC fetch

Improve CLI querying with structured subcommands

Refactor dim loaders for generic reuse

Propose ideas in the Discussions tab before starting major rewrites.


License

ALKfred is released under the GNU General Public License v3.0 (GPL-3.0).
By contributing, you agree that your code will be distributed under the same license.