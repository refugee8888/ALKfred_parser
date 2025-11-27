# civic_parser.py
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def gene_in_molecular_profile(mp_name: str, gene_symbol: str) -> bool:
    """
    Return True if `gene_symbol` appears as a token in `mp_name` (including split fusion parts).

    - Case-insensitive, token-aware (splits on common separators).
    - Handles fusions like "EML4::ALK" by splitting into ["EML4", "ALK"].
    - No partials (e.g., "ALK" does not match "TALK1").
    """
    if not mp_name or not gene_symbol:
        return False

    gene_symbol = gene_symbol.upper()
    mp_up = mp_name.upper()

    # Tokenize by common separators
    tokens = re.split(r"[\s\-\_:;()/\\|&]+", mp_up)

    # Split fusion tokens like EML4::ALK
    for fusion in re.findall(r"([A-Z0-9]+::[A-Z0-9]+)", mp_up):
        tokens.extend(part.strip() for part in fusion.split("::") if part.strip())

    return gene_symbol in tokens
