import api_calls
import civic_parser
from alkfred import config
from pathlib import Path



def fetch_civic_evidence(symbol="ALK", raw_path=None, overwrite=False):
    # Fetch CIViC evidence
    all_items = api_calls.fetch_civic_all_evidence_items()
    filtered = []
    for ei in all_items:
            if not ei or not isinstance(ei, dict):
                continue
            mp = ei.get("molecularProfile")
            # disease = ei.get("disease")
            
            if not mp:
                continue
            mp_name = mp.get("name", "")
            # disease_name = disease.get("name", "")
            
            if civic_parser.gene_in_molecular_profile(mp_name, symbol):
                filtered.append(ei)
    if not overwrite and Path(raw_path).exists():
        print(f"Raw data exists at {raw_path}. Use --overwrite to refetch.")
        return
    
    config.save_to_json(filtered, path=raw_path)
    
    return filtered
   
