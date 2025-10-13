# sql_fact_evidence_build_from_dims.py
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("alkfred.db")
UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

FACT_DDL = """
CREATE TABLE IF NOT EXISTS fact_evidence (
  fact_id         TEXT PRIMARY KEY,
  eid             INTEGER NOT NULL,
  variant_id      TEXT NOT NULL,
  doid            TEXT NOT NULL,
  ncit_id         TEXT NOT NULL,
  direction       TEXT NOT NULL DEFAULT 'RESISTANT',
  significance    TEXT NOT NULL DEFAULT 'RESISTANCE',
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
IDX1 = "CREATE INDEX IF NOT EXISTS idx_fact_doid_dir ON fact_evidence(doid, direction);"
IDX2 = "CREATE INDEX IF NOT EXISTS idx_fact_variant ON fact_evidence(variant_id);"
IDX3 = "CREATE INDEX IF NOT EXISTS idx_fact_therapy ON fact_evidence(ncit_id);"
IDX4 = "CREATE INDEX IF NOT EXISTS idx_fact_eid ON fact_evidence(eid);"

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def main():
    conn = sqlite3.connect(DB_PATH.as_posix())
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # sanity: required tables
    for t in ("dim_disease","dim_gene_variant","dim_therapy","dim_evidence","evidence_link"):
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,))
        row = cur.fetchone()
        if not row:
            raise RuntimeError(f"Missing required table: {t}")

    # ensure fact and indexes
    cur.execute(FACT_DDL)
    cur.execute(FACT_UNIQUE)
    cur.execute(IDX1); cur.execute(IDX2); cur.execute(IDX3); cur.execute(IDX4)
    conn.commit()

    # pull only rows that are valid by dims and meet evidence filters
    # we keep direction/significance from dim_evidence to stay faithful to source
    cur.execute("""
        SELECT el.eid, el.doid, el.variant_id, el.ncit_id,
               UPPER(COALESCE(de.direction,''))   AS direction,
               UPPER(COALESCE(de.significance,'')) AS significance
        FROM evidence_link el
        JOIN dim_evidence   de ON de.eid       = el.eid
        JOIN dim_disease    d  ON d.doid       = el.doid
        JOIN dim_gene_variant v ON v.variant_id = el.variant_id
        JOIN dim_therapy    t  ON t.ncit_id    = el.ncit_id
        WHERE UPPER(COALESCE(de.direction,''))   = 'SUPPORTS'
          AND UPPER(COALESCE(de.significance,'')) = 'RESISTANCE'
    """)
    rows = cur.fetchall()
    if not rows:
        print("No eligible rows found from dims+link (check evidence_link and dim_evidence filters).")
        return

    payload = []
    now_iso = utc_now_iso()
    for eid, doid, variant_id, ncit_id, direction, significance in rows:
        # deterministic PK over the tuple
        key = f"{eid}|{doid}|{variant_id}|{ncit_id}"
        fact_id = str(uuid.uuid5(UUID_NAMESPACE, key))
        payload.append((fact_id, eid, variant_id, doid, ncit_id, direction, significance, now_iso, RUN_ID))

    cur.executemany("""
        INSERT OR IGNORE INTO fact_evidence
            (fact_id, eid, variant_id, doid, ncit_id, direction, significance, created_at_utc, run_id)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, payload)
    conn.commit()

    # report
    print(f"Upserted {cur.rowcount} fact rows this run.")
    cur.execute("SELECT COUNT(*) FROM fact_evidence")
    total = cur.fetchone()[0]
    print(f"Total fact rows: {total}")

    # optional peek
    cur.execute("""
        SELECT eid, doid, variant_id, ncit_id, direction, significance
        FROM fact_evidence
        ORDER BY eid, variant_id, ncit_id
        LIMIT 10
    """)
    for r in cur.fetchall():
        print(r)

    conn.close()

if __name__ == "__main__":
    main()
