PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS civic_stg_evidence;
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


DROP TABLE IF EXISTS civic_stg_disease; 
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


DROP TABLE  IF EXISTS civic_stg_molecular_profile;
CREATE TABLE IF NOT EXISTS civic_stg_molecular_profile (
molecular_profile_count TEXT PRIMARY KEY,
molecular_profile_id INTEGER NOT NULL,
eid INTEGER NOT NULL,
mp_name TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_molecular_profile_id ON civic_stg_molecular_profile(molecular_profile_id);
CREATE INDEX IF NOT EXISTS idx_eid ON civic_stg_molecular_profile(eid);


DROP TABLE IF EXISTS civic_stg_gene_variant;
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


DROP TABLE IF EXISTS civic_stg_therapy;
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
ncit_id TEXT UNIQUE,
synonyms_json TEXT NOT NULL DEFAULT '[]',
rxnorm_id TEXT,
id_combo INTEGER NOT NULL DEFAULT 0,
combo_parts_json TEXT,
class_ids_json TEXT NOT NULL DEFAULT '[]'
);


CREATE INDEX IF NOT EXISTS idx_therapy_name_norm ON civic_dim_therapy(therapy_name_norm);
CREATE INDEX IF NOT EXISTS idx_ncit_id ON civic_dim_therapy(ncit_id);

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

DROP TABLE IF EXISTS fact_evidence;

DROP TABLE IF EXISTS evidence_link;


CREATE TABLE IF NOT EXISTS evidence_link (
eid                INTEGER NOT NULL,
doid               TEXT    NOT NULL,
molecular_profile_id TEXT,
variant_id         TEXT,
ncit_id            TEXT,
direction          TEXT    NOT NULL,
significance       TEXT    NOT NULL,
pub_year           INTEGER,
created_at_utc     TEXT    NOT NULL DEFAULT (datetime('now')),
PRIMARY KEY (eid, doid, molecular_profile_id, variant_id, ncit_id),
FOREIGN KEY (eid)  REFERENCES civic_dim_evidence(eid) ON DELETE CASCADE,
FOREIGN KEY (doid) REFERENCES civic_dim_disease(doid) ON DELETE CASCADE,
FOREIGN KEY (molecular_profile_id) REFERENCES civic_dim_molecular_profile(molecular_profile_id) ON DELETE CASCADE,
FOREIGN KEY (variant_id) REFERENCES civic_dim_gene_variant(variant_id) ON DELETE CASCADE,
FOREIGN KEY (ncit_id) REFERENCES civic_dim_therapy(ncit_id) ON DELETE CASCADE,
CHECK (direction IN ('SUPPORTS','DOES_NOT_SUPPORT','NA')),
CHECK (significance IN ('RESISTANCE','SENSITIVITY', 'ADVERSE_RESPONSE','REDUCED_SENSITIVITY',
'BETTER_OUTCOME','POOR_OUTCOME','POSITIVE','NEGATIVE','PREDISPOSITION','PROTECTIVENESS',
'ONCOGENITICITY','GAIN_OF_FUNCTION','LOSS_OF_FUNCTION','UNALTERED_FUNCTION','NEOMORPHIC',
'DOMINANT_NEGATIVE','UNKNOWN','NA'))
);

CREATE INDEX IF NOT EXISTS idx_el_eid   ON evidence_link(eid);
CREATE INDEX IF NOT EXISTS idx_el_doid  ON evidence_link(doid);
CREATE INDEX IF NOT EXISTS idx_el_ncit  ON evidence_link(ncit_id);
CREATE INDEX IF NOT EXISTS idx_el_var   ON evidence_link(variant_id);
CREATE INDEX IF NOT EXISTS idx_el_mp    ON evidence_link(molecular_profile_id);
CREATE INDEX IF NOT EXISTS idx_el_sig   ON evidence_link(significance, direction);



CREATE TABLE IF NOT EXISTS fact_evidence (
eid                  INTEGER NOT NULL,
doid                 TEXT    NOT NULL,
molecular_profile_id TEXT,
variant_id           TEXT,
ncit_id              TEXT,
direction            TEXT,
significance         TEXT,
pub_year             INTEGER,
created_at_utc       TEXT DEFAULT (datetime('now')),
PRIMARY KEY (eid, doid, molecular_profile_id, variant_id, ncit_id),


FOREIGN KEY (eid, doid, molecular_profile_id, variant_id, ncit_id)
REFERENCES evidence_link(eid, doid, molecular_profile_id, variant_id, ncit_id) ON DELETE CASCADE,
FOREIGN KEY (eid)  REFERENCES civic_dim_evidence(eid) ON DELETE CASCADE,
FOREIGN KEY (doid) REFERENCES civic_dim_disease(doid) ON DELETE CASCADE,
FOREIGN KEY (molecular_profile_id) REFERENCES civic_dim_molecular_profile(molecular_profile_id) ON DELETE CASCADE,
FOREIGN KEY (variant_id) REFERENCES civic_dim_gene_variant(variant_id) ON DELETE CASCADE,
FOREIGN KEY (ncit_id) REFERENCES civic_dim_therapy(ncit_id) ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_fact_doid ON fact_evidence(doid);
CREATE INDEX IF NOT EXISTS idx_fact_ncit ON fact_evidence(ncit_id);
CREATE INDEX IF NOT EXISTS idx_fact_variant ON fact_evidence(variant_id);
CREATE INDEX IF NOT EXISTS idx_fact_mp ON fact_evidence(molecular_profile_id);
CREATE INDEX IF NOT EXISTS idx_fact_sig_dir ON fact_evidence(significance, direction);


