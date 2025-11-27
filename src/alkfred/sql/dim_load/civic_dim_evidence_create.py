import json
from pathlib import Path
from alkfred import config
import logging



JSON_PATH = Path("data/civic_raw_evidence_db.json")  

logger = logging.getLogger(__name__)
def main():

    conn = config.postgres_conn()
    cur = conn.cursor()

    rows_evidence = []
    cur.execute("""SELECT      
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
        if r[0] is not None:
            significance = r[2].strip().upper().replace("SENSITIVITYRESPONSE", "SENSITIVITY")
            direction  = r[1].strip() or None
            evidence_level = r[3].strip() or None
            evidence_type = r[4].strip() or None
            status = r[6].strip() or None
            description = r[9].strip() or None
            created_at_utc = config.utc_now_iso()
            updated_at_utc = config.utc_now_iso()
            staging_table_ingest_lineage = json.dumps({"stg_created": r[10],
                                    "stg_updated": r[11]})
            rows_evidence.append((
            r[0],
            direction, 
            significance, 
            evidence_level, 
            evidence_type, 
            r[5], 
            status, 
            r[7], 
            r[8], 
            description, 
            staging_table_ingest_lineage, 
            created_at_utc, 
            updated_at_utc))
        else:
            logger.info("Evidence ID can't be empty")
            raise ValueError()

    

    cur.executemany(
        """INSERT INTO civic_dim_evidence (         
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
                updated_at_utc
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT(eid) DO UPDATE SET
        direction = COALESCE(excluded.direction, civic_dim_evidence.direction),
        significance = COALESCE(excluded.significance, civic_dim_evidence.significance),
        staging_table_ingest_lineage = CASE
                                    WHEN excluded.staging_table_ingest_lineage IS NOT NULL
                                    AND excluded.staging_table_ingest_lineage != '[]'
                                    THEN excluded.staging_table_ingest_lineage
                                    ELSE civic_dim_evidence.staging_table_ingest_lineage
                                    END,
        pmids_json = CASE
                    WHEN excluded.pmids_json IS NOT NULL
                    AND excluded.pmids_json != '[]'
                    THEN excluded.pmids_json
                    ELSE civic_dim_evidence.pmids_json
                    END,
        evidence_level = COALESCE(excluded.evidence_level, civic_dim_evidence.evidence_level),
        evidence_type = COALESCE(excluded.evidence_type, civic_dim_evidence.evidence_type),
        rating = COALESCE(excluded.rating, civic_dim_evidence.rating),
        status = COALESCE(excluded.status, civic_dim_evidence.status),
        description = COALESCE(excluded.description, civic_dim_evidence.description),
        updated_at_utc = COALESCE(excluded.updated_at_utc, civic_dim_evidence.updated_at_utc);""",
        rows_evidence,
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
