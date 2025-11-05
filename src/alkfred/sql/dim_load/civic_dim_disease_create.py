from pathlib import Path
import logging
from utils import normalize_label, canon_doid
from alkfred import config


DB_PATH = config.default_db_path()
JSON_PATH = Path(
    "/app/data/civic_raw_evidence_db.json"
) 


def main():

    logger = logging.getLogger(__name__)

    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()

    logger.info("Table dim_disease created or already exists in %s", DB_PATH)

    rows_disease = []
    cur.execute("""SELECT disease_count, eid, doid, disease_name, synonyms_json 
                FROM civic_stg_disease
                """)
    for r in cur.fetchall():
        doid = canon_doid(r[2])
        disease_name_norm = normalize_label(r[3])
    
        rows_disease.append((r[0], r[1], doid, r[3], disease_name_norm, r[4], None, None, '[]'))





    cur.executemany(
        """INSERT INTO dim_disease (disease_count, eid, doid, disease_name, 
        disease_name_norm, synonyms_json, mondo_id, ncit_id, lineage_json) VALUES (?,?,?,?,?,?,?,?,?)""",
        rows_disease,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
