import json
import sqlite3
from pathlib import Path
import uuid

DB_PATH = "alkfred.db"
JSON_PATH = Path("data/civic_raw_evidence_db.json")  # use forward slashes or raw string

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
    created_at_utc TEXT,
    run_id TEXT,
    FOREIGN KEY (eid) REFERENCES dim_evidence(eid),
    FOREIGN KEY (variant_id) REFERENCES dim_gene_variant(variant_id),
    FOREIGN KEY (doid) REFERENCES dim_disease(doid),
    FOREIGN KEY (ncit_id) REFERENCES dim_therapy(ncit_id)
);
""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_fact_id ON evidence_fact(fact_id);")



# Load JSON as a dict
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Collect rows

namespace = uuid.UUID("00000000-0000-0000-0000-000000000000")  # fixed namespace
key = f"{eid_for_uuid()}|{doid}|{variant_id}|{ncit_id}"
fact_id = str(uuid.uuid5(namespace, key))


    



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