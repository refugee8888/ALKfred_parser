import json
import sqlite3
from pathlib import Path

from dotenv.main import logger

from utils import normalize_label
from alkfred import config


DB_PATH = config.default_db_path()
JSON_PATH = Path("data/curated_resistance_db.json") 

def main():
    
    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()

    # Load JSON as a dict
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect rows
    rows_gene_variant = []

    for rec in data.values():
        for comp in rec.get("components",[]):                      # iterate values, not keys
            civic_ca_id= comp.get("ca_id", [])
            variant_id = civic_ca_id if civic_ca_id else comp.get("variant")
            gene_symbol = comp.get("gene_symbol", "")
            label_display = comp.get("variant","")
            label_gene_variant_norm = normalize_label(label_display)
            aliases_json = json.dumps(rec.get("aliases", []))
        
        
            rows_gene_variant.append((variant_id, civic_ca_id, None, gene_symbol, label_display, label_gene_variant_norm, None, None, aliases_json, None))
        

    # Bulk insert

    cur.executemany(
        "INSERT OR IGNORE INTO dim_gene_variant (variant_id, civic_ca_id, hgnc_id, gene_symbol, label_display, label_gene_variant_norm, hgvs_p, hgvs_c, aliases_json, confidence) VALUES (?,?,?,?,?,?,?,?,?,?)",
        rows_gene_variant
    )
    conn.commit()


    conn.close()

if __name__ == "__main__":
    main()