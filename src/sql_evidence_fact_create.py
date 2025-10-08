# sql_evidence_fact_create.py
from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from utils import normalize_label  # your normalizer
import api_calls  # for fetch_civic_molecular_profile

# ----------------------------
# Config
# ----------------------------
DB_PATH = Path("alkfred.db")
RAW_JSON_PATH = Path("data/civic_raw_evidence_db.json")  # list of CIViC evidence nodes
UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

LINK_INSERT_SQL = """
INSERT OR IGNORE INTO evidence_link
  (eid, doid, variant_id, ncit_id, mp_name, therapy_label, created_at_utc, run_id)
VALUES (?,?,?,?,?,?,?,?)
"""

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

# ----------------------------
# Ensure fact table
# ----------------------------
FACT_DDL = """
CREATE TABLE IF NOT EXISTS fact_evidence (
  fact_id         TEXT PRIMARY KEY,
  eid             INTEGER NOT NULL,
  variant_id      TEXT NOT NULL,
  doid            TEXT NOT NULL,
  ncit_id         TEXT NOT NULL,
  created_at_utc  TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  run_id          TEXT,
  FOREIGN KEY (eid)        REFERENCES dim_evidence(eid),
  FOREIGN KEY (variant_id) REFERENCES dim_gene_variant(variant_id),
  FOREIGN KEY (doid)       REFERENCES dim_disease(doid),
  FOREIGN KEY (ncit_id)    REFERENCES dim_therapy(ncit_id)
);
"""
FACT_UNIQUE = """
CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_tuple
ON fact_evidence(eid, doid, variant_id, ncit_id);
"""
IDX_FACT_EID = "CREATE INDEX IF NOT EXISTS idx_fact_eid ON fact_evidence(eid);"
IDX_FACT_DOID = "CREATE INDEX IF NOT EXISTS idx_fact_doid ON fact_evidence(doid);"
IDX_FACT_VARIANT = "CREATE INDEX IF NOT EXISTS idx_fact_variant ON fact_evidence(variant_id);"
IDX_FACT_THERAPY = "CREATE INDEX IF NOT EXISTS idx_fact_therapy ON fact_evidence(ncit_id);"

# ----------------------------
# Caches from dims to avoid per-row queries
# ----------------------------
def preload_dim_caches(cur: sqlite3.Cursor):
    # Diseases
    cur.execute("SELECT doid FROM dim_disease")
    seen_doid = {r[0] for r in cur.fetchall() if r[0]}

    # Therapies
    cur.execute("SELECT ncit_id, label_norm FROM dim_therapy")
    therapy_by_ncit = set()
    therapy_by_norm = {}
    for ncit_id, label_norm in cur.fetchall():
        if ncit_id:
            therapy_by_ncit.add(ncit_id)
        if label_norm:
            therapy_by_norm[label_norm] = ncit_id

    # Variants
    cur.execute("SELECT variant_id FROM dim_gene_variant")
    variant_ids = {r[0] for r in cur.fetchall() if r[0]}

    # Evidence (eid) presence
    cur.execute("SELECT eid FROM dim_evidence")
    evidence_eids = {int(r[0]) for r in cur.fetchall() if r[0] is not None}

    return seen_doid, therapy_by_ncit, therapy_by_norm, variant_ids, evidence_eids

# ----------------------------
# Minimal upserts
# ----------------------------
def upsert_disease_min(cur: sqlite3.Cursor, doid: str, label_display: str | None, seen_doid: set):
    if doid in seen_doid:
        return
    label_display = (label_display or "").strip() or f"DOID:{doid}"
    label_norm = normalize_label(label_display)
    cur.execute(
        "INSERT OR IGNORE INTO dim_disease (doid, label_display, label_norm, synonyms_json, mondo_id, ncit_id, lineage_json) "
        "VALUES (?, ?, ?, '[]', NULL, NULL, '[]')",
        (doid, label_display, label_norm),
    )
    seen_doid.add(doid)

def upsert_therapy_min(cur: sqlite3.Cursor, name: str, ncit_id: str | None,
                       therapy_by_ncit: set, therapy_by_norm: dict):
    if ncit_id:
        if ncit_id in therapy_by_ncit:
            return ncit_id
        label_norm = normalize_label(name or "")
        cur.execute(
            "INSERT OR IGNORE INTO dim_therapy (ncit_id, label_display, label_norm, synonyms_json, rxnorm_id, id_combo, combo_parts_json, class_ids_json) "
            "VALUES (?, ?, ?, '[]', NULL, 0, NULL, NULL)",
            (ncit_id, name, label_norm),
        )
        therapy_by_ncit.add(ncit_id)
        therapy_by_norm[label_norm] = ncit_id
        return ncit_id

    # Fallback: resolve by normalized name
    label_norm = normalize_label(name or "")
    resolved = therapy_by_norm.get(label_norm)
    return resolved  # could be None

def upsert_variant_min(cur: sqlite3.Cursor, variant_id: str, label_display: str,
                       variant_ids: set, gene_symbol_default: str = "ALK"):
    if variant_id in variant_ids:
        return
    label_norm = normalize_label(label_display or "")
    # Your schema requires gene_symbol NOT NULL → default to "ALK" for now (short-term assumption).
    cur.execute(
        "INSERT OR IGNORE INTO dim_gene_variant (variant_id, civic_ca_id, hgnc_id, gene_symbol, label_display, label_norm, hgvs_p, hgvs_c, aliases_json, confidence) "
        "VALUES (?, ?, NULL, ?, ?, ?, NULL, NULL, '[]', NULL)",
        (variant_id, variant_id, gene_symbol_default, label_display, label_norm),
    )
    variant_ids.add(variant_id)

def upsert_dim_evidence_min(cur: sqlite3.Cursor, ei: dict, evidence_eids: set):
    eid = int(ei.get("id"))
    if eid in evidence_eids:
        return
    src = ei.get("source") or {}
    source_json = json.dumps(src)
    direction = (ei.get("evidenceDirection") or "").strip().upper()
    significance = (ei.get("significance") or "").strip().upper()
    ev_level = (ei.get("evidenceLevel") or "").strip().upper()
    ev_type = (ei.get("evidenceType") or "").strip().upper()
    rating = ei.get("evidenceRating")
    status = (ei.get("status") or "").strip().upper()
    pmids = []
    if src.get("citationId"):
        pmids.append(str(src.get("citationId")))
    pmids_json = json.dumps(pmids)
    pub_year = src.get("publicationYear") or ei.get("publicationYear")
    description = (ei.get("description") or "").strip() or None
    now = utc_now_iso()
    cur.execute(
        "INSERT OR IGNORE INTO dim_evidence (eid, source_json, direction, significance, evidence_level, evidence_type, rating, status, pmids_json, pub_year, description, created_at_utc, updated_at_utc) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (eid, source_json, direction, significance, ev_level, ev_type, rating, status, pmids_json, pub_year, description, now, None),
    )
    evidence_eids.add(eid)

# ----------------------------
# Main
# ----------------------------
def main():
    if not RAW_JSON_PATH.exists():
        raise FileNotFoundError(f"Raw JSON not found: {RAW_JSON_PATH}")

    with RAW_JSON_PATH.open("r", encoding="utf-8") as f:
        nodes = json.load(f)
    if not isinstance(nodes, list):
        raise ValueError("RAW JSON must be a list of CIViC evidence nodes")

    conn = sqlite3.connect(DB_PATH.as_posix())
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # Ensure fact table + indexes
    cur.execute(FACT_DDL)
    cur.execute(FACT_UNIQUE)
    cur.execute(IDX_FACT_EID)
    cur.execute(IDX_FACT_DOID)
    cur.execute(IDX_FACT_VARIANT)
    cur.execute(IDX_FACT_THERAPY)
    conn.commit()

    # Preload caches
    seen_doid, therapy_by_ncit, therapy_by_norm, variant_ids, evidence_eids = preload_dim_caches(cur)

    components_cache: dict[str, list[dict]] = {}

    inserted_facts = 0
    skipped_direction = 0
    skipped_missing_bits = 0
    skipped_no_therapy_match = 0
    skipped_no_components = 0

    fact_rows_batch = []
    BATCH = 500
    now_iso = utc_now_iso()

    for ei in nodes:
        try:
            eid = ei.get("id")
            if eid is None:
                continue
            eid = int(eid)

            # Filters
            direction = (ei.get("evidenceDirection") or "").strip().upper()
            significance = (ei.get("significance") or "").strip().upper()
            if not (direction == "SUPPORTS" and significance == "RESISTANCE"):
                skipped_direction += 1
                continue

            disease = ei.get("disease") or {}
            doid = disease.get("doid")
            mp = ei.get("molecularProfile") or {}
            mp_name = (mp.get("name") or "").strip()
            therapies = ei.get("therapies") or []

            if not doid or not mp_name or not therapies:
                skipped_missing_bits += 1
                continue

            # Ensure dim_evidence exists
            upsert_dim_evidence_min(cur, ei, evidence_eids)
            # Ensure disease
            upsert_disease_min(cur, doid, disease.get("name"), seen_doid)

            # Resolve therapies -> ncit_id
            resolved_therapies: list[tuple[str, str]] = []  # (ncit_id, display_name)
            for t in therapies:
                name = (t.get("name") or "").strip()
                ncit = t.get("ncitId")
                ncit_id = upsert_therapy_min(cur, name, ncit, therapy_by_ncit, therapy_by_norm)
                if ncit_id:
                    resolved_therapies.append((ncit_id, name))
                else:
                    # no NCIt id and couldn't resolve by normalized name
                    continue
            if not resolved_therapies:
                skipped_no_therapy_match += 1
                continue

            # Resolve molecular profile components -> variant_ids
            if mp_name not in components_cache:
                try:
                    components_cache[mp_name] = api_calls.fetch_civic_molecular_profile(mp_name) or []
                except Exception as e:
                    logging.debug("Component fetch failed for %r: %s", mp_name, e)
                    components_cache[mp_name] = []

            comps = components_cache[mp_name]
            if not comps:
                skipped_no_components += 1
                continue

            # Ensure variants exist in dim_gene_variant (minimal upsert if missing)
            for c in comps:
                label = (c.get("variant") or "").strip()
                ca_id = c.get("ca_id") or None
                if not ca_id and not label:
                    continue
                variant_id = ca_id if ca_id else str(uuid.uuid5(UUID_NAMESPACE, f"var|{label}"))
                upsert_variant_min(cur, variant_id, label or variant_id, variant_ids)

                # Cross-product with all therapies
                for ncit_id, _disp in resolved_therapies:
                    key = f"{eid}|{doid}|{variant_id}|{ncit_id}"
                    fact_id = str(uuid.uuid5(UUID_NAMESPACE, key))
                    fact_rows_batch.append((fact_id, eid, variant_id, doid, ncit_id, now_iso, RUN_ID))

            # Batch insert
            if len(fact_rows_batch) >= BATCH:
                cur.executemany(
                    "INSERT OR IGNORE INTO fact_evidence (fact_id, eid, variant_id, doid, ncit_id, created_at_utc, run_id) "
                    "VALUES (?,?,?,?,?,?,?)",
                    fact_rows_batch
                )
                inserted_facts += cur.rowcount
                fact_rows_batch.clear()
                conn.commit()

        except Exception as e:
            logging.exception("Error processing eid=%s: %s", ei.get("id"), e)

    # Flush remaining
    if fact_rows_batch:
        cur.executemany(
            "INSERT OR IGNORE INTO fact_evidence (fact_id, eid, variant_id, doid, ncit_id, created_at_utc, run_id) "
            "VALUES (?,?,?,?,?,?,?)",
            fact_rows_batch
        )
        inserted_facts += cur.rowcount
        fact_rows_batch.clear()
        conn.commit()

    # Report
    cur.execute("SELECT COUNT(*) FROM fact_evidence")
    total = cur.fetchone()[0]
    logging.info("facts inserted this run: %d; total facts: %d", inserted_facts, total)
    logging.info("skipped (non-RESISTANCE/SUPPORTS): %d", skipped_direction)
    logging.info("skipped (missing doid/mp_name/therapies): %d", skipped_missing_bits)
    logging.info("skipped (no therapy match): %d", skipped_no_therapy_match)
    logging.info("skipped (no components): %d", skipped_no_components)

    # Optional: sample peek
    cur.execute("""
        SELECT eid, doid, variant_id, ncit_id
        FROM fact_evidence
        ORDER BY eid, variant_id, ncit_id
        LIMIT 10
    """)
    for r in cur.fetchall():
        print(r)

    conn.close()

if __name__ == "__main__":
    main()
