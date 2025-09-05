import time
import requests

GRAPHQL_URL = "https://civicdb.org/api/graphql"
HEADERS = {"Content-Type": "application/json"}


def ping_civic_api():
    print("\U0001F50E Pinging CIViC API endpoint...")
    try:
        response = requests.options(GRAPHQL_URL, timeout=5)
        response = requests.post(
            GRAPHQL_URL,
            json={"query": '''query { gene(entrezSymbol: "ALK") { name } }'''},
            headers=HEADERS
        )
        if response.status_code in (200, 204):
            print(f"✅ CIViC API is reachable ({response.status_code})")
        else:
            print(f"⚠️ CIViC API responded with unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ CIViC API not reachable: {e}")

def fetch_civic_all_evidence_items():
    after_cursor = None
    all_items = []
    page = 1

    while True:
        print(f"🔎 Fetching page {page} of CIViC evidenceItems...")
        query = f"""
        {{
          evidenceItems(status: ACCEPTED, first: 500{f', after: "{after_cursor}"' if after_cursor else ''}) {{
            pageInfo {{
              hasNextPage
              endCursor
            }}
            nodes {{
              id
              significance
              evidenceDirection
              description
              molecularProfile {{
                name
              }}
              therapies {{
                name
              }}
              disease {{
                name
                diseaseAliases
              }}
            }}
          }}
        }}
        """
        response = requests.post(GRAPHQL_URL, json={"query": query}, headers=HEADERS)
        response.raise_for_status()
        data = response.json()["data"]["evidenceItems"]
        all_items.extend(data["nodes"])

        if not data["pageInfo"]["hasNextPage"]:
            break
        after_cursor = data["pageInfo"]["endCursor"]
        page += 1
        time.sleep(0.2)

    return all_items

def fetch_civic_molecular_profile(profile_name: str) -> list[dict]:
    query = f"""
    {{
      molecularProfiles(name: "{profile_name}") {{
        nodes {{
          variants {{
            name
            ... on GeneVariant {{
              alleleRegistryId
            }}
            feature {{
              name
            }}
          }}
        }}
      }}
    }}
    """
    response = requests.post(GRAPHQL_URL, json={"query": query}, headers=HEADERS)
    response.raise_for_status()
    nodes = response.json()["data"]["molecularProfiles"]["nodes"]
    if not nodes:
        return []

    return [
        {
            "variant": f"{v['feature']['name']} {v['name']}".strip(),
            "ca_id": v.get("alleleRegistryId") or None
        }
        for v in nodes[0]["variants"]
    ]