import json
from pathlib import Path
import logging
from alkfred import config
import uuid


DB_PATH = config.default_db_path()
JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")
unique_key_generator = config.UniqueKeyGenerator(initial_keys_list=set(config.load_from_json("data/unique_keys_list.json")) or None)


def main():

    logger = logging.getLogger(__name__)

    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()

    logger.info("Table civic_stg_evidence created or already exists in %s", DB_PATH)

    data_dict = config.raw_json_list_to_dict(JSON_PATH)

    # Collect rows
    rows_evidence = []

    for rec in data_dict.values():
        evidence_count = unique_key_generator.generate_key()
        eid = rec.get("id", None)
        status = rec.get("status")
        significance = rec.get("significance")
        evidence_type = rec.get("evidenceType")
        evidence_level = rec.get("evidenceLevel")
        rating = rec.get("evidenceRating")
        direction = rec.get("evidenceDirection")
        description = rec.get("description")
        pmids_json = json.dumps(rec.get("source").get("pmcId"))
        pub_year = rec.get("source").get("publicationYear")
        created_at_utc = config.utc_now_iso()
        updated_at_utc = config.utc_now_iso()

        rows_evidence.append(
            (   evidence_count,
                eid,
                status,
                significance,
                evidence_type,
                evidence_level,
                rating,
                direction,
                description,
                pmids_json,
                pub_year,
                created_at_utc,
                updated_at_utc,
            )
        )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_stg_evidence(evidence_count, eid, status, significance, evidence_type, evidence_level, rating, direction, description, pmids_json, pub_year, created_at_utc, updated_at_utc) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows_evidence,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
