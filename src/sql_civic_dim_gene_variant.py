import json
import sqlite3
from pathlib import Path

DB_PATH = "dim_gene_variant.db"
JSON_PATH = Path("data/curated_resistance_db.json")  # use forward slashes or raw string

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()



cur.execute(""" CREATE TABLE IF NOT EXISTS dim_gene_variant (
  variant_id TEXT PRIMARY KEY,   -- either CIViC ca_id, or your own generated UID
  hgnc_id TEXT,                  -- HGNC stable ID for the gene (if known)
  gene_symbol TEXT,     -- e.g. "ALK"
  variant_label TEXT,   -- raw variant string, e.g. "ALK T1151dup"
  hgvs_p TEXT,                   -- normalized protein-level HGVS if available
  hgvs_c TEXT,                   -- optional: cDNA HGVS
  aliases_json TEXT,             -- store multiple synonyms
  confidence TEXT                -- HIGH/MED/LOW for mapping certainty
)
""")
# cur.execute(""" CREATE TABLE IF NOT EXISTS evidence_fact (
#   id TEXT PRIMARY KEY,
#   doid TEXT ,
#   ncit_id TEXT NOT NULL,
#   hgnc_id TEXT NOT NULL,
#   variant_key TEXT NOT NULL,
#   direction TEXT CHECK(direction IN ('Resistant','Sensitive','Mixed','Unknown')),
#   evidence_level TEXT,        -- CIViC levels A..E
#   evidence_type TEXT,         -- clinical / preclinical / case / series / trial
#   pub_year INTEGER,
#   pmid TEXT,
#   FOREIGN KEY (doid) REFERENCES dim_disease(doid),
#   FOREIGN KEY (ncit_id) REFERENCES dim_therapy(ncit_id),
#   FOREIGN KEY (hgnc_id, variant_key) REFERENCES dim_gene_variant(hgnc_id, variant_key)

# )
# """)

# Load JSON as a dict
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Collect rows
rows_gene_variant = []
gene_symbol = "ALK"
for rec in data.values():
    for comp in rec.get("components",[]):                      # iterate values, not keys
        ca_id= comp.get("ca_id", [])
        variant_id = ca_id if ca_id else comp.get("variant")
        variant_label = comp.get("variant","")
    
    
        rows_gene_variant.append((variant_id, None, gene_symbol, variant_label, None, None, None, None))
    
    



# Bulk insert

cur.executemany(
    "INSERT OR IGNORE INTO dim_gene_variant (variant_id, hgnc_id, gene_symbol, variant_label, hgvs_p, hgvs_c, aliases_json, confidence) VALUES (?,?,?,?,?,?,?,?)",
    rows_gene_variant
)
conn.commit()

# Verify inserts

cur.execute("SELECT COUNT(*) FROM dim_gene_variant")
print("rows in dim_gene_variant:", cur.fetchone()[0])

# Optional: peek a few

cur.execute("SELECT * FROM dim_gene_variant ORDER BY variant_id LIMIT 200")
for r in cur.fetchall():
    print(r)

conn.close()