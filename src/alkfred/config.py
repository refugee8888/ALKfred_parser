import dotenv
import os

from pathlib import Path
import sqlite3


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
    d = data_dir() / "alkfred"
    d.mkdir(parents=True, exist_ok=True)
    return d

def env_path() -> Path:
    # Return the absolute environment directory
    d = repo_root() / ".env"
    return d

def load_env() -> None:
    # Load the environment file
    path = env_path() / ".env"
    if not path.exists():
        raise FileNotFoundError(f"Environment file not found at {env_path}")
    dotenv.load_dotenv(path, override=False)

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

def norm_general_use(text: str) -> str:
    # Normalize the text for general use
    return text.lower().strip()


    

    