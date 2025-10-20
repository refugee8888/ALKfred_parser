import argparse
from pathlib import Path
from alkfred import config
parser = argparse.ArgumentParser(description="Welcome to ALKfred")

def cli_query_commands() -> None:
    
    parser.add_argument("--overwrite", action="store_true", help="Refetch and rebuild JSONs even if they exist"),
    parser.add_argument("--limit", type = int),
    parser.add_argument("--from", choices=["curated", "civic"], required=True),
    parser.add_argument("--db", type=Path, default=config.default_db_path()),
    parser.add_argument("--curated", type=Path, default=config.data_dir() / "curated_resistance_db.json"),
    parser.add_argument("--raw", type=Path, default=config.data_dir() / "civic_raw_evidence_db.json"),
    parser.add_argument("--verbose", action="store_true"),
    args = parser.parse_args()
    





if __name__ == "__main__":
    cli_commands()