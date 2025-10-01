import json
import sqlite3
from pathlib import Path

DB_PATH = "dim_disease_create.db"
JSON_PATH = Path("data/curated_resistance_db.json")  # use forward slashes or raw string

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()


cur.execute(""" CREATE TABLE IF NOT EXISTS dim_disease (
  doid TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  mondo_id TEXT,
  ncit_id TEXT,
  synonyms_json TEXT

)
""")
# cur.execute(""" CREATE TABLE IF NOT EXISTS dim_gene_variant (
#   hgnc_id TEXT,
#   variant_key TEXT,
#   gene_symbol TEXT NOT NULL,
#   hgvs_p TEXT,
#   PRIMARY KEY (hgnc_id, variant_key)

# )
# """)
# cur.execute(""" CREATE TABLE IF NOT EXISTS evidence_fact (
#   id TEXT PRIMARY KEY,
#   doid TEXT NOT NULL,
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
rows_disease = []
for rec in data.values():                       # iterate values, not keys
    doid = rec.get("disease_doid",[])
    label = rec.get("disease_name",[])
    rows_disease.append((doid, label, None, None, None))
    
    



# Bulk insert

cur.executemany(
    "INSERT OR IGNORE INTO dim_disease (doid, label, mondo_id, ncit_id, synonyms_json) VALUES (?,?,?,?,?)",
    rows_disease
)
conn.commit()

# Verify inserts

cur.execute("SELECT COUNT(*) FROM dim_disease")
print("rows in dim_disease:", cur.fetchone()[0])

# Optional: peek a few

cur.execute("SELECT * FROM dim_disease ORDER BY label LIMIT 200")
for r in cur.fetchall():
    print(r)

conn.close()