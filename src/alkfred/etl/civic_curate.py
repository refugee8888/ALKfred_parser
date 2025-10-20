import api_calls
import civic_parser
from alkfred import config
from pathlib import Path

def curate_civic(evidence_items: list[dict],curated_path = None):
    # using civic parser to parse fetched civic evidence
    curated_path = Path(curated_path or config.data_dir() / "curated_resistance_db.json")
    rules = civic_parser.parse_entries(evidence_items, fetch_components=api_calls.fetch_civic_molecular_profile)
    config.save_to_json(rules, path=curated_path)
    return rules