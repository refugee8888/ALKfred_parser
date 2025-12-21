import json
from pathlib import Path
from uuid import uuid4
from alkfred import config


JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")


def main():

    conn = config.postgres_conn()
    cur = conn.cursor()

    data_dict = config.raw_json_list_to_dict(JSON_PATH)

    # Collect rows
    rows_evidence = []

    for rec in data_dict.values():

        ingestion_run_id = str(uuid4())
        eid = rec.get("id", None)
        status = rec.get("status")
        significance = (
            rec.get("significance")
            .strip()
            .upper()
            .replace("SENSITIVITYRESPONSE", "SENSITIVITY")
        )
        evidence_type = rec.get("evidenceType")
        evidence_level = rec.get("evidenceLevel")
        rating = rec.get("evidenceRating")
        direction = rec.get("evidenceDirection")
        description = rec.get("description")
        pmids_json = json.dumps(rec.get("source").get("pmcId"))
        pub_year = rec.get("source").get("publicationYear")
        ingested_at_utc = config.utc_now_iso()

        rows_evidence.append(
            (
                eid,
                direction,
                significance,
                evidence_level,
                evidence_type,
                rating,
                status,
                pmids_json,
                pub_year,
                description,
                ingestion_run_id,
                ingested_at_utc,
            )
        )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_raw_evidence(
                eid,
                direction,
                significance,
                evidence_level,
                evidence_type,
                rating,
                status,
                pmids_json,
                pub_year,
                description,
                ingestion_run_id,
                ingested_at_utc) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows_evidence,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
