import json
import sqlite3
from pathlib import Path
import logging
from utils import normalize_label
from alkfred import config
from utils import canon_doid
import uuid


DB_PATH = config.default_db_path()
JSON_PATH = Path("/app/data/civic_raw_evidence_db.json")
UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")



def main():
    

    logger = logging.getLogger(__name__)


    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()


    logger.info("Table civic_stg_therapy created or already exists in %s", DB_PATH)

    data_dict = config.raw_json_list_to_dict(JSON_PATH)
    
    # Collect rows
    rows_therapy = []
    



    for rec in data_dict.values():
        
        molecular_profile_id = rec.get("molecularProfile").get("id")
        eid = rec.get("id")
        
        
        for r in rec.get("therapies"):
             
            ncit_id = r.get("ncitId", None) 
            therapy_name = r.get("name", None)
            unique_seed = str(uuid.uuid4())
            therapy_id = str(uuid.uuid5(UUID_NAMESPACE, unique_seed))


        
            rows_therapy.append((therapy_id, eid, molecular_profile_id, ncit_id, therapy_name))
    

    # Bulk insert
 
    
    cur.executemany(
        """
        INSERT INTO civic_stg_therapy (therapy_id, eid, molecular_profile_id, ncit_id, therapy_name) VALUES (?,?,?,?,?)""",
        rows_therapy
    )
    conn.commit()

    conn.close()

if __name__ == "__main__":
    main()