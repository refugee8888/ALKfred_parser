PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS civic_stg_evidence (
evidence_count INTEGER PRIMARY KEY,      
eid INTEGER NOT NULL,
source_json TEXT,
direction TEXT,
significance TEXT,
evidence_level TEXT,
evidence_type TEXT,
rating INTEGER,
status TEXT,
pmids_json TEXT,
pub_year INTEGER,
description TEXT,
created_at_utc TEXT,
updated_at_utc TEXT
);

CREATE TABLE IF NOT EXISTS civic_stg_disease(
disease_count INTEGER PRIMARY KEY,
eid INTEGER NOT NULL,
doid TEXT NOT NULL,
label_display TEXT NOT NULL,
synonyms_json TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_disease_count ON civic_stg_disease(disease_count);
CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_disease(eid);
CREATE INDEX IF NOT EXISTS idx_doid ON civic_stg_disease(doid);

CREATE TABLE IF NOT EXISTS civic_stg_molecular_profile (
molecular_profile_count INTEGER PRIMARY KEY,
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
gene_symbol TEXT NOT NULL,     
label_display TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_gene_variant(eid);
CREATE INDEX IF NOT EXISTS idx_variant_id ON civic_stg_gene_variant(variant_id);
CREATE INDEX IF NOT EXISTS idx_molecular_profile_id ON civic_stg_gene_variant(molecular_profile_id);

CREATE TABLE IF NOT EXISTS civic_stg_therapy (
therapy_id TEXT PRIMARY KEY,
eid INTEGER NOT NULL,
molecular_profile_id INTEGER NOT NULL,
ncit_id TEXT UNIQUE NULL,
label_display TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_therapy_id ON civic_stg_therapy(therapy_id);
CREATE INDEX IF NOT EXISTS idx_molecular_profile_id ON civic_stg_therapy(molecular_profile_id);
CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_therapy(eid);



CREATE TABLE IF NOT EXISTS dim_disease (
doid TEXT PRIMARY KEY,
label_display TEXT NOT NULL,
label_disease_norm TEXT NOT NULL,
synonyms_json TEXT NOT NULL DEFAULT '[]',
mondo_id TEXT,
ncit_id TEXT,
lineage_json TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_label_disease_norm ON dim_disease(label_disease_norm);


CREATE TABLE IF NOT EXISTS dim_gene_variant (
variant_id TEXT PRIMARY KEY,   
civic_ca_id TEXT,
hgnc_id TEXT,                  
gene_symbol TEXT NOT NULL,     
label_display TEXT NOT NULL,   
label_gene_variant_norm TEXT NOT NULL,
hgvs_p TEXT,                   
hgvs_c TEXT,                   
confidence TEXT           
);

CREATE INDEX IF NOT EXISTS idx_gene_symbol ON dim_gene_variant(gene_symbol);
CREATE INDEX IF NOT EXISTS idx_label_gene_variant_norm ON dim_gene_variant(label_gene_variant_norm);

CREATE TABLE IF NOT EXISTS dim_therapy (
therapy_id TEXT PRIMARY KEY,
ncit_id TEXT UNIQUE NULL,
label_display TEXT NOT NULL,
label_therapy_norm TEXT NOT NULL ,
synonyms_json TEXT NOT NULL DEFAULT '[]',
rxnorm_id TEXT,
id_combo INTEGER NOT NULL DEFAULT 0,
combo_parts_json TEXT,
class_ids_json TEXT


);


CREATE INDEX IF NOT EXISTS idx_label_therapy_norm ON dim_therapy(label_therapy_norm);

CREATE TABLE IF NOT EXISTS dim_evidence (    
eid INTEGER PRIMARY KEY,
source_json TEXT,
direction TEXT,
significance TEXT,
evidence_level TEXT,
evidence_type TEXT,
rating INTEGER,
status TEXT,
pmids_json TEXT,
pub_year INTEGER,
description TEXT,
created_at_utc TEXT,
updated_at_utc TEXT
);

CREATE INDEX IF NOT EXISTS idx_evidence_eid ON dim_evidence(eid);



CREATE TABLE IF NOT EXISTS evidence_link (
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


CREATE INDEX IF NOT EXISTS idx_link_doid_variant ON evidence_link(doid, variant_id);
CREATE INDEX IF NOT EXISTS idx_link_therapy      ON evidence_link(therapy_id);
CREATE INDEX IF NOT EXISTS idx_link_eid          ON evidence_link(eid);


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


