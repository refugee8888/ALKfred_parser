import json







with open("data/mutation_resistance_db.json") as f:
    db = json.load(f)

class Mutation:
    def __init__(self, mutation_name: str, canonical_id: str, aliases: list[str], resistant_to: list[str], category:str):
        self.name = mutation_name
        self.canonical_id = canonical_id
        self.aliases = aliases
        self.resistant_to = resistant_to
        self.category = category
    
    @classmethod
    
    def from_mutation_name(cls, mutation_name: str, resistance_data: list[dict]):

        query = mutation_name.lower()

        for entry in resistance_data:
            if not isinstance(entry, dict):
                continue

            name = entry.get("name", "").lower()
            aliases = [a.lower() for a in entry.get("aliases", [])]

            
            if query in name or query in aliases:
                if entry.get("canonical_id", "") != None:
                

                    return cls(
                        mutation_name=entry["name"],
                        canonical_id=entry.get("canonical_id", ""),
                        aliases=entry.get("aliases", []),
                        resistant_to=entry.get("resistant_to", []),
                        category=entry.get("category", "")
                    )
            
        



        # ❌ No fuzzy fallback — strict matching only
        raise ValueError(f"Mutation '{mutation_name}' not found in resistance DB.")

    
        
        


    

class TreatmentEvent:
    def __init__(self, drug: str, start_date: str, end_date: str = "", response: str = "", resistance_mutations: list[str] = []):
        self.drug = drug
        self.start_date = start_date
        self.end_date = end_date
        self.response = response
        self.resistance_mutations = resistance_mutations or []

class Patient:
    def __init__(self, patient_id: str, cancer_type: str, treatment_history: list[TreatmentEvent], mutation_history: list[Mutation]):
        self.patient_id = patient_id
        self.cancer_type = cancer_type
        self.treatment_history = treatment_history
        self.mutation_history = mutation_history




mutation = Mutation.from_mutation_name("ALK", db)
print(mutation.name)
print(mutation.canonical_id)
print(mutation.category)
print(mutation.resistant_to)



