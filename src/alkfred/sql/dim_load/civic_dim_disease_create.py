from pathlib import Path
import logging
from utils import normalize_label, canon_doid
from alkfred import config
import json


JSON_PATH = Path(
    "/app/data/civic_raw_evidence_db.json"
) 


def main():

    logger = logging.getLogger(__name__)

    conn = config.postgres_conn()
    cur = conn.cursor()

  

    rows_disease = []
    cur.execute("""SELECT doid, disease_name, synonyms_json 
                FROM civic_stg_disease
                """)
    for r in cur.fetchall():
        doid = canon_doid(r[0])
        disease_name_norm = normalize_label(r[1])
        
        rows_disease.append((doid, r[1], disease_name_norm, r[2], None, None, '[]'))





    cur.executemany(
        """INSERT INTO civic_dim_disease (
        doid, disease_name, disease_name_norm, synonyms_json, mondo_id, ncit_id, lineage_json
        ) VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT(doid) DO UPDATE SET
        disease_name      = COALESCE(excluded.disease_name, civic_dim_disease .disease_name),
        disease_name_norm = COALESCE(excluded.disease_name_norm, civic_dim_disease .disease_name_norm),
        synonyms_json     = CASE
                                WHEN excluded.synonyms_json IS NOT NULL
                                AND excluded.synonyms_json != '[]'
                                THEN excluded.synonyms_json
                                ELSE civic_dim_disease .synonyms_json
                            END,
        mondo_id          = COALESCE(excluded.mondo_id, civic_dim_disease .mondo_id),
        ncit_id           = COALESCE(excluded.ncit_id, civic_dim_disease .ncit_id),
        lineage_json      = COALESCE(excluded.lineage_json, civic_dim_disease .lineage_json);""",
        rows_disease,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
