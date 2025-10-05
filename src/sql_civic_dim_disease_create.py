import json
import sqlite3
from pathlib import Path
import logging

from dotenv.main import logger
from utils import normalize, normalize_label

# logger = logging.getLogger(__name__)
DB_PATH = "alkfred.db"
JSON_PATH = Path("data/curated_resistance_db.json")  # use forward slashes or raw string

logger = logging.getLogger(__name__)


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""PRAGMA foreign_keys = ON""")
try:
    cur.execute(f""" CREATE TABLE IF NOT EXISTS dim_disease (
    doid TEXT PRIMARY KEY,
    label_display TEXT NOT NULL,
    label_norm TEXT NOT NULL,
    synonyms_json TEXT NOT NULL DEFAULT '[]',
    mondo_id TEXT,
    ncit_id TEXT,
    lineage_json TEXT NOT NULL DEFAULT '[]'

    )
    """)
except sqlite3.Error as e:
    logger.debug("Following errors happend while trying to create the database: %r", e)
    raise e.sqlite_errorcode or e.sqlite_errorname

logger.info("Table dim_disease created or already exists in %s", DB_PATH)

cur.execute("CREATE INDEX IF NOT EXISTS idx_label_norm ON dim_disease(label_norm);")


# Load JSON as a dict
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Collect rows
rows_disease = []
for rec in data.values():                       # iterate values, not keys
    doid = rec.get("disease_doid")
    label_display = rec.get("disease_name")
    label_norm = normalize_label(label_display)
    rows_disease.append((doid, label_display, label_norm , "[]", None, None, "[]"))
    
    



# Bulk insert

cur.executemany(
    "INSERT OR IGNORE INTO dim_disease (doid, label_display, label_norm, synonyms_json, mondo_id, ncit_id, lineage_json) VALUES (?,?,?,?,?,?,?)",
    rows_disease
)
conn.commit()

# Verify inserts

cur.execute("SELECT COUNT(*) FROM dim_disease")
count = cur.fetchone()[0]
logger.info("dim_disease loaded with %d rows", count)

# Optional: peek a few

cur.execute("SELECT * FROM dim_disease ORDER BY label_display LIMIT 200")
for r in cur.fetchall():
    print(r)


conn.close()