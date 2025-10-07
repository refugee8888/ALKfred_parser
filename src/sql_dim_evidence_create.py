import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = "alkfred.db"
JSON_PATH = Path("data/civic_raw_evidence_db.json")  # use forward slashes or raw string

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""PRAGMA foreign_keys = ON""")

cur.execute("""
CREATE TABLE IF NOT EXISTS dim_evidence (
    
    eid INTEGER PRIMARY KEY,
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
    updated_at_utc TEXT
    )
""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_evidence_eid ON dim_evidence(eid);")

# Load JSON as a dict
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Collect rows
rows_evidence = []

for rec in data:
                        # iterate values, not keys
    eid= rec.get("id", None)

    source_json = json.dumps(rec.get("source", ""))
    direction = rec.get(("evidenceDirection") or None).strip()
    significance = rec.get(("significance") or None).strip()
    evidence_level = rec.get(("evidenceLevel") or None).strip()
    evidence_type = rec.get(("evidenceType") or None).strip()
    rating = rec.get(("evidenceRating") or None)
    status = rec.get(("status") or None).strip()

    src = rec.get("source") or {}
    citation_id = src.get("citationId")
    pmids = []
    if citation_id:
        pmids.append(str(citation_id))
    pmids_json = json.dumps(pmids)

    pub_year = src.get(("publicationYear") or None)
    description = rec.get(("description") or None)
    created_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    updated_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    



    rows_evidence.append((eid, source_json, direction, significance, evidence_level, evidence_type, rating, status, pmids_json, pub_year, description, created_at_utc, updated_at_utc))

    



# Bulk insert

cur.executemany(
    "INSERT OR IGNORE INTO dim_evidence(eid, source_json, direction, significance, evidence_level, evidence_type, rating, status, pmids_json, pub_year, description, created_at_utc, updated_at_utc) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
    rows_evidence
)
conn.commit()

# Verify inserts

cur.execute("SELECT COUNT(*) FROM dim_evidence")
print("rows in dim_evidence:", cur.fetchone()[0])

# Optional: peek a few

cur.execute("SELECT * FROM dim_evidence ORDER BY eid LIMIT 10")
for r in cur.fetchall():
    print(r)

conn.close()