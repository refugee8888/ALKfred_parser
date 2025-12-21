import json
from pathlib import Path
import logging
from alkfred import config
from uuid import uuid4


JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")


def main():

    logger = logging.getLogger(__name__)

    conn = config.postgres_conn()
    cur = conn.cursor()

    data_dict = config.raw_json_list_to_dict(JSON_PATH)
    ingestion_run_id = str(uuid4())
    ingested_at_utc = config.utc_now_iso()

    # Collect rows
    rows_disease = []
    count = 0

    for rec in data_dict.values():

        eid = rec.get("id")

        disease = rec.get("disease")

        try:
            doid = disease.get("doid")
        except Exception as e:
            count += 1
            logger.debug("No doid found %s", e)
            logger.info("No doid found. Entries skipped: %s", count)
            continue

        doid = disease.get("doid")

        disease_name = disease.get("name")
        synonyms_json = json.dumps(disease.get("diseaseAliases"))

        rows_disease.append(
            (eid, doid, disease_name, synonyms_json, ingestion_run_id, ingested_at_utc)
        )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_raw_disease (eid, doid, disease_name, synonyms_json, ingestion_run_id, ingested_at_utc) VALUES (%s,%s,%s,%s,%s,%s)""",
        rows_disease,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
