# evidence_link_populate.py
from __future__ import annotations
import re
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from utils import normalize_label, canon_doid
from alkfred import config

# ----------------------------
# Config
# ----------------------------
DB_PATH = config.default_db_path()
RAW_JSON_PATH = Path("data/civic_raw_evidence_db.json")  # list of CIViC evidence nodes
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")





def main():

    logger = logging.getLogger(__name__)
    conn = config.get_conn(DB_PATH)
    cur = conn.cursor()


    logger.info("Table evidence_link created or already exists in %s", DB_PATH)



    cur.execute("""
    INSERT INTO evidence_link (
            eid, doid, molecular_profile_id, variant_id, ncit_id, direction, significance, pub_year
            )
            SELECT
            se.eid,
            sd.doid,
            smp.molecular_profile_id,
            sgv.variant_id,
            st.ncit_id,
            UPPER(TRIM(se.direction)),
            REPLACE(UPPER(TRIM(se.significance)), 'SENSITIVITYRESPONSE', 'SENSITIVITY'),
            se.pub_year
            FROM civic_stg_evidence            AS se
            JOIN civic_stg_disease             AS sd   ON sd.eid  = se.eid
            LEFT JOIN civic_stg_molecular_profile AS smp ON smp.eid = se.eid
            LEFT JOIN civic_stg_gene_variant   AS sgv  ON sgv.eid = se.eid
            LEFT JOIN civic_stg_therapy        AS st   ON st.eid  = se.eid
            WHERE EXISTS (SELECT 1 FROM civic_dim_evidence            AS de  WHERE de.eid  = se.eid)
            AND EXISTS (SELECT 1 FROM civic_dim_disease             AS dd  WHERE dd.doid = sd.doid)
            AND (smp.molecular_profile_id IS NULL OR EXISTS (
                    SELECT 1 FROM civic_dim_molecular_profile AS dmp WHERE dmp.molecular_profile_id = smp.molecular_profile_id))
            AND (sgv.variant_id IS NULL OR EXISTS (
                    SELECT 1 FROM civic_dim_gene_variant     AS dgv WHERE dgv.variant_id = sgv.variant_id))
            AND (st.ncit_id IS NULL OR EXISTS (
                    SELECT 1 FROM civic_dim_therapy          AS dt  WHERE dt.ncit_id = st.ncit_id))
            ON CONFLICT(eid, doid, molecular_profile_id, variant_id, ncit_id) DO NOTHING;""")
    
    
    conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
