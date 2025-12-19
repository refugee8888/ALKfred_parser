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

            therapy_id = unique_key_generator.generate_key()

            rows_therapy.append(
                (therapy_id, eid, molecular_profile_id, ncit_id, therapy_name)
            )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_stg_therapy (therapy_id, eid, molecular_profile_id, ncit_id, therapy_name) VALUES (%s,%s,%s,%s,%s)""",
        rows_therapy,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
