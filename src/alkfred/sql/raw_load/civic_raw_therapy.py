from pathlib import Path
from uuid import uuid4
from alkfred import config


JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")


def main():

    conn = config.postgres_conn()
    cur = conn.cursor()

    data_dict = config.raw_json_list_to_dict(JSON_PATH)
    ingestion_run_id = str(uuid4())
    ingested_at_utc = config.utc_now_iso()

    # Collect rows
    rows_therapy = []

    for rec in data_dict.values():

        molecular_profile_id = rec.get("molecularProfile").get("id")
        eid = rec.get("id")

        for r in rec.get("therapies"):

            raw_ncit = r.get("ncitId", None)
            if raw_ncit is None or str(raw_ncit).strip().upper() in ("N/A", ""):
                ncit_id = None
            else:
                ncit_id = str(raw_ncit).strip()
            therapy_name = r.get("name", None)

            rows_therapy.append(
                (
                    eid,
                    molecular_profile_id,
                    ncit_id,
                    therapy_name,
                    ingestion_run_id,
                    ingested_at_utc,
                )
            )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_raw_therapy (eid, molecular_profile_id, ncit_id, therapy_name, ingestion_run_id, ingested_at_utc) VALUES (%s,%s,%s,%s,%s,%s)""",
        rows_therapy,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
