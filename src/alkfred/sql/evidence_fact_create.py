# fact_evidence_build_from_dims.py
from __future__ import annotations

from datetime import datetime, timezone
from alkfred import config


DB_PATH = config.default_db_path()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main():
    conn = config.postgres_conn()

    cur = conn.cursor()

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
        ON CONFLICT(eid, doid, molecular_profile_id, variant_id) DO UPDATE SET
        direction   = excluded.direction,
        significance= excluded.significance,
        pub_year    = excluded.pub_year
    """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
