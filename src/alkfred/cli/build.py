import argparse
from alkfred import config
from alkfred.etl import civic_curate, civic_fetch
import sqlite3
import logging
from pathlib import Path
import sys



logger = logging.getLogger(__name__)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Welcome to ALKfred")
    p.add_argument("--overwrite", action="store_true", help="Refetch and rebuild JSONs even if they exist")
    p.add_argument("--limit", type = int)
    p.add_argument("--oncogene", type=str)
    p.add_argument("--source", choices=["curated", "civic"], required=True)
    p.add_argument("--db", type=Path, default=config.default_db_path())
    p.add_argument("--curated", type=Path, default=config.data_dir() / "curated_resistance_db.json")
    p.add_argument("--raw", type=Path, default=config.data_dir() / "civic_raw_evidence_db.json")
    p.add_argument("--verbose", action="store_true")
    return p



def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    if args.source == "civic":
    
        items = civic_fetch.fetch_civic_evidence(
            oncogene = args.oncogene,
            raw_path=args.raw,
            overwrite=args.overwrite,
            limit=args.limit,           # <-- actually use it
        )
        civic_curate.curate_civic(items, curated_path=args.curated)
        
    else:
        if not Path(args.curated).exists():
            logger.error("Curated file not found: %s (run with --source civic first)", args.curated)
            sys.exit(2)
    # config.default_db_path = (lambda p=Path(args.db): lambda: p)()
    # config.data_dir        = (lambda p=Path(args.curated).parent: lambda: p)()

    # Build — ensure these functions consume the same paths
    config.apply_schema(db_path=args.db)
    config.apply_dim_disease()
    config.apply_dim_gene_variant()
    config.apply_dim_therapy()
    config.apply_dim_evidence()
    config.apply_evidence_link()   
    config.apply_fact_evidence()

    logger.info("Database ready: %s", args.db)

if __name__ == "__main__":
    
    raise SystemExit(main())   
    
   

    









