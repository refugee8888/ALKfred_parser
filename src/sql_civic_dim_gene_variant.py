import json
import sqlite3
from pathlib import Path

from dotenv.main import logger

from utils import normalize_label



DB_PATH = "alkfred.db"
JSON_PATH = Path("data/curated_resistance_db.json")  # use forward slashes or raw string

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""PRAGMA foreign_keys = ON""")

try:
    cur.execute(""" CREATE TABLE IF NOT EXISTS dim_gene_variant (
    variant_id TEXT PRIMARY KEY,   -- either CIViC ca_id, or your own generated UID
    civic_ca_id TEXT,
    hgnc_id TEXT,                  -- HGNC stable ID for the gene (if known)
    gene_symbol TEXT NOT NULL,     -- e.g. "ALK"
    label_display TEXT NOT NULL,   -- raw variant string, e.g. "ALK T1151dup"
    label_norm TEXT NOT NULL,
    hgvs_p TEXT,                   -- normalized protein-level HGVS if available
    hgvs_c TEXT,                   -- optional: cDNA HGVS
    aliases_json TEXT NOT NULL DEFAULT '[]',             -- store multiple synonyms
    confidence TEXT                -- HIGH/MED/LOW for mapping certainty
    )
    """)
except sqlite3.Error as e:
    logger.debug("Following errors happend while trying to create the database: %r", e)
    raise e.sqlite_errorcode or e.sqlite_errorname

cur.execute("CREATE INDEX IF NOT EXISTS idx_gene_symbol ON dim_gene_variant(gene_symbol)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_label_norm ON dim_gene_variant(label_norm)")

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
        label_norm = normalize_label(label_display)
        aliases_json = json.dumps(rec.get("aliases"))
    
    
        rows_gene_variant.append((variant_id, civic_ca_id, None, gene_symbol, label_display, label_norm, None, None, aliases_json, None))
    
    



# Bulk insert

cur.executemany(
    "INSERT OR IGNORE INTO dim_gene_variant (variant_id, civic_ca_id, hgnc_id, gene_symbol, label_display, label_norm, hgvs_p, hgvs_c, aliases_json, confidence) VALUES (?,?,?,?,?,?,?,?,?,?)",
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