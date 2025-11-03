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


def main():
    

    logger = logging.getLogger(__name__)


    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()


    logger.info("Table civic_stg_molecular_profile created or already exists in %s", DB_PATH)

    data_dict = config.raw_json_list_to_dict(JSON_PATH)
    
    # Collect rows
    rows_molecular_profile = []
   
    
    for rec in data_dict.values():
        molecular_profile_id = rec.get("molecularProfile").get("id")
        eid = rec.get("id")
        mp_name = rec.get("molecularProfile").get("name")

        
        rows_molecular_profile.append((molecular_profile_id, eid, mp_name ))
        

    # Bulk insert

    
    cur.executemany(
        """
        INSERT INTO civic_stg_molecular_profile (molecular_profile_id, eid, mp_name) VALUES (?,?,?)""",
        rows_molecular_profile
    )
    conn.commit()

    conn.close()

if __name__ == "__main__":
    main()