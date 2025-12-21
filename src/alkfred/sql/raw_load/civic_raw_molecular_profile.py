from pathlib import Path
from uuid import uuid4
from alkfred import config


JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")


def main():

    conn = config.postgres_conn()
    cur = conn.cursor()

    data_dict = config.raw_json_list_to_dict(JSON_PATH)

    # Collect rows
    rows_molecular_profile = []

    for rec in data_dict.values():

        molecular_profile_id = rec.get("molecularProfile").get("id")
        eid = rec.get("id")
        mp_name = rec.get("molecularProfile").get("name")
        ingestion_run_id = str(uuid4())
        ingested_at_utc = config.utc_now_iso()

        rows_molecular_profile.append(
            (molecular_profile_id,
             eid, mp_name, ingestion_run_id, ingested_at_utc)
        )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_raw_molecular_profile (molecular_profile_id, eid, mp_name, ingestion_run_id, ingested_at_utc) VALUES (%s,%s,%s,%s,%s)""",
        rows_molecular_profile,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
