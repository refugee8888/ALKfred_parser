import re
import itertools
import api_calls
import openai
import numpy as np
import os
from utils import normalize



def generate_aliases(profile_name: str, components: list[dict]) -> list[str]:
    aliases = set() #making sure no duplicate aliases are created
    raw_aliases = set() #making sure no duplicate raw aliases are created

    aliases.add(profile_name.strip()) #adding the profile name to the aliases and striping of extra white spaces
    aliases.add(normalize(profile_name)) #adding the normalized profile name to the aliases

    variant_aliases = [] #we're storing variant aliases in a list
    for comp in components: #we're iterating through the components which we will fetch from the api calls in out pasing function
        raw = comp["variant"] #we're getting the variant from the component which will be a molecular profile dictionary 
        raw_aliases.add(raw) # we're adding the comp["variant"] to the raw_aliases set to make sure no duplicates are created

        tokens = re.split(r"[:\-_\s]+", raw) #we're splitting the raw variant by common separators
        gene = tokens[0].upper() if tokens else "" #we're getting the gene symbol from the tokens and make it uppercase
        mutation = " ".join(tokens[1:]) if len(tokens) > 1 else "" #we're getting the mutation from the tokens

        vset = set([ #we're creating a set of aliases for the variant, reasonable presumptions for aliases
            raw,
            normalize(raw), #using the mormailze method to normalize the raw variant
            f"{gene} {mutation}".strip(), #we're creating an alias for the variant
            f"{mutation} in {gene}".strip(), #we're creating an alias for the variant
            f"{gene} exon variant {mutation}".strip() #we're creating an alias for the variant
        ])

        if "fusion" in raw.lower(): #we're checking if the raw variant contains the word "fusion"
            partner = raw.split("::")[0] if "::" in raw else "" #we're getting the partner gene from the raw variant only if this "::" symbol is in the string and we're splitting by it
            fusion_gene = gene #we're getting the fusion gene from the raw variant; not sure if this is ok; we're always assuming that the ALK gene is second and the partner gene comes first; what happens if there's a ALK :: EML4 fusion
            vset.update([ #we're updating the vset with the following aliases
                f"{partner}-{fusion_gene}", #we're creating an alias for the variant
                f"{fusion_gene} fusion",
                f"{partner} fused to {fusion_gene}",
                f"{fusion_gene} translocation",
            ])
        if "t1151" in raw.lower(): #we're checking if the raw variant contains the word "t1151"
            vset.update(["T1151_L1152INS", "T1151dup"]) #we're updating the vset with the following aliases

        variant_aliases.append(vset) #we're appending the vset to the variant_aliases list

    # Flatten, clean, deduplicate
    flat_aliases = set() #we're creating a set of flattened aliases
    for vset in variant_aliases: #we're iterating through the variant_aliases list by vset
        for v in vset: #we're iterating through the vset
            if v and len(v) > 2: #we're checking if the alias is not empty and has more than 2 characters
                flat_aliases.add(v.strip()) #we're adding the alias to the flat_aliases set for deduplication and we're also stripping off spaces

    # Filter bad tokens BEFORE adding to aliases
    flat_aliases = [a for a in flat_aliases if len(a) > 3 and a.lower() not in {"in", "with", "variant"}] #we're filtering out aliases that are less than 3 characters and contain the words "in", "with", or "variant"

    aliases.update(flat_aliases)

    # Cross-product aliases
    for combo in itertools.combinations(flat_aliases, 2): #we're iterating infinitely through all possible combos of 2 tokens in the flat_aliases set
        aliases.add(f"{combo[0]} {combo[1]}") #we're adding the combo to the aliases set
        aliases.add(f"{combo[1]} with {combo[0]}") #we're adding the combo to the aliases set

    return sorted(set(a.strip() for a in aliases if a and len(a) > 3)) #we're returning the sorted set of aliases

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

        therapies = item.get("therapies", [])
        resistant_drugs = {t["name"] for t in therapies if t.get("name")}
        if not resistant_drugs:
            continue

        print(f"📦 Saving profile: {profile_name} with {len(resistant_drugs)} resistant drugs")

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
                "resistant_to": set(resistant_drugs),
                "evidence_count": 1,
                "descriptions": [item["description"].strip()] if item.get("description") else [],
                "disease_name": item["disease"]["name"],
                "disease_aliases": list(item.get("disease", {}).get("diseaseAliases", [])),

            }
        else:
            rules[profile_name]["evidence_count"] += 1
            rules[profile_name]["resistant_to"].update(resistant_drugs)
            rules[profile_name]["aliases"].update(aliases)
            rules[profile_name]["disease_name"] = item["disease"]["name"]
            rules[profile_name]["disease_aliases"] = item["disease"]["diseaseAliases"]
            if item.get("description"):
                rules[profile_name]["descriptions"].append(item["description"].strip())

            existing_components = {(c["variant"], c["ca_id"]) for c in rules[profile_name]["components"]}
            for c in components:
                if (c["variant"], c["ca_id"]) not in existing_components:
                    rules[profile_name]["components"].append(c)

    for entry in rules.values():
        entry["aliases"] = sorted(entry["aliases"])
        entry["resistant_to"] = sorted(entry["resistant_to"])
        entry["descriptions"] = sorted(set(entry.get("descriptions", [])))
        entry["disease_name"] = entry["disease_name"].strip()
        entry["disease_aliases"] = sorted(set(entry.get("disease_aliases", [])))
        

    return rules
