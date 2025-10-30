import json
import sqlite3
from pathlib import Path
import logging
from dotenv.main import logger
from utils import normalize_label
from alkfred import config


DB_PATH = config.default_db_path()
JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")  # use forward slashes or raw string

def main():
    

    logger = logging.getLogger(__name__)


    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()


    logger.info("Table dim_disease created or already exists in %s", DB_PATH)


    # Load JSON as a dict
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect rows
    rows_disease = []
    data_dict = config.raw_json_list_to_dict(JSON_PATH)

    for rec in data_dict.values():                       # iterate values, not keys
        doid = rec.get("id")
        disease = rec.get("disease")
        label_display = disease.get("name")
        label_disease_norm = normalize_label(label_display)
        
        synonyms_json = json.dumps(rec.get("disease_aliases", []))
        rows_disease.append((doid, label_display, label_disease_norm , synonyms_json, None, None, "[]"))
        

    # Bulk insert

    cur.executemany(
        "INSERT OR IGNORE INTO dim_disease (doid, label_display, label_disease_norm, synonyms_json, mondo_id, ncit_id, lineage_json) VALUES (?,?,?,?,?,?,?)",
        rows_disease
    )
    conn.commit()

    conn.close()

if __name__ == "__main__":
    main()