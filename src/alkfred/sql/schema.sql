PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS civic_stg_evidence (
evidence_count TEXT PRIMARY KEY,      
eid INTEGER NOT NULL,
direction TEXT,
significance TEXT,
evidence_level TEXT,
evidence_type TEXT,
rating INTEGER,
status TEXT,
pmids_json TEXT NOT NULL DEFAULT '[]',
pub_year INTEGER,
description TEXT,
created_at_utc TEXT,
updated_at_utc TEXT
);

CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_evidence(eid);

CREATE TABLE IF NOT EXISTS civic_stg_disease(
disease_count TEXT PRIMARY KEY,
eid INTEGER NOT NULL,
doid TEXT NOT NULL,
disease_name TEXT NOT NULL,
synonyms_json TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_disease_count ON civic_stg_disease(disease_count);
CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_disease(eid);
CREATE INDEX IF NOT EXISTS idx_doid ON civic_stg_disease(doid);

CREATE TABLE IF NOT EXISTS civic_stg_molecular_profile (
molecular_profile_count TEXT PRIMARY KEY,
molecular_profile_id INTEGER NOT NULL,
eid INTEGER NOT NULL,
mp_name TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_molecular_profile_id ON civic_stg_molecular_profile(molecular_profile_id);
CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_molecular_profile(eid);

CREATE TABLE IF NOT EXISTS civic_stg_gene_variant (
variant_id TEXT PRIMARY KEY,
eid INTEGER NOT NULL,
molecular_profile_id INTEGER NOT NULL,
civic_ca_id TEXT,                
gene_symbol TEXT,     
variant_name TEXT
);
CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_gene_variant(eid);
CREATE INDEX IF NOT EXISTS idx_variant_id ON civic_stg_gene_variant(variant_id);
CREATE INDEX IF NOT EXISTS idx_molecular_profile_id ON civic_stg_gene_variant(molecular_profile_id);

CREATE TABLE IF NOT EXISTS civic_stg_therapy (
therapy_id TEXT PRIMARY KEY,
eid INTEGER NOT NULL,
molecular_profile_id INTEGER NOT NULL,
ncit_id TEXT,
therapy_name TEXT
);

CREATE INDEX IF NOT EXISTS idx_therapy_id ON civic_stg_therapy(therapy_id);
CREATE INDEX IF NOT EXISTS idx_molecular_profile_id ON civic_stg_therapy(molecular_profile_id);
CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_therapy(eid);



CREATE TABLE IF NOT EXISTS civic_dim_disease (
doid TEXT PRIMARY KEY,
disease_name TEXT NOT NULL,
disease_name_norm TEXT NOT NULL,
synonyms_json TEXT NOT NULL CHECK (json_valid(synonyms_json)),
mondo_id TEXT,
ncit_id TEXT,
lineage_json TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_doid ON civic_dim_disease(doid);
CREATE INDEX IF NOT EXISTS idx_disease_name_norm ON civic_dim_disease(disease_name_norm);

CREATE TABLE IF NOT EXISTS civic_dim_molecular_profile(
molecular_profile_id INTEGER PRIMARY KEY,
mp_name TEXT NOT NULL,
mp_name_norm TEXT NOT NULL

);

CREATE TABLE IF NOT EXISTS civic_dim_gene_variant (
variant_id TEXT PRIMARY KEY,   
civic_ca_id TEXT,
hgnc_id TEXT,                  
gene_symbol TEXT NOT NULL,     
variant_name TEXT NOT NULL,   
variant_name_norm TEXT NOT NULL,
hgvs_p TEXT,                   
hgvs_c TEXT            
);

CREATE INDEX IF NOT EXISTS idx_gene_symbol ON civic_dim_gene_variant(gene_symbol);
CREATE INDEX IF NOT EXISTS idx_variant_name_norm ON civic_dim_gene_variant(variant_name_norm);

CREATE TABLE IF NOT EXISTS civic_dim_therapy (
therapy_name_norm TEXT PRIMARY KEY,
therapy_name TEXT NOT NULL,
ncit_id TEXT,
synonyms_json TEXT NOT NULL DEFAULT '[]',
rxnorm_id TEXT,
id_combo INTEGER NOT NULL DEFAULT 0,
combo_parts_json TEXT,
class_ids_json TEXT NOT NULL DEFAULT '[]'
);


CREATE INDEX IF NOT EXISTS idx_therapy_name_norm ON civic_dim_therapy(therapy_name_norm);

CREATE TABLE IF NOT EXISTS civic_dim_evidence (  
eid INTEGER PRIMARY KEY,
direction TEXT,
significance TEXT,
evidence_level TEXT,
evidence_type TEXT,
rating INTEGER,
status TEXT,
pmids_json TEXT NOT NULL DEFAULT '[]',
pub_year INTEGER,
description TEXT,
staging_table_ingest_lineage TEXT NOT NULL DEFAULT '[]',
created_at_utc TEXT,
updated_at_utc TEXT
);

CREATE INDEX IF NOT EXISTS idx_evidence_eid ON civic_dim_evidence(eid);



CREATE TABLE IF NOT EXISTS civic_evidence_link (
  eid             INTEGER NOT NULL,
  doid            TEXT    NOT NULL,
  variant_id      TEXT    NOT NULL,
  therapy_id      TEXT    NOT NULL,
  mp_name         TEXT,         -- optional provenance
  therapy_label   TEXT,         -- optional provenance (as seen in CIViC)
  created_at_utc  TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  run_id          TEXT,
  PRIMARY KEY (eid, doid, variant_id, therapy_id),
  FOREIGN KEY (eid)        REFERENCES dim_evidence(eid),
  FOREIGN KEY (doid)       REFERENCES dim_disease(doid),
  FOREIGN KEY (variant_id) REFERENCES dim_gene_variant(variant_id),
  FOREIGN KEY (therapy_id)    REFERENCES dim_therapy(therapy_id)
);


CREATE INDEX IF NOT EXISTS idx_link_doid_variant ON civic_evidence_link(doid, variant_id);
CREATE INDEX IF NOT EXISTS idx_link_therapy      ON civic_evidence_link(therapy_id);
CREATE INDEX IF NOT EXISTS idx_link_eid          ON civic_evidence_link(eid);


CREATE TABLE IF NOT EXISTS fact_evidence (
fact_id         TEXT PRIMARY KEY,
eid             INTEGER NOT NULL,
variant_id      TEXT NOT NULL,
doid            TEXT NOT NULL,
therapy_id      TEXT NOT NULL,
direction       TEXT NOT NULL DEFAULT 'N/A',
significance    TEXT NOT NULL DEFAULT 'N/A',
created_at_utc  TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
run_id          TEXT,
FOREIGN KEY (eid)        REFERENCES dim_evidence(eid),
FOREIGN KEY (variant_id) REFERENCES dim_gene_variant(variant_id),
FOREIGN KEY (doid)       REFERENCES dim_disease(doid),
FOREIGN KEY (therapy_id)    REFERENCES dim_therapy(therapy_id)
);


CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_tuple
ON fact_evidence(eid, doid, variant_id, therapy_id);

CREATE INDEX IF NOT EXISTS idx_fact_doid_dir ON fact_evidence(doid, direction);
CREATE INDEX IF NOT EXISTS idx_fact_variant ON fact_evidence(variant_id);
CREATE INDEX IF NOT EXISTS idx_fact_therapy ON fact_evidence(therapy_id);
CREATE INDEX IF NOT EXISTS idx_fact_eid ON fact_evidence(eid);
CREATE INDEX IF NOT EXISTS idx_fact_keys ON fact_evidence(variant_id, therapy_id, doid);
CREATE INDEX IF NOT EXISTS idx_fact_semantics ON fact_evidence(direction, significance);


