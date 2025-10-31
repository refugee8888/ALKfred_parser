# evidence_link_populate.py
from __future__ import annotations
import re
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from utils import normalize_label
import api_calls  # expects: fetch_civic_molecular_profile(mp_name) -> list[{"variant": str, "ca_id": str|None}]
from alkfred import config

# ----------------------------
# Config
# ----------------------------
DB_PATH = config.default_db_path()
RAW_JSON_PATH = Path("data/civic_raw_evidence_db.json")  # list of CIViC evidence nodes
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("evidence_link_populate")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


LINK_INSERT_SQL = """
INSERT OR IGNORE INTO evidence_link
  (eid, doid, variant_id, therapy_id, mp_name, therapy_label, created_at_utc, run_id)
VALUES (?,?,?,?,?,?,?,?)
"""

# ----------------------------
# Preload read-only caches
# ----------------------------
def preload_dim_caches(cur: sqlite3.Cursor):
    # diseases
    cur.execute("SELECT doid FROM dim_disease")
    seen_doid: set[str] = {r[0] for r in cur.fetchall() if r[0]}

    # therapies → we only READ what's there; no ID generation here
    cur.execute("SELECT therapy_id, ncit_id, label_therapy_norm FROM dim_therapy")
    therapy_id_by_ncit: dict[str, str] = {}
    therapy_id_by_norm: dict[str, str] = {}
    for therapy_id, ncit_id, label_therapy_norm in cur.fetchall():
        if ncit_id:
            therapy_id_by_ncit[str(ncit_id)] = therapy_id
        if label_therapy_norm:
            therapy_id_by_norm[label_therapy_norm] = therapy_id

    # variants
    cur.execute("SELECT variant_id FROM dim_gene_variant")
    variant_ids: set[str] = {r[0] for r in cur.fetchall() if r[0]}

    # evidence
    cur.execute("SELECT eid FROM dim_evidence")
    evidence_eids: set[int] = {int(r[0]) for r in cur.fetchall() if r[0] is not None}

    return seen_doid, therapy_id_by_ncit, therapy_id_by_norm, variant_ids, evidence_eids


# ----------------------------
# Minimal, defensive upserts (dimensions)
# ----------------------------
def upsert_disease_min(cur: sqlite3.Cursor, doid: str, label_display: str | None, seen_doid: set[str]) -> None:
    if not doid or doid in seen_doid:
        return
    label_display = (label_display or "").strip() or doid
    label_disease_norm = normalize_label(label_display)
    cur.execute(
        "INSERT OR IGNORE INTO dim_disease "
        "(doid, label_display, label_disease_norm, synonyms_json, mondo_id, ncit_id, lineage_json) "
        "VALUES (?, ?, ?, '[]', NULL, NULL, '[]')",
        (doid, label_display, label_disease_norm),
    )
    seen_doid.add(doid)


def _therapy_uuid_seed(ncit_id: str | None, label_norm: str) -> str:
    # Deterministic seed with entity prefix to avoid collisions with other entities
    return f"therapy|{ncit_id}" if ncit_id else f"therapy|{label_norm}"




def upsert_therapy_min(
    cur: sqlite3.Cursor,
    name: str,
    ncit_id: str | None,
    therapy_id_by_ncit: dict[str, str],
    therapy_id_by_norm: dict[str, str],
) -> str | None:
    """
    Always returns the internal therapy_id (or None on hard failure).
    Resolution order:
      1) by ncit_id via cache
      2) by normalized label via cache (+ attach ncit if newly provided)
      3) insert new (deterministic therapy_id via uuid5 over seed)
    """

    label_display = (name or "").strip()
    label_norm = normalize_label(label_display)
    if not label_norm:
        return None

    # 1) Found by NCIt
    if ncit_id and ncit_id in therapy_id_by_ncit:
        return therapy_id_by_ncit[ncit_id]

    # 2) Found by normalized label
    if label_norm in therapy_id_by_norm:
        therapy_id = therapy_id_by_norm[label_norm]
        # Attach NCIt if we have it now and it's not set yet
        if ncit_id:
            cur.execute("SELECT ncit_id FROM dim_therapy WHERE therapy_id = ?", (therapy_id,))
            row = cur.fetchone()
            if row and (row[0] is None):
                cur.execute("UPDATE dim_therapy SET ncit_id = ? WHERE therapy_id = ?", (ncit_id, therapy_id))
            therapy_id_by_ncit[ncit_id] = therapy_id
        return therapy_id

    # 3) Insert new
    seed = _therapy_uuid_seed(ncit_id, label_norm)
    therapy_id = str(uuid.uuid5(UUID_NAMESPACE, seed))
    cur.execute(
        "INSERT OR IGNORE INTO dim_therapy "
        "(therapy_id, ncit_id, label_display, label_therapy_norm, synonyms_json, rxnorm_id, id_combo, combo_parts_json, class_ids_json) "
        "VALUES (?, ?, ?, ?, '[]', NULL, 0, NULL, NULL)",
        (therapy_id, ncit_id, label_display, label_norm),
    )
    if ncit_id:
        therapy_id_by_ncit[ncit_id] = therapy_id
    therapy_id_by_norm[label_norm] = therapy_id
    return therapy_id

def _looks_like_gene(s: str | None) -> bool:
        return bool(s and re.fullmatch(r"[A-Z0-9]{2,}", s))

def upsert_variant_min(
    cur: sqlite3.Cursor,
    variant_label: str | None,
    civic_ca_id: str | None,
    variant_ids: set[str],
    gene_symbol_default: str | None,
) -> str | None:
    """
    Returns variant_id. Uses CIViC CA if available; otherwise deterministic UUIDv5 over normalized label.
    Ensures a row exists in dim_gene_variant.
    """
    gene_from_label = (variant_label or "").strip().split(" ")[0].upper()
    gene_candidate = gene_from_label if _looks_like_gene(gene_from_label) else None

    # prefer explicit default (from component or --oncogene) over label guess
    gene_symbol = (gene_symbol_default or gene_candidate or "").strip().upper()
    if not _looks_like_gene(gene_symbol):
        return None
    label_display = (variant_label or "").strip()
    label_norm = normalize_label(label_display)
    if civic_ca_id:
        variant_id = civic_ca_id
    elif label_norm:
        variant_id = str(uuid.uuid5(UUID_NAMESPACE, f"variant|{label_norm}"))
    else:
        return None

    if variant_id in variant_ids:
        return variant_id

    cur.execute(
        "INSERT OR IGNORE INTO dim_gene_variant "
        "(variant_id, civic_ca_id, hgnc_id, gene_symbol, label_display, label_gene_variant_norm, hgvs_p, hgvs_c, aliases_json, confidence) "
        "VALUES (?, ?, NULL, ?, ?, ?, NULL, NULL, '[]', NULL)",
        (variant_id, civic_ca_id, gene_symbol_default, label_display or variant_id, label_norm or variant_id),
    )
    variant_ids.add(variant_id)
    return variant_id


def upsert_dim_evidence_min(cur: sqlite3.Cursor, ei: dict, evidence_eids: set[int]) -> None:
    eid = ei.get("id")
    if eid is None:
        return
    eid = int(eid)
    if eid in evidence_eids:
        return

    src = ei.get("source") or {}
    source_json = json.dumps(src)
    direction   = (ei.get("evidenceDirection") or "").strip().upper()
    significance= (ei.get("significance") or "").strip().upper()
    ev_level = (ei.get("evidenceLevel") or "").strip().upper()
    ev_type = (ei.get("evidenceType") or "").strip().upper()
    rating = ei.get("evidenceRating")
    status = (ei.get("status") or "").strip().upper() or None
    pmids = []
    if src.get("citationId"):
        pmids.append(str(src.get("citationId")))
    pmids_json = json.dumps(pmids)
    pub_year = src.get("publicationYear") or ei.get("publicationYear")
    description = (ei.get("description") or "").strip() or None
    now = utc_now_iso()

    cur.execute(
        "INSERT OR IGNORE INTO dim_evidence "
        "(eid, source_json, direction, significance, evidence_level, evidence_type, rating, status, pmids_json, pub_year, description, created_at_utc, updated_at_utc) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (eid, source_json, direction, significance, ev_level, ev_type, rating, status, pmids_json, pub_year, description, now, None),
    )
    evidence_eids.add(eid)

def create_links(db_path = config.default_db_path(), raw_path= Path("data/civic_raw_evidence_db.json"), oncogene = "") -> None:
    
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw CIViC JSON not found: {raw_path}")
    with raw_path.open("r", encoding="utf-8") as f:
        nodes = json.load(f)
   
    if not isinstance(nodes, list):
        raise ValueError("civic_raw_evidence_db.json must be a list of evidence nodes")

    conn = config.get_conn(db_path.as_posix())
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # Caches from dims
    seen_doid, id_by_ncit, id_by_norm, variant_ids, evidence_eids = preload_dim_caches(cur)

    components_cache: dict[str, list[dict]] = {}

    inserted_links = 0
    skipped_direction = 0
    skipped_missing_bits = 0
    skipped_no_therapy_match = 0
    skipped_no_components = 0

    batch: list[tuple] = []
    BATCH = 500

    for ei in nodes:
        try:
            eid = ei.get("id")
            if eid is None:
                continue
            eid = int(eid)

            disease = ei.get("disease") or {}
            doid = disease.get("doid")
            mp = ei.get("molecularProfile") or {}
            mp_id = mp.get("id")
            mp_name = (mp.get("name") or "").strip()
            therapies = ei.get("therapies") or []

            mp_key = mp_id if mp_id is not None else mp_name

            if not doid or not mp_name or not therapies:
                skipped_missing_bits += 1
                continue

            # Ensure minimal dims exist
            upsert_dim_evidence_min(cur, ei, evidence_eids)
            upsert_disease_min(cur, doid, disease.get("name"), seen_doid)

            # Resolve therapy → therapy_id (always)
            resolved_therapies: list[tuple[str, str]] = []  # (therapy_id, display_name)
            for t in therapies:
                name = (t.get("name") or "").strip()
                ncit = t.get("ncitId") or t.get("ncit_id")
                therapy_id = upsert_therapy_min(cur, name, ncit, id_by_ncit, id_by_norm)
                if therapy_id:
                    resolved_therapies.append((therapy_id, name))
            if not resolved_therapies:
                skipped_no_therapy_match += 1
                continue

            # Resolve molecular profile → component variants
            if mp_key not in components_cache:
                try:
                    if mp_id is not None:
                        # new, ID-based fetch (robust)
                        components_cache[mp_key] = mp or []
                    else:
                        # fallback, name-based (legacy)
                        components_cache[mp_key] = mp or []
                except Exception as e:
                    log.debug("Component fetch failed for %r: %s", mp_key, e)
                    components_cache[mp_key] = []

            comps = components_cache[mp_key]
            if not comps:
                skipped_no_components += 1
                continue

            # Ensure variant rows exist, then cross-product links
            # for c in comps:
            for v in comps.get("variants" or []):
                vlabel = (v.get("name") or "").strip()
                ca_id = v.get("alleleRegistryId") or None
                variant_id = upsert_variant_min(cur, vlabel, ca_id, variant_ids, gene_symbol_default=oncogene)
                if not variant_id:
                    continue

                for therapy_id, disp_name in resolved_therapies:
                    batch.append((eid, doid, variant_id, therapy_id, mp_name, disp_name, utc_now_iso(), RUN_ID))

            # Batch insert
            if len(batch) >= BATCH:
                cur.executemany(LINK_INSERT_SQL, batch)
                inserted_links += len(batch)
                batch.clear()
                conn.commit()

        except Exception:
            log.exception("Error processing eid=%s", ei.get("id"))

    # Flush remaining
    if batch:
        cur.executemany(LINK_INSERT_SQL, batch)
        inserted_links += len(batch)
        batch.clear()
        conn.commit()

    log.info("Inserted links: %d | skipped_direction=%d skipped_missing=%d skipped_no_therapy=%d skipped_no_components=%d",
             inserted_links, skipped_direction, skipped_missing_bits, skipped_no_therapy_match, skipped_no_components)

    conn.close()
# ----------------------------
# Main populate
# ----------------------------
def main():
     create_links(config.default_db_path(), Path("data/civic_raw_evidence_db.json"), oncogene="ALK")

    


if __name__ == "__main__":
    main()
   