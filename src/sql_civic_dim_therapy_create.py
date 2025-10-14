import json
import logging
import sqlite3
from pathlib import Path

from utils import normalize_label
from alkfred import config

DB_PATH = config.default_db_path()
JSON_PATH = Path("data/curated_resistance_db.json")  # use forward slashes or raw string

logger = logging.getLogger(__name__)

conn = config.get_conn(DB_PATH)
cur = conn.cursor()
cur.execute("""PRAGMA foreign_keys = ON""")
try:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_therapy (
    ncit_id TEXT PRIMARY KEY,
    label_display TEXT NOT NULL,
    label_norm TEXT NOT NULL ,
    synonyms_json TEXT NOT NULL DEFAULT '[]',
    rxnorm_id TEXT,
    id_combo INTEGER NOT NULL DEFAULT 0,
    combo_parts_json TEXT,
    class_ids_json TEXT

    )
    """)
except sqlite3.Error as e:
    logger.debug("Following errors happend while trying to create the database: %r", e)
    raise e
    

logger.info("Table dim_therapy created or already exists in %s", DB_PATH)

cur.execute("CREATE INDEX IF NOT EXISTS idx_label_norm ON dim_therapy(label_norm)")


# Load JSON as a dict
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Collect rows (ncitid, label, synonyms_json, rxnorm_id)
rows_theraphy = []

for rec in data.values():                       # iterate values, not keys
    for t in rec.get("therapies"):          # list of {"name":..., "ncit_id":...}
        ncit_id = t.get("ncit_id")
        label_display = t.get("name","")
        label_norm = normalize_label(label_display)
        if not ncit_id or not label_display:
            continue                            # skip malformed entries
        rows_theraphy.append((ncit_id, label_display, label_norm, "[]", None, 0, None, None))  # synonyms/rxnorm unknown for now
  
    



# Bulk insert
cur.executemany(
    "INSERT OR IGNORE INTO dim_therapy(ncit_id, label_display, label_norm, synonyms_json, rxnorm_id, id_combo, combo_parts_json, class_ids_json) VALUES (?,?,?,?,?,?,?,?)",
    rows_theraphy
)

conn.commit()

# Verify inserts
cur.execute("SELECT COUNT(*) FROM dim_therapy")

count = cur.fetchone()[0]
logger.info(f"Table created with: {count}, rows")
# Optional: peek a few
cur.execute("SELECT * FROM dim_therapy ORDER BY label_norm LIMIT 5")

for r in cur.fetchall():
    print(r)

conn.close()