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


def apply_stg_evidence():
    print(
        f"Loading /app/src/alkfred/sql/stg_load/civic_stg_evidence.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.stg_load.civic_stg_evidence")


def apply_stg_disease():
    print(
        f"Loading /app/src/alkfred/sql/dim_load/sql_civic_dim_disease_create.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.stg_load.civic_stg_disease")


def apply_stg_molecular_profile():
    print(
        f"Loading /app/src/alkfred/sql/stg_load/civic_stg_molecular_profile.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.stg_load.civic_stg_molecular_profile")


def apply_stg_gene_variant():
    print(
        f"Loading /app/src/alkfred/sql/stg_load/civic_stg_gene_variant.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.stg_load.civic_stg_gene_variant")


def apply_stg_therapy():
    print(
        f"Loading /app/src/alkfred/sql/stg_load/civic_stg_therapy.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.stg_load.civic_stg_therapy")


def apply_dim_disease():

    print(
        f"Loading /app/src/alkfred/sql/dim_load/sql_civic_dim_disease_create.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.dim_load.civic_dim_disease_create")

def apply_dim_molecular_profile():

    print(
        f"Loading /app/src/alkfred/sql/dim_load/sql_civic_dim_molecular_profile.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.dim_load.civic_dim_molecular_profile")


def apply_dim_gene_variant():
    print(
        f"Loading /app/src/alkfred/sql/dim_load/sql_civic_dim_gene_variant.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.dim_load.civic_dim_gene_variant")


def apply_dim_therapy():
    print(
        f"Loading /app/src/alkfred/sql/dim_load/sql_civic_dim_therapy_create.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.dim_load.civic_dim_therapy_create")


def apply_dim_evidence():
    print(
        f"Loading /app/src/alkfred/sql/dim_load/sql_dim_evidence_create.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.dim_load.civic_dim_evidence_create")

def apply_evidence_link():
    print(
        f"Loading /app/src/alkfred/sql/evidence_link_create.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.evidence_link_create")

def apply_fact_evidence(
    db_path: Path | str = default_db_path(),
    raw_path: Path | str = data_dir() / "civic_raw_evidence_db.json",
    oncogene=None,
):
    print(
        f"Loading /app/src/alkfred/sql/sql_evidence_fact_create.py to {default_db_path()}"
    )
    _run_module_main("alkfred.sql.evidence_fact_create")

def postgres_conn():
    conn = psycopg2.connect(
        postgres_key())
    return conn


class UniqueKeyGenerator:

    def __init__(self, initial_keys_list: set() = None):
      
        self.seen_keys: set[str] = initial_keys_list if initial_keys_list is not None else set()

    def generate_key(self) -> str:
        
        while True:
            seed = str(uuid.uuid4())
            new_key = str(uuid.uuid5(UUID_NAMESPACE, seed))
            if new_key not in self.seen_keys:
                self.seen_keys.add(new_key)
                try:
                    with open("data/unique_keys_list.json", "w") as dump:
                        json.dump(list(self.seen_keys), dump, indent= 2)
                except Exception as e:
                    logger.info("Could not save to file %s:", e)
            return new_key

    def get_seen_keys(self)->set():

        return self.seen_keys




   