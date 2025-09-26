import re
import api_calls
from utils import normalize
from typing import Optional,Any,Annotated




def generate_aliases(profile_name: str, components: list[dict]) -> list[str]:
    aliases: set[str] = set()

    # Base aliases for the whole profile
    base = profile_name.strip()
    if base:
        aliases.add(base)
    norm_base = normalize(profile_name)
    if norm_base:
        aliases.add(norm_base)

    variant_aliases: list[set[str]] = []

    for comp in components:
        raw = comp.get("variant", "") or ""
        vset: set[str] = set()

        # Always include a normalized per-variant form (if any)
        nraw = normalize(raw)
        if nraw:
            vset.add(nraw)

        # Gene + mutation (non-fusion shapes)
        tokens = re.split(r"[:\-_–/\s]+", raw)  # include en dash U+2013
        gene = tokens[0].upper() if tokens and tokens[0] else ""
        mutation = " ".join(t for t in tokens[1:] if t) if len(tokens) > 1 else ""
        if gene and mutation:
            vset.update({f"{gene} {mutation}", f"{mutation} {gene}"})

        # Fusion parsing: A-B, A::B, A/B, A–B [+ optional ' fusion']
        m = re.search(r'(?i)\b([A-Z0-9]+)\s*(?:-|::|/|–)\s*([A-Z0-9]+)(?:\s+fusion)?\b', raw)
        if m:
            a, b = m.group(1).upper(), m.group(2).upper()
            vset.update({
                f"{a}-{b} fusion", f"{a}-{b}",
                f"{b}-{a} fusion", f"{b}-{a}",
                f"{a}::{b}", f"{b}::{a}",
            })

        variant_aliases.append({re.sub(r'\s+', ' ', v).strip() for v in vset if v})

    # Flatten + filter
    flat_aliases: set[str] = set()
    for vset in variant_aliases:
        for v in vset:
            if len(v) > 3 and v.lower() not in {"in", "with", "variant"}:
                flat_aliases.add(v)

    aliases.update(flat_aliases)

    # Optional: cap to avoid downstream blowups (keep shortest first)
    # aliases = set(sorted(aliases, key=len)[:20])

    return sorted(a for a in aliases if a and len(a) > 3)

def disease_matches(disease_block, target): #this feels unnecesary since we're using openai to match diseases
    if not disease_block:
        return False
    target = target.lower().strip()
    names = [
        disease_block.get("name", "").lower().strip(),
        disease_block.get("displayName", "").lower().strip(),
        *[alias.lower().strip() for alias in disease_block.get("diseaseAliases") or []]
    ]
    return any(target in name for name in names)

def gene_in_molecular_profile(mp_name: str, gene_symbol: str) -> bool:
    """
    Returns True if gene_symbol appears in any token of the profile name,
    including fusions or composite profiles.
    """
    if not mp_name or not gene_symbol:
        return False

    gene_symbol = gene_symbol.upper()
    mp_name = mp_name.upper()

    # Split on common separators
    tokens = re.split(r'[\s\-\_:;()/\\|&]+', mp_name)
    # Also split fusions like EML4::ALK
    fusion_parts = [part.strip() for fusion in re.findall(r'([A-Z0-9]+::[A-Z0-9]+)', mp_name) for part in fusion.split("::")]

    return gene_symbol in tokens or gene_symbol in fusion_parts



def parse_resistance_entries(evidence_items: list[dict], gene_filter: str = "") -> dict[str, dict]:
    rules = {}
    profile_enrichment_cache = {}
    print("🧠 Building resistance rule DB from CIViC evidenceItems...")

    for item in evidence_items:
        mp = item.get("molecularProfile")
        if not mp or not mp.get("name"):
            continue

        raw_name = mp["name"].strip()
        profile_name = raw_name.lower().replace("::", "-")

        if gene_filter and gene_filter.lower() not in profile_name:
            continue

        if item.get("significance", "").upper() != "RESISTANCE":
            continue
        if item.get("evidenceDirection") != "SUPPORTS":
            continue

        therapies_raw = item.get("therapies") or []
        therapies = []
        seen = set()  # Set[Tuple[str, Optional[str]]]

        for t in therapies_raw:
            name = (t.get("name") or "").strip()
            if not name:
                continue
            ncit = t.get("ncitId") or None
            key = (normalize(name), ncit)   # 2-tuple literal, not tuple()

            if key in seen:
                continue
            therapies.append({"name": name, "ncit_id": ncit})
            seen.add(key)

        if not therapies:
            continue
            
            

        # for t in therapies:
        #     if t.get("name"):
        #         resistant_drugs = {  t["name"]

        #         }
        #     if t.get("ncitId"):
        #         therapy_ncitid = { t["ncitId"]}
                
        # resistant_drugs = {t["name"] for t in therapies if t.get("name")}
                          
        # if not resistant_drugs:
        #     continue

        print(f"📦 Saving profile: {profile_name} with {len(therapies)} therapies")

        # Enrichment caching
        if raw_name not in profile_enrichment_cache:
            components = api_calls.fetch_civic_molecular_profile(raw_name)
            profile_enrichment_cache[raw_name] = components
        else:
            components = profile_enrichment_cache[raw_name]

        canonical_id = next((c["ca_id"] for c in components if c["ca_id"]), profile_name)
        aliases = generate_aliases(profile_name, components)

        if profile_name not in rules:
            rules[profile_name] = {
                "canonical_id": canonical_id,
                "components": components,
                "aliases": set(aliases),
                "therapies": therapies,
                # "resistant_to": set(resistant_drugs),
                # "therapy_ncitid": set(therapy_ncitid),
                "evidence_count": 1,
                "descriptions": [item["description"].strip()] if item.get("description") else [],
                "disease_name": item["disease"]["name"],
                "disease_doid": item["disease"]["doid"],
                "disease_aliases": list(item.get("disease", {}).get("diseaseAliases", [])),

            }
        else:
            rules[profile_name]["evidence_count"] += 1
            # rules[profile_name]["resistant_to"].update(resistant_drugs)
            # rules[profile_name]["therapy_ncitid"].update(therapy_ncitid)
            rules[profile_name]["therapies"].append(therapies)
            rules[profile_name]["aliases"].update(aliases)
            rules[profile_name]["disease_name"] = item["disease"]["name"]
            rules[profile_name]["disease_doid"] = item["disease"]["doid"]
            rules[profile_name]["disease_aliases"] = item["disease"]["diseaseAliases"]
            if item.get("description"):
                rules[profile_name]["descriptions"].append(item["description"].strip())

            existing_components = {(c["variant"], c["ca_id"]) for c in rules[profile_name]["components"]}
            for c in components:
                if (c["variant"], c["ca_id"]) not in existing_components:
                    rules[profile_name]["components"].append(c)

    for entry in rules.values():
        entry["aliases"] = sorted(entry["aliases"])
        # entry["resistant_to"] = sorted(entry["resistant_to"])
        # entry["therapy_ncitid"] = sorted(entry["therapy_ncitid"])
        # entry["therapies"] = entry["therapies"]
        entry["descriptions"] = sorted(set(entry.get("descriptions", [])))
        entry["disease_name"] = entry["disease_name"].strip()
        entry["disease_doid"] = entry["disease_doid"].strip()
        entry["disease_aliases"] = sorted(set(entry.get("disease_aliases", [])))
        

    return rules
