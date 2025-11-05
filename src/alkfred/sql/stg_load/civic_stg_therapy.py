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

    logger.info("Table civic_stg_therapy created or already exists in %s", DB_PATH)

    data_dict = config.raw_json_list_to_dict(JSON_PATH)

    # Collect rows
    rows_therapy = []

    for rec in data_dict.values():

        molecular_profile_id = rec.get("molecularProfile").get("id")
        eid = rec.get("id")

        for r in rec.get("therapies"):

            ncit_id = r.get("ncitId", None)
            therapy_name = r.get("name", None)
            
            therapy_id = unique_key_generator.generate_key()

            rows_therapy.append(
                (therapy_id, eid, molecular_profile_id, ncit_id, therapy_name)
            )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_stg_therapy (therapy_id, eid, molecular_profile_id, ncit_id, therapy_name) VALUES (?,?,?,?,?)""",
        rows_therapy,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
