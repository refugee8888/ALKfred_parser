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

    logger.info("Table civic_dim_therapy created or already exists in %s", DB_PATH)

    rows_therapy = []
    cur.execute("""SELECT ncit_id, therapy_name
                FROM civic_stg_therapy
                """)
    for r in cur.fetchall():
        
        therapy_name_norm = normalize_label(r[1])
        
        rows_therapy.append((therapy_name_norm, r[1], r[0], "[]", None, 0, None, "[]"))

    cur.executemany(
        """INSERT INTO civic_dim_therapy (
        therapy_name_norm,
        therapy_name,
        ncit_id,
        synonyms_json,
        rxnorm_id,
        id_combo,
        combo_parts_json,
        class_ids_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(therapy_name_norm) DO UPDATE SET
        ncit_id = COALESCE(excluded.ncit_id, civic_dim_therapy.ncit_id),
        therapy_name_norm = COALESCE(excluded.therapy_name_norm, civic_dim_therapy.therapy_name_norm);""",
        rows_therapy,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
