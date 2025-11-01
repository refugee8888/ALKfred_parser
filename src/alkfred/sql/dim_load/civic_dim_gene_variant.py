import json
import sqlite3
from pathlib import Path

from dotenv.main import logger
import uuid
from utils import normalize_label
from alkfred import config


DB_PATH = config.default_db_path()
JSON_PATH = Path("data/civic_raw_evidence_db.json") 
UUID_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")

def main():
    
    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()

    # Load JSON as a dict
    data_dict = config.raw_json_list_to_dict(JSON_PATH)
    
    
    # Collect rows
    rows_gene_variant = []

    for rec in data_dict.values():
        entry = rec.get("molecularProfile",[])
        for v in entry.get("variants", []):                   
            civic_ca_id= v.get("alleleRegistryId", "")
            gene_symbol = v.get("feature", {}).get("name", "")
            label_display = v.get("name","")
            label_gene_variant_norm = normalize_label(label_display)
            variant_id = civic_ca_id if civic_ca_id else str(uuid.uuid5(UUID_NAMESPACE, f"variant|{label_gene_variant_norm}"))
        
        
            rows_gene_variant.append((variant_id, civic_ca_id, None, gene_symbol, label_display, label_gene_variant_norm, None, None, None))
        

    # Bulk insert

    cur.executemany(
        "INSERT OR IGNORE INTO dim_gene_variant (variant_id, civic_ca_id, hgnc_id, gene_symbol, label_display, label_gene_variant_norm, hgvs_p, hgvs_c, confidence) VALUES (?,?,?,?,?,?,?,?,?)",
        rows_gene_variant
    )
    conn.commit()


    conn.close()

if __name__ == "__main__":
    main()