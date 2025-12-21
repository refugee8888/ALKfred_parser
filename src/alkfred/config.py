import json
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import sqlite3
import importlib
from typing import Any
from datetime import datetime, timezone
import uuid
import psycopg2

logging.basicConfig(
    level=logging.INFO,  # or DEBUG to also see debug() messages
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)
UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")


def _run_module_main(dotted: str):
    mod = importlib.import_module(dotted)
    if hasattr(mod, "main"):
        mod.main()
    else:
        raise RuntimeError(f"{dotted} has no main()")


def repo_root() -> Path:
    # Return the abosulte repo root
    return Path(__file__).resolve().parents[2]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def data_dir() -> Path:
    # Return the absolute data directory
    d = repo_root() / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def default_db_path() -> Path:
    # Return the absolute default database path
    d = data_dir() / "alkfred.sqlite"
    return d


def raw_json_list_to_dict(path: Path) -> dict[Any, Any]:
    raw_dict = {index: value for index, value in enumerate(load_from_json(path))}
    return raw_dict


def env_path() -> Path:
    # Return the absolute environment directory
    d = repo_root() / "/app/src/.env"
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

    return get_env("BIOPORTAL_API_KEY", required=True)


def postgres_key() -> str:
    return get_env("PG_DSN", required=True)


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


def apply_schema(db_path: Path):
    import sqlite3

    schema_path = "src/alkfred/sql/schema.sql"

    print(f"Applying schema from {schema_path} to {db_path}")
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def apply_raw_evidence():
    print("Loading /app/src/alkfred/sql/raw_load/civic_raw_evidence.py")
    _run_module_main("alkfred.sql.raw_load.civic_raw_evidence")


def apply_raw_disease():
    print("Loading /app/src/alkfred/sql/raw_load/civic_raw_disase.py")
    _run_module_main("alkfred.sql.raw_load.civic_raw_disease")


def apply_raw_molecular_profile():
    print("Loading /app/src/alkfred/sql/raw_load/civic_raw_molecular_profile.py")
    _run_module_main("alkfred.sql.raw_load.civic_raw_molecular_profile")


def apply_raw_gene_variant():
    print("Loading /app/src/alkfred/sql/raw_load/civic_raw_gene_variant.py")
    _run_module_main("alkfred.sql.raw_load.civic_raw_gene_variant")


def apply_raw_therapy():
    print(
        "Loading /app/src/alkfred/sql/raw_load/civic_raw_therapy.py"
    )
    _run_module_main("alkfred.sql.raw_load.civic_raw_therapy")


def postgres_conn():
    conn = psycopg2.connect(postgres_key())
    return conn
