import json
from pathlib import Path
import requests
from dotenv import load_dotenv
import os

src = Path("data/raw_bioportal_db.json")
dst = Path("data/parsed_bioportal_data.json")
load_dotenv(Path("src/.env"))
bioportal_api_key = os.getenv("BIOPORTAL_API_KEY")

HEADERS = {"Authorization": f"apikey token={bioportal_api_key}"}

with src.open("r", encoding="utf-8") as f:
    data = json.load(f)

# This will grab the actual node list
def fetch_ncit_from_bioportal() -> list[dict]:
    result = []
    
    for nodes in data["collection"]:
        
            result.append(nodes["links"]["self"] )
        
    return result

def call_ontology_api()->list[dict]:
    x = fetch_ncit_from_bioportal()
    print(f"Found {len(x)} nodes")
    b =[]
    for m in x:
        SITE=m
        if "NCIT" in m:
            resp = requests.get(SITE, headers=HEADERS, timeout=5)
            if resp.status_code == 200:
                
                b.append(resp.json())
                
                
    with open("data/NCIT_bioportal_dump.json", "w") as f:
        json.dump(b,f,indent=2, ensure_ascii=False)
    
if __name__ == "__main__":
    call_ontology_api()
    



