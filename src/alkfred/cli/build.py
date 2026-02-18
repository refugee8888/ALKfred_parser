import argparse
import logging
import os
import subprocess
from pathlib import Path
from typing import List, Optional

from prefect import flow, task, get_run_logger

from alkfred import config
from alkfred.etl import civic_fetch

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Welcome to ALKfred")

    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Refetch CIViC JSON even if it exists (does NOT imply dbt full-refresh).",
    )
    p.add_argument("--limit", type=int, default=None)

    # IMPORTANT CHANGE: allow multiple genes
    p.add_argument(
        "--oncogene",
        type=str,
        default=None,
        help="Target oncogene symbol(s). Comma-separated, e.g. ALK,EGFR,ROS1",
    )

    p.add_argument("--source", choices=["civic", "test"], required=True)

    p.add_argument(
        "--civic",
        type=Path,
        default=config.data_dir() / "civic_raw_evidence_db.json",
        help="Canonical CIViC JSON path used by raw loaders.",
    )
    p.add_argument(
        "--testcivic", type=Path, default=config.data_dir() / "civic_test.json"
    )

    # Optional: run dbt automatically
    p.add_argument("--build-dbt", action="store_true", help="Build dbt after raw load.")
    p.add_argument(
        "--full-refresh",
        action="store_true",
        help="Pass --full-refresh to dbt",
    )
    p.add_argument(
        "--dbt-project-dir",
        type=Path,
        default=None,
        help="dbt project dir (default: ./dbt or DBT_PROJECT_DIR env var).",
    )
    p.add_argument(
        "--dbt-profiles-dir",
        type=Path,
        default=None,
        help="Optional dbt profiles dir.",
    )
    p.add_argument(
        "--dbt-select",
        type=str,
        default=None,
        help='Optional dbt selection, e.g. "stg_* dim_* fct_*" or "tag:core".',
    )

    p.add_argument("--verbose", action="store_true")
    return p


def _parse_oncogenes(arg: Optional[str]) -> List[str]:
    if not arg:
        return []
    genes = [x.strip().upper() for x in arg.split(",") if x.strip()]
    # de-dupe preserving order
    out: List[str] = []
    seen = set()
    for g in genes:
        if g not in seen:
            seen.add(g)
            out.append(g)
    return out


@task
def ensure_schema_and_tables() -> None:
    """
    Runs schema apply once + ensures raw tables exist.
    NOTE: schema apply runs psql on dbt_ready_schema.sql.
    """
    log = get_run_logger()
    log.info("Applying schema (idempotent DDL expected)...")
    config.apply_schema()

    log.info("Ensuring raw tables exist and loading modules available...")
    log.info("Schema/tables step complete.")


@task
def fetch_gene_payload(
    oncogene: str, source: str, civic_path: Path, overwrite: bool, limit: Optional[int]
) -> None:
    log = get_run_logger()

    if source != "civic":
        raise ValueError(
            "Only source=civic is supported in this build script right now."
        )

    log.info(f"Fetching CIViC payload for oncogene={oncogene} -> {civic_path}")

    civic_fetch.fetch_civic_evidence(
        oncogene=oncogene,
        civic_path=civic_path,
        overwrite=overwrite,
        limit=limit,
        logger=log,
    )


@task
def load_raw_from_current_json() -> None:
    """
    Calls existing raw-load modules.
    """
    log = get_run_logger()
    log.info("Loading civic_raw_* from canonical JSON path...")

    config.apply_raw_evidence()
    config.apply_raw_disease()
    config.apply_raw_molecular_profile()
    config.apply_raw_gene_variant()
    config.apply_raw_therapy()

    log.info("Raw load complete.")


@task
def build_dbt(
    project_dir: Optional[Path],
    profiles_dir: Optional[Path],
    select: Optional[str],
    full_refresh: bool,
) -> None:
    log = get_run_logger()

    if project_dir is None:
        env_dir = os.getenv("DBT_PROJECT_DIR")
        project_dir = Path(env_dir) if env_dir else Path("./dbt")

    cmd = ["dbt", "build"]
    if full_refresh:
        cmd.append("--full-refresh")
    if select:
        cmd += ["--select", select]

    cmd += ["--project-dir", str(project_dir.resolve())]
    if profiles_dir:
        cmd += ["--profiles-dir", str(profiles_dir.resolve())]

    log.info("Running dbt: %s", " ".join(cmd))

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        log.error("dbt failed.\nSTDOUT:\n%s\nSTDERR:\n%s", proc.stdout, proc.stderr)
        raise RuntimeError("dbt build failed")

    log.info("dbt build succeeded.")


@flow(log_prints=True)
def alkfred_build_flow(
    oncogenes: List[str],
    source: str,
    civic_path: Path,
    overwrite: bool,
    limit: Optional[int],
    build_dbt_flag: bool,
    dbt_project_dir: Optional[Path],
    dbt_profiles_dir: Optional[Path],
    dbt_select: Optional[str],
    full_refresh: bool,
) -> None:
    log = get_run_logger()

    log.info("ALKfred build start | oncogenes=%s", oncogenes)

    # 1) Ensure schema once
    ensure_schema_and_tables()

    # 2) For each gene: fetch -> load raw

    for gene in oncogenes:
        fetch_gene_payload(
            oncogene=gene,
            source=source,
            civic_path=civic_path,
            overwrite=overwrite,
            limit=limit,
        )
        load_raw_from_current_json()

    # 3) dbt optional
    if build_dbt_flag:
        build_dbt(
            project_dir=dbt_project_dir,
            profiles_dir=dbt_profiles_dir,
            select=dbt_select,
            full_refresh=full_refresh,
        )

    log.info("ALKfred build done.")


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    oncogenes = _parse_oncogenes(args.oncogene)
    if not oncogenes:
        # single gene, default to ALK if not provided
        oncogenes = ["ALK" if args.oncogene is None else args.oncogene.upper()]

    civic_path = args.civic if args.source == "civic" else args.testcivic

    alkfred_build_flow(
        oncogenes=oncogenes,
        source=args.source,
        civic_path=civic_path,
        overwrite=args.overwrite,
        limit=args.limit,
        build_dbt_flag=args.build_dbt,
        dbt_project_dir=args.dbt_project_dir,
        dbt_profiles_dir=args.dbt_profiles_dir,
        dbt_select=args.dbt_select,
        full_refresh=args.full_refresh,
    )

    logger.info("Database ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
