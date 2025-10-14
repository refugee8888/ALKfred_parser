import argparse

from alkfred.etl import civic_fetch

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

civic_fetch.fetch_and_curate(symbol = "ALK", raw_path = "/app/data/civic_raw_evidence_db.json", curated_path = "/app/data/curated_resistance_db.json", overwrite= args.overwrite )