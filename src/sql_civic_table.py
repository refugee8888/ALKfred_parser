import json
import sqlite3
from pathlib import Path

DB_PATH = "dim_therapy.db"
JSON_PATH = Path("data/curated_resistance_db.json")  # use forward slashes or raw string

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS dim_therapy (
  ncitid TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  synonyms_json TEXT,
  rxnorm_id TEXT
)
""")

# Load JSON as a dict
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Collect rows (ncitid, label, synonyms_json, rxnorm_id)
rows = []
for rec in data.values():                       # iterate values, not keys
    for t in rec.get("therapies", []):          # list of {"name":..., "ncit_id":...}
        ncit = t.get("ncit_id")
        label = t.get("name")
        if not ncit or not label:
            continue                            # skip malformed entries
        rows.append((ncit, label, None, None))  # synonyms/rxnorm unknown for now

# Bulk insert
cur.executemany(
    "INSERT OR IGNORE INTO dim_therapy (ncitid, label, synonyms_json, rxnorm_id) VALUES (?,?,?,?)",
    rows
)
conn.commit()

# Verify inserts
cur.execute("SELECT COUNT(*) FROM dim_therapy")
print("rows in dim_therapy:", cur.fetchone()[0])

# Optional: peek a few
cur.execute("SELECT * FROM dim_therapy ORDER BY label LIMIT 5")
for r in cur.fetchall():
    print(r)

conn.close()