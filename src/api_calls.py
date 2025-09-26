import time
import requests
from utils import help_request, graphql_query
import json
import logging

GRAPHQL_URL = "https://civicdb.org/api/graphql"
HEADERS = {"Content-Type": "application/json"}
API_THROTTLE = 0.2

def fetch_civic_all_evidence_items():
    after_cursor = None
    all_items = []
    seen_ids = set()
    page = 1
    MAX_PAGES = 10000

    query = """
      query ($first: Int!, $after: String) {
        evidenceItems(status: ACCEPTED, first: $first, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            significance
            evidenceDirection
            description
            molecularProfile { name }
            therapies { name ncitId }
            disease {doid name diseaseAliases }
          }
        }
      }
    """

    while True:
        data = graphql_query(
            url= GRAPHQL_URL,
            query=query,
            variables={"first": 500, "after": after_cursor},
            headers= HEADERS,
        )

        evidence_items = data["evidenceItems"]
        for node in evidence_items["nodes"]:
            if node["id"] not in seen_ids:
                seen_ids.add(node["id"])
                all_items.append(node)

        if not evidence_items["pageInfo"]["hasNextPage"]:
            break

        after_cursor = evidence_items["pageInfo"]["endCursor"]
        page += 1
        logging.info("Fetched page %s with %s items", page, len(all_items))
        time.sleep(API_THROTTLE)

        if page > MAX_PAGES:
            raise RuntimeError("Exceeded max pages — likely stuck in a loop")

    return all_items

def fetch_civic_molecular_profile(profile_name: str) -> list[dict]:
    query = """
     query ($name: String!){
      molecularProfiles(name: $name) {
        nodes {
          variants {
            name
            ... on GeneVariant {
              alleleRegistryId
            }
            feature {
              name
            }
          }
        }
      }
    }
    """
    data = graphql_query(
            url= GRAPHQL_URL,
            query=query,
            variables={"name": profile_name},
            headers= HEADERS,
        )
    nodes = data["molecularProfiles"]["nodes"]  
    results = []
    seen = set()
    for node in nodes:
        for v in node.get("variants", []):
            variant_label = " ".join(
                filter(None, [v.get("feature", {}).get("name"), v.get("name")])
            )
            key = (variant_label, v.get("alleleRegistryId"))
            if key not in seen:
                seen.add(key)
                results.append({
                    "variant": variant_label.strip(),
                    "ca_id": v.get("alleleRegistryId") or None
                })
    logging.debug("Fetched %s variants for profile %s", len(results), profile_name)
    return results


# if __name__ == "__main__":

#   print(fetch_civic_molecular_profile("ALK"))