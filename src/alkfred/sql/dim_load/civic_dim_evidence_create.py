import json
from pathlib import Path
from datetime import datetime, timezone
from alkfred import config
import logging


DB_PATH = config.default_db_path()
JSON_PATH = Path("data/civic_raw_evidence_db.json")  # use forward slashes or raw string

logger = logging.getLogger(__name__)
def main():

    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()

    # data_dict = config.raw_json_list_to_dict(JSON_PATH)

    # rows_evidence = []

    # for rec in data_dict.values():

    #     eid = rec.get("id", None)

    #     source_json = json.dumps(rec.get("source", {}))
    #     direction = rec.get(("evidenceDirection") or "").strip().upper()
    #     significance = (
    #         rec.get(("significance") or "")
    #         .strip()
    #         .upper()
    #         .replace("SENSITIVITYRESPONSE", "SENSITIVTY")
    #     )
    #     evidence_level = rec.get(("evidenceLevel") or "").strip()
    #     evidence_type = rec.get(("evidenceType") or "").strip()
    #     rating = rec.get(("evidenceRating") or None)
    #     status = rec.get(("status") or "").strip()

    #     src = rec.get("source") or {}
    #     citation_id = src.get("citationId")
    #     pmids = []
    #     if citation_id:
    #         pmids.append(str(citation_id))
    #     pmids_json = json.dumps(pmids)

    #     pub_year = src.get(("publicationYear") or None)
    #     description = rec.get(("description") or None)
    #     created_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    #     updated_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")

    #     rows_evidence.append(
    #         (
    #             eid,
    #             source_json,
    #             direction,
    #             significance,
    #             evidence_level,
    #             evidence_type,
    #             rating,
    #             status,
    #             pmids_json,
    #             pub_year,
    #             description,
    #             created_at_utc,
    #             updated_at_utc,
    #         )
    #     )
    rows_evidence = []
    cur.execute("""SELECT   
                evidence_count,      
                eid,
                direction,
                significance,
                evidence_level,
                evidence_type,
                rating,
                status,
                pmids_json,
                pub_year,
                description,
                created_at_utc,
                updated_at_utc
                FROM civic_stg_evidence
                """)
    
    for r in cur.fetchall():
        if r[1] != None:
            significance = r[3].strip().upper().replace("SENSITIVITYRESPONSE", "SENSITIVITY")
            direction  = r[2].strip() or None
            evidence_level = r[4].strip() or None
            evidence_type = r[5].strip() or None
            status = r[7].strip() or None
            description = r[10].strip() or None
            created_at_utc = config.utc_now_iso()
            updated_at_utc = config.utc_now_iso()
            staging_table_ingest_lineage = json.dumps({"stg_created": r[11],
                                    "stg_updated": r[12]})
            rows_evidence.append((
            r[0], 
            r[1], 
            direction, 
            significance, 
            evidence_level, 
            evidence_type, 
            r[6], 
            status, 
            r[8], 
            r[9], 
            description, 
            staging_table_ingest_lineage, 
            created_at_utc, 
            updated_at_utc))
        else:
            logger.info("Evidence ID can't be empty")
            raise ValueError()

    

    cur.executemany(
        """INSERT INTO dim_evidence( 
                evidence_count,      
                eid,
                direction,
                significance,
                evidence_level,
                evidence_type,
                rating,
                status,
                pmids_json,
                pub_year,
                description,
                staging_table_ingest_lineage,
                created_at_utc,
                updated_at_utc) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows_evidence,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
