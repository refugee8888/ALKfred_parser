import time
import requests
from utils import help_request, graphql_query
import json
import logging
import re
from typing import Optional

GRAPHQL_URL = "https://civicdb.org/api/graphql"
HEADERS = {"Content-Type": "application/json"}
API_THROTTLE = 0.2

log = logging.getLogger(__name__)

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
            status
            significance
            evidenceType
            evidenceLevel
            evidenceRating
            evidenceDirection
            description
            molecularProfile { id name }
            therapies { name ncitId }
            disease {doid name diseaseAliases }
            source { ascoAbstractId citationId pmcId sourceType title publicationYear }
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



def fetch_civic_molecular_profile(
    mp_id: Optional[int] = None,
    mp_name: Optional[str] = None,
) -> list[dict[str, str | None]]:
    """
    Return unique variant components for a CIViC molecular profile.
    Each item: {"variant": "<gene + mutation or gene>", "ca_id": <CA ID or None>}.
    Prefers exact ID lookup; falls back to exact (case-insensitive) name match.
    """

    def _canon(s: str) -> str:
        return (s or "").strip().lower()

    def _looks_like_gene(sym: str) -> bool:
        # simple guard: >=2 uppercase letters/digits
        return bool(re.fullmatch(r"[A-Z0-9]{2,}", sym or ""))

    def _valid_fusion(label: str) -> bool:
        # drop bogus "V::ALK" type fusions where one side isn't a real gene token
        m = re.search(r"(?i)\b([A-Z0-9]+)\s*(?:-|::|/|–)\s*([A-Z0-9]+)(?:\s+fusion)?\b", label or "")
        if not m:
            return True
        a, b = m.group(1), m.group(2)
        return _looks_like_gene(a) and _looks_like_gene(b)

    def _parse_variants(node: dict, profile_label_for_log: str) -> list[dict[str, str | None]]:
        seen: set[tuple[str, str | None]] = set()
        out: list[dict[str, str | None]] = []
        for v in (node.get("variants") or []):
            gene = ((v.get("feature") or {}).get("name") or "").strip()
            mut  = (v.get("name") or "").strip()
            label = " ".join(p for p in [gene, mut] if p).strip()
            ca_id = v.get("alleleRegistryId") or None

            if not label:
                continue

            # Normalize CIViC’s generic "V:ALK Fusion" / "V::ALK" junk
            if re.search(r"(?i)\bV\s*(?:-|::|/|–)\s*ALK\b", label) or label.upper().startswith("V:ALK"):
                label = "ALK Fusion (unspecified partner)"

            if not _valid_fusion(label):
                log.debug("Dropping junk fusion in %r: %r", profile_label_for_log, label)
                continue

            key = (label, ca_id)
            if key in seen:
                continue
            seen.add(key)
            out.append({"variant": label, "ca_id": ca_id})
        log.debug("Parsed %d variants for profile %s", len(out), profile_label_for_log)
        return out

    # --- Branch 1: ID-based (robust) ---
    if mp_id is not None:
        query = """
        query ($id: Int!) {
          molecularProfile(id: $id) {
            id
            name
            variants {
              name
              ... on GeneVariant { alleleRegistryId }
              feature { name }
            }
          }
        }
        """
        data = graphql_query(
            url=GRAPHQL_URL,
            query=query,
            variables={"id": mp_id},
            headers=HEADERS,
        )
        node = (data or {}).get("molecularProfile")
        if not node:
            log.debug("No molecularProfile found for id=%r", mp_id)
            return []
        return _parse_variants(node, profile_label_for_log=f"id={mp_id} ({node.get('name')})")

    # --- Branch 2: Name-based (fallback) ---
    if mp_name:
        query = """
        query ($name: String!) {
          molecularProfiles(name: $name) {
            nodes {
              id
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
            variables={"name": mp_name},
            headers=HEADERS,
        )
        nodes = ((data or {}).get("molecularProfiles") or {}).get("nodes") or []
        # exact match (case-insensitive)
        exact = [n for n in nodes if _canon(n.get("name")) == _canon(mp_name)]
        if not exact:
            log.debug("No exact node match for profile %r (found %d candidates).", mp_name, len(nodes))
            return []
        # If multiple exacts (rare), parse them all and dedupe via _parse_variants per node
        out: list[dict[str, str | None]] = []
        seen_pairs: set[tuple[str, str | None]] = set()
        for node in exact:
            parts = _parse_variants(node, profile_label_for_log=node.get("name") or mp_name)
            for p in parts:
                key = (p["variant"], p["ca_id"])
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                out.append(p)
        return out

    # Nothing to do
    return []
