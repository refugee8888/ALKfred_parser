import api_calls
import civic_parser
from alkfred import config
from pathlib import Path
from typing import Optional
import json



def fetch_civic_evidence(oncogene = None, raw_path=None, overwrite=False, limit: Optional[int] = None):
    
    
    if raw_path is None:
        raw_path = config.data_dir() / "civic_raw_evidence_db.json"
    raw_path = Path(raw_path)

    if raw_path.exists() and not overwrite:
        with raw_path.open("r", encoding="utf-8") as f:
            return json.load(f)
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
            
            if civic_parser.gene_in_molecular_profile(mp_name, oncogene):
                filtered.append(ei)
                if limit is not None and len(filtered) >= limit:
                    break
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    
    config.save_to_json(filtered, path=raw_path)
    
    return filtered
   
