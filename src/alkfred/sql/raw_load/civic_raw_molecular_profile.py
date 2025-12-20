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
    rows_molecular_profile = []

    for rec in data_dict.values():
        molecular_profile_count = unique_key_generator.generate_key()
        molecular_profile_id = rec.get("molecularProfile").get("id")
        eid = rec.get("id")
        mp_name = rec.get("molecularProfile").get("name")

        rows_molecular_profile.append(
            (molecular_profile_count, molecular_profile_id, eid, mp_name)
        )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_raw_molecular_profile (molecular_profile_count, molecular_profile_id, eid, mp_name) VALUES (%s,%s,%s,%s)""",
        rows_molecular_profile,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
