from pathlib import Path
import logging
from utils import normalize_label, canon_doid
from alkfred import config
import json

DB_PATH = config.default_db_path()
JSON_PATH = Path(
    "/app/data/civic_raw_evidence_db.json"
) 


def main():

    logger = logging.getLogger(__name__)

    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()

    logger.info("Table civic_dim_gene_variant created or already exists in %s", DB_PATH)

    rows_gene_variant = []
    cur.execute("""SELECT variant_id, civic_ca_id, gene_symbol, variant_name
                FROM civic_stg_gene_variant
                """)
    for r in cur.fetchall():
        
        variant_name_norm = normalize_label(r[3])
        gene_symbol = normalize_label(r[2])
        rows_gene_variant.append((r[0], r[1], None, gene_symbol, r[3], variant_name_norm, None, None))





    cur.executemany(
        """INSERT INTO civic_dim_gene_variant (
       variant_id, civic_ca_id, hgnc_id, gene_symbol, variant_name, variant_name_norm, hgvs_p, hgvs_c
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?) 
        ON CONFLICT(variant_id) DO UPDATE SET
        civic_ca_id = COALESCE(excluded.civic_ca_id, civic_dim_gene_variant.civic_ca_id),
        gene_symbol = COALESCE(excluded.gene_symbol, civic_dim_gene_variant.gene_symbol),
        variant_name = COALESCE(excluded.variant_name, civic_dim_gene_variant.variant_name),
        variant_name_norm = COALESCE(excluded.variant_name_norm, civic_dim_gene_variant.variant_name_norm);""",
        rows_gene_variant,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
