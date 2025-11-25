from pathlib import Path
import logging
from alkfred import config
import uuid



JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")
unique_key_generator = config.UniqueKeyGenerator(initial_keys_list=set(config.load_from_json("data/unique_keys_list.json")) or None)


def main():

    logger = logging.getLogger(__name__)

    conn = config.postgres_conn()
    cur = conn.cursor()



    data_dict = config.raw_json_list_to_dict(JSON_PATH)

    # Collect rows
    rows_variant = []
    

    for rec in data_dict.values():

        molecular_profile_id = rec.get("molecularProfile").get("id")
        eid = rec.get("id")

        for r in rec.get("molecularProfile").get("variants"):

            variant_name = r.get("name", None)
            civic_ca_id = r.get("alleleRegistryId", None)
            gene_symbol = r.get("feature").get("name") or None
            variant_id = unique_key_generator.generate_key()

            

            rows_variant.append(
                (
                    variant_id,
                    eid,
                    molecular_profile_id,
                    civic_ca_id,
                    gene_symbol,
                    variant_name,
                )
            )

    # Bulk insert

    cur.executemany(
        """
        INSERT INTO civic_stg_gene_variant (variant_id, eid, molecular_profile_id, civic_ca_id, gene_symbol, variant_name) VALUES (%s,%s,%s,%s,%s,%s)""",
        rows_variant,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
