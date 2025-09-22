import os
import json
import sys
import api_calls
import civic_parser

from dotenv import load_dotenv
import re
from civic_parser import gene_in_molecular_profile
import logging, argparse
from openai import OpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)




load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("Missing OPENAI_API_KEY in environment or .env file")
    sys.exit(1)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))








def get_matching_diseases(user_input, evidence_items):
    disease_names = set()
    for item in evidence_items:
        if not item or not isinstance(item, dict):
            continue
        disease = item.get("disease", {})
        if not isinstance(disease, dict):
            disease = {}
        name = disease.get("name", "")
        aliases = disease.get("diseaseAliases", [])
        if name:
            disease_names.add(name.strip())
        for alias in aliases:
            if alias:
                disease_names.add(alias.strip())

    disease_names = sorted(disease_names)
    if not disease_names:
        return []

    prompt = f"""
You are a biomedical expert AI. Given this user query: '{user_input}'
and a list of known disease names, return all diseases that are likely equivalent,
closely related, or semantically interchangeable with the user's query in a clinical or molecular oncology context.

Return only a clean Python list of strings. Do NOT explain anything.

Diseases:
{json.dumps(disease_names, indent=2)}
"""

    
    try:
        print("\U0001F9E0 Asking OpenAI to match diseases...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a precise biomedical disease matcher."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=500
        )
        reply = response.choices[0].message.content

        
        if not reply:
            raise ValueError("⚠️ OpenAI returned no content in the response.")

        try:
            matched = json.loads(reply)
        except json.JSONDecodeError as e:
            # Try to extract a list using regex as a fallback
            print(f"⚠️ Failed to parse LLM output as JSON, attempting regex fallback...", file=sys.stderr)
            match = re.search(r'\[(.*?)\]', reply, re.DOTALL)
            if match:
                items = match.group(0)
                try:
                    matched = json.loads(items)
                except Exception as e2:
                    raise ValueError(f"⚠️ Fallback also failed: {e2}\nRaw reply: {reply}")
            else:
                raise ValueError(f"⚠️ Failed to extract list from LLM output. Raw reply: {reply}")
        
        print(f"\u2705 LLM matched {len(matched)} disease names: {matched}")
        return matched
    except Exception as e:
        print(f"\u274C LLM disease match error: {e}", file=sys.stderr)
        return []

def save_to_json(data, path="data/curated_resistance_db.json"):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    
    try:
        symbol = input("Enter a gene symbol: ").strip().upper()
        disease_prompt = input("Enter a disease name or acronym (e.g., NSCLC): ").strip()

        all_items = api_calls.fetch_civic_all_evidence_items()
        matched_diseases = get_matching_diseases(disease_prompt, all_items)

        filtered = []
        for ei in all_items:
            if not ei or not isinstance(ei, dict):
                continue
            mp = ei.get("molecularProfile")
            disease = ei.get("disease")
            
            if not mp or not disease:
                continue
            mp_name = mp.get("name", "")
            disease_name = disease.get("name", "")
            
            if gene_in_molecular_profile(mp_name, symbol) and any(
                disease_name.strip().lower() == md.strip().lower()
                for md in matched_diseases
            ):
                filtered.append(ei)

        if not filtered:
            print(f"\u26a0\ufe0f No evidence items found for gene '{symbol}' and disease '{disease_prompt}' (matched: {matched_diseases})")
        else:
            print(f"🧮 Total evidence items matched: {len(filtered)}")


        rules = civic_parser.parse_resistance_entries(filtered)
        save_to_json(rules)
        print(f"\u2705 Saved {len(rules)} entries to curated_resistance_db.json")

    except Exception as e:
        print(f"\u274C Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
