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
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (therapy_name_norm)
        DO UPDATE SET
        therapy_name = EXCLUDED.therapy_name,
        ncit_id = CASE
            WHEN EXCLUDED.ncit_id IS NOT NULL AND EXCLUDED.ncit_id != 'N/A'
                THEN EXCLUDED.ncit_id
            ELSE civic_dim_therapy.ncit_id
        END,

        synonyms_json = COALESCE(EXCLUDED.synonyms_json, civic_dim_therapy.synonyms_json),
        rxnorm_id = COALESCE(EXCLUDED.rxnorm_id, civic_dim_therapy.rxnorm_id),
        id_combo = COALESCE(EXCLUDED.id_combo, civic_dim_therapy.id_combo),
        combo_parts_json = COALESCE(EXCLUDED.combo_parts_json, civic_dim_therapy.combo_parts_json),
        class_ids_json = COALESCE(EXCLUDED.class_ids_json, civic_dim_therapy.class_ids_json);""",
        rows_therapy,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
