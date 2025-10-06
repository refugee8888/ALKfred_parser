import json
import sqlite3
from pathlib import Path

DB_PATH = "alkfred.db"
JSON_PATH = Path("data/curated_resistance_db.json")  # use forward slashes or raw string

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""PRAGMA foreign_keys = ON""")

cur.execute("""
CREATE TABLE IF NOT EXISTS evidence_fact (
    fact_id TEXT PRIMARY KEY,
    eid INTEGER NOT NULL,
    mp_id TEXT,
    variant_id TEXT NOT NULL,
    doid TEXT NOT NULL,
    ncit_id TEXT,
    source_json TEXT,
    direction TEXT,
    significance TEXT,
    evidence_level TEXT,
    evidence_type TEXT,
    rating INTEGER,
    status TEXT,
    pmids_json TEXT,
    pub_year INTEGER,
    description TEXT,
    created_at_utc TEXT,
    updated_at_utc TEXT,
    run_id TEXT,
    FOREIGN KEY (variant_id) REFERENCES dim_gene_variant(variant_id),
    FOREIGN KEY (doid) REFERENCES dim_disease(doid),
    FOREIGN KEY (ncit_id) REFERENCES dim_therapy(ncit_id)
);
""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_eid ON evidence_fact(eid);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_doid_direction ON evidence_fact(doid, direction);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_variant ON evidence_fact(variant_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_therapy ON evidence_fact(ncit_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_mp ON evidence_fact(mp_id);")


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
    "INSERT OR IGNORE INTO fact_evidence(fact_id,eid,mp_id,variant_id,doid,ncit_id,source,direction,significance,evidence_level,evidence_type,rating,status,pmids_json,pub_year,description,created_at_utc,updated_at_utc,run_id)) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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