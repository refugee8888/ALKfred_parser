from ast import main
import json
from pdb import run
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import sqlite3
import importlib

logging.basicConfig(
    level=logging.INFO,  # or DEBUG to also see debug() messages
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def _run_module_main(dotted: str):
    mod = importlib.import_module(dotted)
    if hasattr(mod, "main"):
        mod.main()
    else:
        raise RuntimeError(f"{dotted} has no main()")

def repo_root() -> Path:
    # Return the abosulte repo root
    return Path(__file__).resolve().parents[2]

def data_dir() -> Path:
    # Return the absolute data directory
    d = repo_root() / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d

def default_db_path() -> Path:
    # Return the absolute default database path
    d = data_dir() / "alkfred.sqlite"
    return d

def env_path() -> Path:
    # Return the absolute environment directory
    d = repo_root() / ".env"
    return d

def load_env() -> None:
    # Load the environment file
    path = env_path()
    if not path.exists():
        raise FileNotFoundError(f"Environment file not found at {path}")
    load_dotenv(path, override=False)

def get_env(key: str, required: bool = True) -> str | None:
    # Get the environment variable
    val = os.getenv(key)
    if required and not val:
        raise EnvironmentError(f"Environment variable {key} is not set")
        
    return val

def bioportal_api_key() -> str:
    # Get the Bioportal API key
    return get_env("BIOPORTAL_API_KEY", required=True)

def openai_api_key() -> str:
    # Get the OpenAI API key
    return get_env("OPENAI_API_KEY", required=True)

def get_conn(db_path: str | Path | None) -> sqlite3.Connection:
    # Get a connection to the database
    if db_path is None:
        db_path = default_db_path()
    conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    
    return conn

def norm(text: str) -> str:
    # Normalize the text for general use
    return text.lower().strip()

def save_to_json(data, path) -> json:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_from_json(path) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    return data

def apply_schema():
    import sqlite3
    schema_path = "src/alkfred/sql/schema.sql"
    db_path = default_db_path()
    print(f"Applying schema from {schema_path} to {db_path}")
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def apply_dim_disease():
    print(f"Loading src/sql_civic_dim_disease_create.py to {default_db_path()}")
    _run_module_main("sql_civic_dim_disease_create")

def apply_dim_gene_variant():
    print(f"Loading src/sql_civic_dim_gene_variant.py to {default_db_path()}")
    _run_module_main("sql_civic_dim_gene_variant")

def apply_dim_therapy():
    print(f"Loading src/sql_civic_dim_therapy_create.py to {default_db_path()}")
    _run_module_main("sql_civic_dim_therapy_create")

def apply_dim_evidence():
    print(f"Loading src/sql_dim_evidence_create.py to {default_db_path()}")
    _run_module_main("sql_dim_evidence_create")

def apply_evidence_link():
    print(f"Loading src/sql_evidence_link_create.py to {default_db_path()}")
    _run_module_main("sql_evidence_link_create")

def apply_fact_evidence():
    print(f"Loading src/sql_evidence_fact_create.py to {default_db_path()}")
    _run_module_main("sql_evidence_fact_create")

    