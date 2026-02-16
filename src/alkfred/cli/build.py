import argparse
from alkfred import config
from alkfred.etl import civic_fetch
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Welcome to ALKfred")
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Refetch and rebuild JSONs even if they exist",
    )
    p.add_argument("--limit", type=int)
    p.add_argument("--oncogene", type=str, default=None, help="Target oncogene symbol")
    p.add_argument("--source", choices=["civic", "test"], required=True)
    p.add_argument(
        "--civic", type=Path, default=config.data_dir() / "civic_raw_evidence_db.json"
    )
    p.add_argument(
        "--testcivic", type=Path, default=config.data_dir() / "civic_test.json"
    )
    p.add_argument("--verbose", action="store_true")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    if args.source == "civic":

        civic_fetch.fetch_civic_evidence(
            oncogene=args.oncogene,
            civic_path=args.civic,
            overwrite=args.overwrite,
            limit=args.limit,
        )
    #before running the build make sure the right usernames and connection
    #credentials are set
    config.apply_schema()
    config.apply_raw_evidence()
    config.apply_raw_disease()
    config.apply_raw_molecular_profile()
    config.apply_raw_gene_variant()
    config.apply_raw_therapy()

    logger.info("Database ready")


if __name__ == "__main__":

    raise SystemExit(main())
