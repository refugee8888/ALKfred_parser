import argparse
from alkfred import config
from alkfred.etl import civic_curate, civic_fetch
import sqlite3
import logging


logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--overwrite", action="store_true", help="Refetch and rebuild JSONs even if they exist")
parser.add_argument("--limit", type = int)
args = parser.parse_args()


# def main():
#     parser = argparse.ArgumentParser(description="Build ALKfred database")
#     parser.add_argument("--from", choices=["curated", "civic"], required=True)
#     parser.add_argument("--db", type=Path, default=config.default_db_path())
#     parser.add_argument("--curated", type=Path, default=config.data_dir() / "curated_resistance_db.json")
#     parser.add_argument("--raw", type=Path, default=config.data_dir() / "civic_raw_evidence_db.json")
#     parser.add_argument("--overwrite", action="store_true")
#     parser.add_argument("--verbose", action="store_true")
#     args = parser.parse_args()

# items = civic_fetch.fetch_civic_evidence(symbol = "ALK", raw_path = "/app/data/civic_raw_evidence_db.json", overwrite= args.overwrite )
# civic_curate.curate_civic(items, curated_path = "/app/data/curated_resistance_db.json")
config.apply_schema()
config.apply_dim_disease()
config.apply_dim_gene_variant()
config.apply_dim_therapy()
config.apply_dim_evidence()
config.apply_evidence_link()
config.apply_fact_evidence()
config.get_conn(config.default_db_path())
cur = config.get_conn(config.default_db_path()).cursor()



# cur.execute("SELECT COUNT(*) FROM dim_disease;")
# count = cur.fetchone()[0]
# logger.info("dim_disease loaded with %d rows", count)
# cur.execute("SELECT COUNT(*) FROM dim_gene_variant")
# count_2 = cur.fetchone()[0]
# logger.info("rows in dim_gene_variant: %d", count_2)
# # Verify inserts
# cur.execute("SELECT COUNT(*) FROM dim_therapy")

# count = cur.fetchone()[0]
# logger.info(f"dim_therapy created with: {count}, rows")
# # Optional: peek a few
# cur.execute("SELECT * FROM dim_therapy ORDER BY label_norm LIMIT 5")

# for r in cur.fetchall():
#     print(r)
# # Verify inserts

cur.execute("SELECT COUNT(*) FROM evidence_link")
print("rows in evidence_link:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM fact_evidence")
print("rows in fact_evidence:", cur.fetchone()[0])


# # Optional: peek a few

# cur.execute("SELECT * FROM dim_evidence ORDER BY eid LIMIT 10")
# for r in cur.fetchall():
#     print(r)
# cur.execute("SELECT COUNT(*) FROM evidence_link")
# total = cur.fetchone()[0]
# logging.info("total links: %d",total)


# # Optional peek
# cur.execute("""
#     SELECT eid, doid, variant_id, ncit_id
#     FROM evidence_link
#     ORDER BY eid, variant_id, ncit_id
#     LIMIT 10
# """)
# for r in cur.fetchall():
#     print(r)


# optional peek
cur.execute("""
    SELECT UPPER(direction) AS dir, UPPER(significance) AS sig, COUNT(*) 
    FROM dim_evidence
    GROUP BY dir, sig
    ORDER BY COUNT(*) DESC;
    """)
for r in cur.fetchall():
    print(r)


