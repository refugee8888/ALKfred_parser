import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from alkfred import config





DB_PATH = config.default_db_path()
JSON_PATH = Path("data/civic_raw_evidence_db.json")  # use forward slashes or raw string    

def main():

    

    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()

    data_dict = config.raw_json_list_to_dict(JSON_PATH)
    
    rows_evidence = []

    for rec in data_dict.values():
                            # iterate values, not keys
        eid= rec.get("id", None)

        source_json = json.dumps(rec.get("source", {}))
        direction = rec.get(("evidenceDirection") or "").strip()
        significance = rec.get(("significance") or "").strip()
        evidence_level = rec.get(("evidenceLevel") or "").strip()
        evidence_type = rec.get(("evidenceType") or "").strip()
        rating = rec.get(("evidenceRating") or None)
        status = rec.get(("status") or "").strip()

        src = rec.get("source") or {}
        citation_id = src.get("citationId")
        pmids = []
        if citation_id:
            pmids.append(str(citation_id))
        pmids_json = json.dumps(pmids)

        pub_year = src.get(("publicationYear") or None)
        description = rec.get(("description") or None)
        created_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
        updated_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
        



        rows_evidence.append((eid, source_json, direction, significance, evidence_level, evidence_type, rating, status, pmids_json, pub_year, description, created_at_utc, updated_at_utc))


    # Bulk insert

    cur.executemany(
        "INSERT OR IGNORE INTO dim_evidence(eid, source_json, direction, significance, evidence_level, evidence_type, rating, status, pmids_json, pub_year, description, created_at_utc, updated_at_utc) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        rows_evidence
    )
    conn.commit()


    conn.close()

if __name__ == "__main__":
    main()