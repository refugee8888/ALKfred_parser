import json
from pathlib import Path
import requests
from dotenv import load_dotenv
import os

src = Path("data/raw_bioportal_db.json")
dst = Path("data/parsed_bioportal_data.json")
payload = Path("data/NCIT_bioportal_dump.json")
load_dotenv(Path("src/.env"))
bioportal_api_key = os.getenv("BIOPORTAL_API_KEY")

HEADERS = {"Authorization": f"apikey token={bioportal_api_key}"}

with src.open("r", encoding="utf-8") as f:
    data = json.load(f)

# This will grab the actual node list
def fetch_ncit_from_bioportal() -> list[dict]:
    results = {}
    
    for node in data["collection"]:
        class_url = node["links"]["self"]
        ontology = node["links"]["ontology"]
        if "NCIT" in ontology or "MONDO" in ontology or "HGNC" in ontology:
            resp = requests.get(class_url, headers=HEADERS, timeout=5)
            if resp.status_code == 200:
                payload = resp.json()
                class_id = payload.get("@id")
                
                if class_id:
                    results[class_id] = {
                        
                        "label": payload.get("prefLabel"),
                        "synonyms": payload.get("synonym", []),
                        "defs": payload.get("definition", [])
                    }
                    print(f"Added entry for {class_id}")  
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


    
if __name__ == "__main__":
    fetch_ncit_from_bioportal()
    
    



