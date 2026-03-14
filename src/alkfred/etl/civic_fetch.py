import api_calls
import civic_parser
from alkfred import config
from pathlib import Path
from typing import Optional
import json
import logging

log = logging.getLogger(__name__)


def fetch_civic_evidence(
    oncogene=None,
    civic_path=None,
    overwrite=False,
    limit: Optional[int] = None,
    logger=None,
):
    log_ = logger or log

    if civic_path is None:
        civic_path = config.data_dir() / "civic_raw_evidence_db.json"
    civic_path = Path(civic_path)

    if civic_path.exists() and not overwrite:
        log_.info("Using cached CIViC payload at %s (overwrite=False)", civic_path)
        with civic_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    # Fetch CIViC evidence
    log_.info("Fetching all CIViC ACCEPTED evidence items...")
    all_items = api_calls.fetch_civic_all_evidence_items(logger=log_)
    log_.info("Filtering evidence items for oncogene=%s ...", oncogene)
    filtered = []
    for ei in all_items:
        if not ei or not isinstance(ei, dict):
            continue
        mp = ei.get("molecularProfile")

        if not mp:
            continue
        mp_name = mp.get("name", "")

        if civic_parser.gene_in_molecular_profile(mp_name, oncogene):
            filtered.append(ei)
            if limit is not None and len(filtered) >= limit:
                break

    civic_path.parent.mkdir(parents=True, exist_ok=True)

    config.save_to_json(filtered, path=civic_path)
    log_.info(
        "Saved filtered payload | oncogene=%s | rows=%s | path=%s",
        oncogene,
        len(filtered),
        civic_path,
    )

    return filtered


def fetch_civic_all_evidence(
    civic_path=None,
    overwrite=False,
    logger=None,
):
    log_ = logger or log

    if civic_path is None:
        civic_path = config.data_dir() / "civic_raw_evidence_db.json"
    civic_path = Path(civic_path)

    if civic_path.exists() and not overwrite:
        log_.info("Using cached CIViC payload at %s (overwrite=False)", civic_path)
        with civic_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    log_.info("Fetching full CIViC ACCEPTED evidence dataset...")
    all_items = api_calls.fetch_civic_all_evidence_items(logger=log_)

    civic_path.parent.mkdir(parents=True, exist_ok=True)
    config.save_to_json(all_items, path=civic_path)
    log_.info(
        "Saved full payload | rows=%s | path=%s",
        len(all_items),
        civic_path,
    )

    return all_items
