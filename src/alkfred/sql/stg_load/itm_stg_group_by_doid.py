import json
import sqlite3
from pathlib import Path
import logging
from utils import normalize_label
from alkfred import config
from utils import canon_doid
import uuid


DB_PATH = config.default_db_path()
JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")  # use forward slashes or raw string


def main():
    

    logger = logging.getLogger(__name__)


    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()


    logger.info("Table stg_disease created or already exists in %s", DB_PATH)

    data_dict = config.raw_json_list_to_dict(JSON_PATH)
    
    # Collect rows
    rows_disease = []
    cur.execute("""SELECT doid, label_display, synonyms_json FROM stg_disease sd
                GROUP * BY sd.doid;
                """)
    
    
    
    

    

    for rec in data_dict.values():                       
        doid = rec.get("disease").get("doid")
        
        
        if not doid or doid.strip() == "":
            count += 1
            logger.info("No doid found. Entries skipped: %s", count)
            
        else:
            
            disease = rec.get("disease")
            
            label_display = disease.get("name")
            synonyms_json = json.dumps(disease.get("diseaseAliases"))

        
        
            rows_disease.append((doid, label_display, synonyms_json))
        

    # Bulk insert

    cur.executemany(
        "INSERT INTO stg_disease (doid, label_display, synonyms_json) VALUES (?,?,?)",
        rows_disease
    )
    conn.commit()

    conn.close()

if __name__ == "__main__":
    main()