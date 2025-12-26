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

    rows_variant = []

    for rec in data_dict.values():
        mp = rec.get("molecularProfile") or {}
        molecular_profile_id = mp.get("id")
        eid = rec.get("id")

        for r in mp.get("variants") or []:
            variant_name = r.get("name")
            civic_ca_id = r.get("alleleRegistryId")
            feature = r.get("feature") or {}
            gene_symbol = feature.get("name")

            rows_variant.append(
                (
                    eid,
                    molecular_profile_id,
                    civic_ca_id,
                    gene_symbol,
                    variant_name,
                    ingestion_run_id,
                    ingested_at_utc,
                )
            )

    cur.executemany(
        """
        INSERT INTO civic_raw_gene_variant
            (eid, molecular_profile_id, civic_ca_id, gene_symbol, variant_name, ingestion_run_id, ingested_at_utc)
        VALUES
            (%s,%s,%s,%s,%s,%s,%s)
        """,
        rows_variant,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
