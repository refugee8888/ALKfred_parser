# fact_evidence_build_from_dims.py
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from alkfred import config
import logging

DB_PATH = config.default_db_path()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main():
    conn = config.get_conn(DB_PATH.as_posix())
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    logger = logging.getLogger(__name__)
    
    logger.info("Table fact_evidence created or already exists in %s", DB_PATH)

    # sanity: required tables
    for t in (
        "civic_dim_disease",
        "civic_dim_gene_variant",
        "civic_dim_therapy",
        "civic_dim_evidence",
        "civic_dim_molecular_profile",
        "evidence_link",
        "fact_evidence",
    ):
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,)
        )
        if not cur.fetchone():
            raise RuntimeError(f"Missing required table: {t}")

    cur.execute(
        """
        INSERT INTO fact_evidence (
        eid, doid, molecular_profile_id, variant_id, ncit_id,
        direction, significance, pub_year
        )
        SELECT
        el.eid,
        el.doid,
        el.molecular_profile_id,
        el.variant_id,
        el.ncit_id,
        el.direction,
        el.significance,
        el.pub_year
        FROM evidence_link el
        GROUP BY el.eid, el.doid, el.molecular_profile_id, el.variant_id, el.ncit_id
        ON CONFLICT(eid, doid, molecular_profile_id, variant_id, ncit_id) DO UPDATE SET
        direction   = excluded.direction,
        significance= excluded.significance,
        pub_year    = excluded.pub_year
    """
    )
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
