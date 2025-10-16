# fact_evidence_build_from_dims.py
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from alkfred import config

DB_PATH = config.default_db_path()
UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main():
    conn = config.get_conn(DB_PATH.as_posix())
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # sanity: required tables
    for t in ("dim_disease", "dim_gene_variant", "dim_therapy", "dim_evidence", "evidence_link", "fact_evidence"):
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,))
        if not cur.fetchone():
            raise RuntimeError(f"Missing required table: {t}")

    # Build facts from link + dims, preserving evidence filters
    cur.execute("""
        SELECT el.eid, el.doid, el.variant_id, el.therapy_id,
               UPPER(COALESCE(de.direction,''))   AS direction,
               UPPER(COALESCE(de.significance,'')) AS significance
        FROM evidence_link el
        JOIN dim_evidence   de ON de.eid        = el.eid
        JOIN dim_disease    d  ON d.doid        = el.doid
        JOIN dim_gene_variant v ON v.variant_id = el.variant_id
        JOIN dim_therapy    t  ON t.therapy_id  = el.therapy_id
        WHERE UPPER(COALESCE(de.direction,''))   = 'SUPPORTS'
          AND UPPER(COALESCE(de.significance,'')) = 'RESISTANCE'
    """)
    rows = cur.fetchall()
    if not rows:
        print("No eligible rows found (check evidence_link and dim_evidence filters).")
        conn.close()
        return

    payload = []
    now_iso = utc_now_iso()
    for eid, doid, variant_id, therapy_id, direction, significance in rows:
        # deterministic PK over the tuple
        key = f"{eid}|{doid}|{variant_id}|{therapy_id}"
        fact_id = str(uuid.uuid5(UUID_NAMESPACE, key))
        payload.append((fact_id, eid, variant_id, doid, therapy_id, direction, significance, now_iso, RUN_ID))

    cur.executemany("""
        INSERT OR IGNORE INTO fact_evidence
            (fact_id, eid, variant_id, doid, therapy_id, direction, significance, created_at_utc, run_id)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, payload)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
