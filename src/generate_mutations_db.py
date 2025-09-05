import json

with open("data/curated_resistance_db.json", "r") as f:
    db = json.load(f)
FIRST_GEN_ALK_INHIBITORS = ["Crizotinib"]
SECOND_GEN_ALK_INHIBITORS = ["Ceritinib", "Alectinib", "Brigatinib"]
THIRD_GEN_ALK_INHIBITORS = ["Lorlatinib"]
mutations = {}
for profile in db.values():
    aliases = profile.get("aliases",[])
    resistant_to = profile.get("resistant_to",[])
    for component in profile["components"]:
        mutation_name = component.get("variant")
        canonical_id = component.get("ca_id")
        if not mutation_name:
            continue
        if mutation_name not in mutations:
            mutations[mutation_name] = {
                "name": mutation_name,
                "canonical_id": canonical_id,
                "aliases": set(aliases),
                "resistant_to": set(resistant_to),
                "category": ""
            }
    
        mutations[mutation_name]["aliases"].update(aliases)
        mutations[mutation_name]["resistant_to"].update(resistant_to)
        if any(drug in resistant_to for drug in SECOND_GEN_ALK_INHIBITORS + THIRD_GEN_ALK_INHIBITORS):
            mutations[mutation_name]["category"] = "resistant"
        elif any(drug in resistant_to for drug in FIRST_GEN_ALK_INHIBITORS):
            mutations[mutation_name]["category"] = "driver"
        else:
            mutations[mutation_name]["category"] = "unknown"

       
flat_mutations = []
for entry in mutations.values():
    flat_mutations.append({
        "name": entry["name"],
        "canonical_id": entry["canonical_id"],
        "aliases": sorted(entry["aliases"]),
        "resistant_to": sorted(entry["resistant_to"]),
        "category": entry["category"]
    })

with open("data/mutation_resistance_db.json", "w") as f:
    json.dump(flat_mutations, f, indent=2)

print(f"✅ Saved {len(flat_mutations)} mutation entries.")