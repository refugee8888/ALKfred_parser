
# generate_mutations_db.py
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from utils import normalize

logger = logging.getLogger(__name__)

# -----------------------------
# Default inhibitor generation mapping
# (You can override with --map path to a JSON/YAML file.)
# Names are compared case/space/sep-insensitively via `normalize`.
# NCIt IDs are compared verbatim (string equality).
# -----------------------------
DEFAULT_MAP = {
    "first": {
        "names": ["Crizotinib"],
        "ncit_ids": ["C74061"],           # Crizotinib
    },
    "second": {
        "names": ["Alectinib", "Ceritinib", "Brigatinib"],
        "ncit_ids": ["C101790", "C91133", "C111488"],  # Alectinib, Ceritinib, Brigatinib
    },
    "third": {
        "names": ["Lorlatinib"],
        "ncit_ids": ["C132962"],         # Lorlatinib
    },
}


def load_mapping(path: str | None) -> dict[str, dict[str, list[str]]]:
    """
    Load inhibitor generation mapping from optional file, else return DEFAULT_MAP.

    The file may be JSON or YAML (by extension). YAML requires PyYAML installed.
    Expected structure:
    {
      "first":  {"names": [...], "ncit_ids": [...]},
      "second": {"names": [...], "ncit_ids": [...]},
      "third":  {"names": [...], "ncit_ids": [...]}
    }
    """
    if not path:
        return DEFAULT_MAP
    p = Path(path)
    if not p.exists():
        logger.warning("Mapping file %s not found; using defaults.", p)
        return DEFAULT_MAP

    try:
        if p.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except Exception as e:
                logger.error("PyYAML not installed but YAML file provided: %s", e)
                return DEFAULT_MAP
            with p.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        else:
            with p.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        # Basic sanity
        for gen in ("first", "second", "third"):
            data.setdefault(gen, {"names": [], "ncit_ids": []})
            data[gen].setdefault("names", [])
            data[gen].setdefault("ncit_ids", [])
        return data
    except Exception as e:
        logger.error("Failed to load mapping from %s: %s. Using defaults.", p, e)
        return DEFAULT_MAP


def classify_category(
    therapy_pairs: set[tuple[str, str | None]],
    mapping: dict[str, dict[str, list[str]]],
) -> str:
    """
    Given therapies as a set of (name_norm, ncit_id), return one of:
    - "resistant" if any SECOND or THIRD gen inhibitor appears
    - "driver" if any FIRST gen inhibitor appears (and none of 2nd/3rd)
    - "unknown" otherwise
    """
    # precompute normalized-name sets
    first_names = {normalize(n) for n in mapping["first"]["names"]}
    second_names = {normalize(n) for n in mapping["second"]["names"]}
    third_names = {normalize(n) for n in mapping["third"]["names"]}

    first_ids = set(mapping["first"]["ncit_ids"])
    second_ids = set(mapping["second"]["ncit_ids"])
    third_ids = set(mapping["third"]["ncit_ids"])

    def has_any(pairs: set[tuple[str, str | None]], names: set[str], ids: set[str]) -> bool:
        for n_norm, nid in pairs:
            if n_norm in names:
                return True
            if nid and nid in ids:
                return True
        return False

    if has_any(therapy_pairs, second_names | third_names, second_ids | third_ids):
        return "resistant"
    if has_any(therapy_pairs, first_names, first_ids):
        return "driver"
    return "unknown"


def to_display_therapies(therapy_pairs: set[tuple[str, str | None]]) -> list[dict[str, Any]]:
    """
    Convert set of (name_norm, ncit_id) → sorted list of {name, ncit_id}.
    We keep the normalized name here for determinism (you can switch to display names later).
    """
    out = [{"name": n, "ncit_id": nid} for (n, nid) in therapy_pairs]
    out.sort(key=lambda x: (x["name"], x["ncit_id"] or ""))
    return out


def build_mutations(curated_rules: dict[str, dict], mapping: dict[str, dict[str, list[str]]]) -> list[dict[str, Any]]:
    """
    Build a flat mutation-level DB from curated profile-level resistance rules.

    Input (per rule value) expected fields (new schema):
      - components: list[{variant: str, ca_id: str|None}]
      - aliases: list[str]
      - therapies: list[{name: str (normalized), ncit_id: str|None}]
      - resistant_to: list[str]                   # optional (back-compat)
      - disease_doid: str                         # not used here, but present
      - evidence_count: int
    Older schema compatibility:
      - If 'therapies' missing, fall back to names from 'resistant_to'.

    Output (per mutation):
      {
        "name": str,                               # component.variant
        "canonical_id": str|None,                  # component.ca_id (first seen)
        "aliases": [str, ...],                     # union of profile aliases
        "therapies": [{"name": str, "ncit_id": str|None}, ...],  # union across profiles
        "resistant_to": [str, ...],                # names only, derived from therapies (normalized)
        "category": "resistant"|"driver"|"unknown",
        "profiles": [str, ...]                     # keys of profiles where this mutation appeared
      }
    """
    mutations: dict[str, dict[str, Any]] = {}

    for profile_key, rule in curated_rules.items():
        aliases = rule.get("aliases", []) or []
        components = rule.get("components", []) or []

        # Build therapy pairs from either 'therapies' list or legacy 'resistant_to' names.
        therapy_pairs: set[tuple[str, str | None]] = set()
        if rule.get("therapies"):
            for t in rule["therapies"]:
                tname = normalize((t.get("name") or "").strip())
                if not tname:
                    continue
                nid = t.get("ncit_id")
                therapy_pairs.add((tname, nid))
        else:
            # legacy
            for name in rule.get("resistant_to", []) or []:
                tname = normalize((name or "").strip())
                if tname:
                    therapy_pairs.add((tname, None))

        # For every component (i.e., variant) in this profile, accumulate info
        for comp in components:
            mname = (comp.get("variant") or "").strip()
            if not mname:
                continue
            ca_id = comp.get("ca_id")

            if mname not in mutations:
                mutations[mname] = {
                    "name": mname,
                    "canonical_id": ca_id,
                    "aliases": set(),                          # will convert to list later
                    "therapies": set(),                        # set[(name_norm, ncit_id)]
                    "resistant_to": set(),                     # set[name_norm]
                    "category": "",                            # to be filled
                    "profiles": set(),                         # set[str]
                }

            m = mutations[mname]
            # prefer first non-null canonical id
            if not m["canonical_id"] and ca_id:
                m["canonical_id"] = ca_id

            # merge aliases from the profile
            for a in aliases:
                a = (a or "").strip()
                if a:
                    m["aliases"].add(a)

            # merge therapies
            m["therapies"].update(therapy_pairs)
            m["resistant_to"].update(n for (n, _nid) in therapy_pairs)

            # remember which profiles this mutation came from
            m["profiles"].add(profile_key)

    # finalize & classify
    out: list[dict[str, Any]] = []
    for entry in mutations.values():
        therapy_list = to_display_therapies(entry["therapies"])
        category = classify_category(entry["therapies"], mapping)

        out.append({
            "name": entry["name"],
            "canonical_id": entry["canonical_id"],
            "aliases": sorted(entry["aliases"]),
            "therapies": therapy_list,
            "resistant_to": sorted(entry["resistant_to"]),   # keep for back-compat / simple search
            "category": category,
            "profiles": sorted(entry["profiles"]),
        })

    # deterministic output
    out.sort(key=lambda x: (x["name"].lower(), x["canonical_id"] or ""))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Build mutation-level resistance DB from curated profile rules.")
    ap.add_argument("--in", dest="inp", default="data/curated_resistance_db.json", help="Input curated rules JSON path")
    ap.add_argument("--out", dest="out", default="data/mutation_resistance_db.json", help="Output mutations JSON path")
    ap.add_argument("--map", dest="map_path", default=None, help="Optional JSON/YAML mapping for inhibitor generations")
    ap.add_argument("--verbose", action="store_true", help="Enable DEBUG logging")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    inp = Path(args.inp)
    out = Path(args.out)

    if not inp.exists():
        logger.error("Input file not found: %s", inp)
        return 2

    mapping = load_mapping(args.map_path)

    try:
        with inp.open("r", encoding="utf-8") as fh:
            curated = json.load(fh)
    except Exception as e:
        logger.error("Failed to read %s: %s", inp, e)
        return 3

    if not isinstance(curated, dict):
        logger.error("Expected dict at top level of curated rules, got %s", type(curated))
        return 4

    mutations = build_mutations(curated, mapping)

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(mutations, fh, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Failed to write %s: %s", out, e)
        return 5

    print(f"✅ Saved {len(mutations)} mutation entries to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
