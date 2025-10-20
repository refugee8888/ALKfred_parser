import argparse
from alkfred import config
from alkfred.etl import civic_curate, civic_fetch
import sqlite3
import logging
from pathlib import Path
import sys


logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(description="Welcome to ALKfred")


if __name__ == "__main__":
    
    parser.add_argument("--overwrite", action="store_true", help="Refetch and rebuild JSONs even if they exist")
    parser.add_argument("--limit", type = int)
    parser.add_argument("--source", choices=["curated", "civic"], required=True)
    parser.add_argument("--db", type=Path, default=config.default_db_path())
    parser.add_argument("--curated", type=Path, default=config.data_dir() / "curated_resistance_db.json")
    parser.add_argument("--raw", type=Path, default=config.data_dir() / "civic_raw_evidence_db.json")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    
    try:
        # ... argparse as you have it ...
        logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

        if args.source == "civic":
            items = civic_fetch.fetch_civic_evidence(
                symbol="ALK",
                raw_path=args.raw,
                overwrite=args.overwrite,
                limit=args.limit,           # <-- actually use it
            )
            civic_curate.curate_civic(items, curated_path=args.curated)
        else:
            if not Path(args.curated).exists():
                logger.error("Curated file not found: %s (run with --source civic first)", args.curated)
                sys.exit(2)

        # Build — ensure these functions consume the same paths
        config.apply_schema(db_path=args.db)
        config.apply_dim_disease(db_path=args.db, curated_path=args.curated)
        config.apply_dim_gene_variant(db_path=args.db, curated_path=args.curated)
        config.apply_dim_therapy(db_path=args.db, curated_path=args.curated)
        config.apply_dim_evidence(db_path=args.db, raw_path=args.raw)
        config.apply_evidence_link(db_path=args.db, raw_path=args.raw)   # <-- critical
        config.apply_fact_evidence(db_path=args.db)

        logger.info("Database ready: %s", args.db)
    except Exception as e:
        logger.exception("Build failed")
        sys.exit(1)

    
   

    









