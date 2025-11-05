import os
from pathlib import Path
import requests
import json
from dotenv import load_dotenv

# Load API key
load_dotenv(Path("src/.env"))
bioportal_api_key = os.getenv("BIOPORTAL_API_KEY")

HEADERS = {"Authorization": f"apikey token={bioportal_api_key}"}


def bioportal_search(website: str) -> str:

    user_input = input("Input term:")

    search = f"search?q={user_input}"
    bioportal_query = website + search
    return bioportal_query


SITE = bioportal_search("https://data.bioontology.org/")


def ping_bioportal() -> None:
    print("🔎 Pinging BioPortal API endpoint...")
    if not bioportal_api_key:
        print("❌ Missing BIOPORTAL_API_KEY in your .env")
        return
    try:
        resp = requests.get(SITE, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "collection" in data:
                print("✅ BioPortal API reachable, key accepted (200)")
            else:
                print("⚠️ 200 OK but unexpected response shape (no 'collection')")
        elif resp.status_code == 401:
            print(
                "❌ 401 Unauthorized: key invalid, malformed header, or not activated"
            )
        else:
            print(f"⚠️ Unexpected status: {resp.status_code} — {resp.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network/Request error: {e}")


def save_to_json(data, path="data/raw_bioportal_db.json"):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def fetch_bioportal_data() -> None:
    requested_data = requests.get(SITE, headers=HEADERS)
    nodes = requested_data.json()
    try:
        save_to_json(nodes)
    except:
        raise ValueError("Nothing to save")


if __name__ == "__main__":

    fetch_bioportal_data()
