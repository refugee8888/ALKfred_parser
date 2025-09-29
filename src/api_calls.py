import time
import requests
from utils import help_request, graphql_query
import json
import logging
import re

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

def fetch_civic_molecular_profile(profile_name: str) -> list[dict[str, str | None]]:
    """
    Return unique variant components for an exact CIViC molecular profile name.
    Each component: {"variant": "<label>", "ca_id": <CA ID or None>}.
    Filters out junk fusions like "V::ALK".
    """
    query = """
    query ($name: String!) {
      molecularProfiles(name: $name) {
        nodes {
          name
          variants {
            name
            ... on GeneVariant { alleleRegistryId }
            feature { name }
          }
        }
      }
    }
    """
    data = graphql_query(
        url=GRAPHQL_URL,
        query=query,
        variables={"name": profile_name},
        headers=HEADERS,
    )

    def canon(s: str) -> str:
        return (s or "").strip().lower()

    def looks_like_gene(sym: str) -> bool:
        # crude but effective: 2+ alphanum, not just a single letter placeholder
        return bool(re.fullmatch(r"[A-Z0-9]{2,}", sym))

    def valid_fusion(label: str) -> bool:
        m = re.search(r"(?i)\b([A-Z0-9]+)\s*(?:-|::|/|–)\s*([A-Z0-9]+)(?:\s+fusion)?\b", label or "")
        if not m:
            return True
        a, b = m.group(1), m.group(2)
        return looks_like_gene(a) and looks_like_gene(b)

    nodes = (data.get("molecularProfiles") or {}).get("nodes") or []
    exact_nodes = [n for n in nodes if canon(n.get("name")) == canon(profile_name)]
    if not exact_nodes:
        logging.debug("No exact node match for profile %r (found %d candidates).", profile_name, len(nodes))
        return []

    seen: set[tuple[str, str | None]] = set()
    out: list[dict[str, str | None]] = []

    for node in exact_nodes:
        for v in node.get("variants") or []:
            gene = ((v.get("feature") or {}).get("name") or "").strip()
            mut  = (v.get("name") or "").strip()
            label = " ".join(p for p in [gene, mut] if p).strip()
            ca_id = v.get("alleleRegistryId") or None

            if not label:
                continue
            # Normalize CIViC’s generic “V:ALK Fusion” → human-safe label, or drop it
            if re.search(r"(?i)\bV\s*(?:-|::|/|–)\s*ALK\b", label) or label.upper().startswith("V:ALK"):
                label = "ALK Fusion (unspecified partner)"
            if not valid_fusion(label):
                logging.debug("Dropping junk fusion in %r: %r", profile_name, label)
                continue

            key = (label, ca_id)
            if key in seen:
                continue
            seen.add(key)
            out.append({"variant": label, "ca_id": ca_id})

    logging.debug("Fetched %d variants for profile %s", len(out), profile_name)
    return out
