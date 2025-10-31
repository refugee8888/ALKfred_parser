# civic_parser.py
# from __future__ import annotations

# import logging
# import re
# from typing import Callable, Optional

# from utils import normalize

# __all__ = [
#     "generate_aliases",
#     "gene_in_molecular_profile",
#     "parse_resistance_entries",
# ]

# logger = logging.getLogger(__name__)


# def generate_aliases(profile_name: str, components: list[dict[str, Optional[str]]]) -> list[str]:
#     """
#     Produce deterministic, compact aliases for a molecular profile (fusion ± secondary mutations).

#     Inputs
#     ------
#     profile_name : str
#         Raw CIViC molecularProfile.name.
#     components : list of {"variant": str, "ca_id": Optional[str]}
#         Variant components fetched upstream (e.g., from CIViC variants for this profile).

#     Rules
#     -----
#     - Always include:
#         - the stripped profile_name
#         - normalize(profile_name) as canonical text form
#     - For each component:
#         - include normalize(variant) if present
#         - if component looks like GENE + mutation → add "GENE <mut>" and "<mut> GENE"
#         - if fusion detected (A-B / A::B / A/B / A–B [en dash]) → add:
#           "A-B fusion", "A-B", "B-A fusion", "B-A", "A::B", "B::A"
#     - Clean: collapse whitespace, drop very short tokens (<= 3 chars), remove trivial words {"in","with","variant"}
#     - Deduplicate via set, return sorted list (deterministic)

#     Non-goals
#     ---------
#     - Do not generate HGVS strings.
#     - Do not explode combinatorially.
#     """
#     aliases: set[str] = set()

#     base = (profile_name or "").strip()
#     if base:
#         aliases.add(base)
#     nbase = normalize(profile_name or "")
#     if nbase:
#         aliases.add(nbase)

#     variant_aliases: list[set[str]] = []

#     for comp in components or []:
#         raw = (comp or {}).get("variant") or ""
#         vset: set[str] = set()

#         nraw = normalize(raw)
#         if nraw:
#             vset.add(nraw)

#         # Gene + mutation (non-fusion shapes)
#         tokens = re.split(r"[:\-_–/\s]+", raw)  # includes en dash U+2013
#         gene = tokens[0].upper() if tokens and tokens[0] else ""
#         mutation = " ".join(t for t in tokens[1:] if t) if len(tokens) > 1 else ""
#         if gene and mutation:
#             vset.update({f"{gene} {mutation}", f"{mutation} {gene}"})

#         # Fusion parsing: A-B, A::B, A/B, A–B [+ optional ' fusion']
#         m = re.search(r"(?i)\b([A-Z0-9]+)\s*(?:-|::|/|–)\s*([A-Z0-9]+)(?:\s+fusion)?\b", raw)
#         if m:
#             a, b = m.group(1).upper(), m.group(2).upper()
#             vset.update({
#                 f"{a}-{b} fusion", f"{a}-{b}",
#                 f"{b}-{a} fusion", f"{b}-{a}",
#                 f"{a}::{b}", f"{b}::{a}",
#             })

#         # Clean & collect
#         cleaned = {re.sub(r"\s+", " ", v).strip() for v in vset if v}
#         variant_aliases.append(cleaned)

#     # Flatten & filter
#     noise = {"in", "with", "variant"}
#     flat: set[str] = set()
#     for vset in variant_aliases:
#         for v in vset:
#             if len(v) > 3 and v.lower() not in noise:
#                 flat.add(v)

#     aliases.update(flat)
#     return sorted(a for a in aliases if a and len(a) > 3)




# def _composite_key(doid: str, profile_norm: str) -> str:
#     """Create a stable string key for dicts that must be JSON-serializable."""
#     return f"DOID:{doid}||{profile_norm}"

    
# def parse_entries(
#     evidence_items: list[dict],
#     fetch_components: Optional[Callable[[str], list[dict[str, Optional[str]]]]] = None,
# ) -> dict[str, dict]:
    
#     logger.info("🧠 Building resistance rule DB from CIViC evidenceItems...")
#     rules: dict[str, dict] = {}
#     profile_enrichment_cache: dict[str, list[dict[str, Optional[str]]]] = {}

#     for item in evidence_items:
#         if not isinstance(item, dict):
#             logger.debug("Skipping non-dict evidence item: %r", item)
#             continue

#         # --------------------
#         # Required blocks
#         # --------------------
#         mp = item.get("molecularProfile") or {}
        
#         disease = item.get("disease") or {}
#         therapies_raw = item.get("therapies") or []

#         mp_name_raw = str(mp.get("name") or "").strip()
#         mp_id = mp.get("id", "")
#         disease_name = str(disease.get("name") or "").strip()
#         disease_doid = disease.get("doid")


#         eid = str(item.get("id")or "").strip()
#         status = str(item.get("status")  or "").strip().upper()
#         source = item.get("source") or []

#         if not mp_name_raw:
#             logger.debug("Skipping item with empty molecularProfile.name")
#             continue
#         if not disease_doid:
#             logger.debug("Skipping item without disease.doid (name=%r)", disease_name)
#             continue

       
#         significance = (item.get("significance") or "").strip().upper()
#         direction = (item.get("evidenceDirection") or "").strip().upper()
#         evidence_level = (item.get("evidenceLevel") or "").strip().upper()
#         evidence_type = (item.get("evidenceType") or "").strip().upper()
#         evidence_rating = item.get("evidenceRating")
       
#         if not therapies_raw:
#             logger.debug("Skipping item with no therapies for profile %r", mp_name_raw)
#             continue

#         # --------------------
#         # Normalize & key
#         # --------------------
#         profile_norm = normalize(mp_name_raw)
#         key = _composite_key(disease_doid, profile_norm)

#         # --------------------
#         # Enrichment (optional, injected)
#         # --------------------
#         if fetch_components:
#             if mp_name_raw not in profile_enrichment_cache:
#                 try:
#                     components = fetch_components(mp_name_raw) or []
#                 except Exception as e:
#                     logger.debug("Component fetch failed for %r: %s", mp_name_raw, e)
#                     components = []
#                 profile_enrichment_cache[mp_name_raw] = components
#             else:
#                 components = profile_enrichment_cache[mp_name_raw]
#         else:
#             components = []

#         # canonical_id: first non-null CA ID
#         canonical_id = next((c.get("ca_id") for c in components if c.get("ca_id")), None)

#         # --------------------
#         # Build/merge rule
#         # --------------------
#         # Dedup therapies by (normalized name, ncit_id)
#         pairs: dict[tuple[str, str | None], str] = {}
#         for t in therapies_raw:
#             raw_name = (t.get("name") or "").strip()
#             if not raw_name:
#                 continue
#             nid = t.get("ncitId") or t.get("ncit_id")
#             tkey = (normalize(raw_name), nid)  # dedupe key
#             pairs.setdefault(tkey, raw_name)   # keep first-seen display casing

#         therapies_list = sorted(
#             ({"name": disp, "ncit_id": nid} for ((_, nid), disp) in pairs.items()),
#             key=lambda x: (x["name"].lower(), x["ncit_id"] or ""),
#         )
#         rule_key = _composite_key(disease_doid, profile_norm)
       
#         # Prepare current entry
#         if rule_key not in rules:
#             rules[rule_key] = {
#                 "canonical_id": canonical_id,
#                 "components": list(components),  # shallow copy ok
#                 "eid": eid,
#                 "mp_id": mp_id,
#                 "status": status,
#                 "source": source,
#                 "significance": significance,
#                 "direction": direction,
#                 "evidence_level": evidence_level,
#                 "evidence_type": evidence_type,
#                 "evidence_rating": evidence_rating,
#                 "aliases": set(generate_aliases(profile_norm, components)),
#                 "therapies": set((normalize(t["name"]), t["ncit_id"]) for t in therapies_list),
#                 "evidence_count": 1,
#                 "gene_symbol": mp_name_raw,
#                 "descriptions": [ (item.get("description") or "").strip() ] if item.get("description") else [],
#                 "disease_name": disease_name,
#                 "disease_doid": disease_doid,
#                 "disease_aliases": set(disease.get("diseaseAliases") or []),
#                 "eids": {eid}
#             }
#             logger.debug("NEW rule: %s (%s)", key, mp_name_raw)
#         else:
#             r = rules[rule_key]
            
#             r["evidence_count"] += 1

#             # canonical_id: keep existing or take new if previously None
#             if not r.get("canonical_id") and canonical_id:
#                 r["canonical_id"] = canonical_id

#             # merge components (by (variant, ca_id))
#             existing = {(c.get("variant"), c.get("ca_id")) for c in r.get("components", [])}
#             for c in components:
#                 tup = (c.get("variant"), c.get("ca_id"))
#                 if tup not in existing:
#                     r["components"].append(c)
#             # # evidence_metadata by eid
#             r["eids"].update(eid)
         
#             # merge aliases
#             r["aliases"].update(generate_aliases(profile_norm, components))

#             # merge therapies (as normalized pairs)
#             r["therapies"].update((normalize(t["name"]), t["ncit_id"]) for t in therapies_list)

#             # disease meta
#             r["disease_name"] = disease_name  # keep latest label
#             r["disease_aliases"].update(disease.get("diseaseAliases") or [])
            
#             r["gene_symbol"] = mp_name_raw

#             # descriptions
#             if item.get("description"):
#                 r["descriptions"].append(item["description"].strip())

#             logger.debug("UPDATE rule: %s (evidence += 1)", key)

#     # --------------------
#     # Finalize: sort lists, stringify therapies
#     # --------------------
#     for k, r in rules.items():
#         # aliases/descriptions/aliases sort + dedupe
#         r["aliases"] = sorted(set(a for a in r["aliases"] if a))
#         r["descriptions"] = sorted(set(d for d in r.get("descriptions", []) if d))
#         r["disease_aliases"] = sorted(set(a for a in r.get("disease_aliases", []) if a and a.strip()))

#         # therapies: convert set[(name_norm, ncit_id)] → list[{name, ncit_id}]
#         # Store display name as the de-normalized best-effort (here we keep normalized for consistency).
#         t_pairs = sorted(r["therapies"], key=lambda x: (x[0], x[1] or ""))
#         r["therapies"] = [{"name": name_norm, "ncit_id": ncit_id} for (name_norm, ncit_id) in t_pairs]

#         r["eids"] = sorted(r["eids"])

#         # ensure disease_name is stripped
#         r["disease_name"] = (r.get("disease_name") or "").strip()

#     return rules

