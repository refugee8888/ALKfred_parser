import json
import logging

from pathlib import Path
import uuid
from utils import normalize_label
from alkfred import config

DB_PATH = config.default_db_path()
JSON_PATH = Path("data/curated_resistance_db.json")  
UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")



        

def main():

    DB_PATH = config.default_db_path()
    JSON_PATH = Path("data/curated_resistance_db.json")  

    logger = logging.getLogger(__name__)

    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()


    logger.info("Table dim_therapy created or already exists in %s", DB_PATH)


    # Load JSON as a dict
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect rows (ncitid, label, synonyms_json, rxnorm_id)
    rows_therapy = []
    

    for rec in data.values():                       # iterate values, not keys
        for t in rec.get("therapies"):          # list of {"name":..., "ncit_id":...}
            ncit_id = t.get("ncit_id")
            label_display = t.get("name","")
            label_therapy_norm = normalize_label(label_display)
            if ncit_id:
                seed = f"therapy|{ncit_id}"
            else:
                seed = f"therapy|{label_therapy_norm}" 
            therapy_id = str(uuid.uuid5(UUID_NAMESPACE, seed))
            if label_therapy_norm == "":
                continue
            
            if not label_display or not label_therapy_norm:
                continue                            # skip malformed entries
            rows_therapy.append((therapy_id, ncit_id, label_display, label_therapy_norm, "[]", None, 0, None, None))  # synonyms/rxnorm unknown for now
    
    
    # Bulk insert
    cur.executemany(
        "INSERT OR IGNORE INTO dim_therapy(therapy_id, ncit_id, label_display, label_therapy_norm, synonyms_json, rxnorm_id, id_combo, combo_parts_json, class_ids_json) VALUES (?,?,?,?,?,?,?,?,?)",
        rows_therapy
    )

    conn.commit()

    conn.close()
if __name__ == "__main__":
    main()