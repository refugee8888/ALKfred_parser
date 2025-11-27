from pathlib import Path

from utils import normalize_label
from alkfred import config


JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")


def main():

    conn = config.postgres_conn()
    cur = conn.cursor()

    rows_molecular_profile = []
    cur.execute(
        """SELECT molecular_profile_id, mp_name
                FROM civic_stg_molecular_profile
                """
    )
    for r in cur.fetchall():

        mp_name_norm = normalize_label(r[1])

        rows_molecular_profile.append((r[0], r[1], mp_name_norm))

    cur.executemany(
        """INSERT INTO civic_dim_molecular_profile (
       molecular_profile_id, mp_name, mp_name_norm
        ) VALUES (%s,%s,%s)
        ON CONFLICT(molecular_profile_id) DO UPDATE SET
        mp_name = COALESCE(excluded.mp_name, civic_dim_molecular_profile.mp_name),
        mp_name_norm = COALESCE(excluded.mp_name_norm, civic_dim_molecular_profile.mp_name_norm);""",
        rows_molecular_profile,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
