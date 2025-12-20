import json
from pathlib import Path
from alkfred import config


JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")
unique_key_generator = config.UniqueKeyGenerator(
    initial_keys_list=set(config.load_from_json("data/unique_keys_list.json")) or None
)


def main():

    conn = config.postgres_conn()
    cur = conn.cursor()

    data_dict = config.raw_json_list_to_dict(JSON_PATH)

    # Collect rows
    rows_evidence = []

    for rec in data_dict.values():
        evidence_count = unique_key_generator.generate_key()
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
        created_at_utc = config.utc_now_iso()
        updated_at_utc = config.utc_now_iso()

        rows_evidence.append(
            (
                evidence_count,
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
                created_at_utc,
                updated_at_utc,
            )
        )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_raw_evidence(evidence_count,
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
                created_at_utc,
                updated_at_utc) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows_evidence,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
