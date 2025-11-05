import json
from pathlib import Path
import logging
from alkfred import config


DB_PATH = config.default_db_path()
JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")


def main():

    logger = logging.getLogger(__name__)

    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()

    logger.info("Table civic_stg_disease created or already exists in %s", DB_PATH)

    data_dict = config.raw_json_list_to_dict(JSON_PATH)

    # Collect rows
    rows_disease = []
    count = 0

    for rec in data_dict.values():
        doid = rec.get("disease").get("doid")
        eid = rec.get("id")

        if not doid or doid.strip() == "":
            count += 1
            logger.info("No doid found. Entries skipped: %s", count)

        else:

            disease = rec.get("disease")

            label_display = disease.get("name")
            synonyms_json = json.dumps(disease.get("diseaseAliases"))

            rows_disease.append((eid, doid, label_display, synonyms_json))

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_stg_disease (eid, doid, label_display, synonyms_json) VALUES (?,?,?,?)""",
        rows_disease,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
