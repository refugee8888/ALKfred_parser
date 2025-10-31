PRAGMA foreign_keys = ON;


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
variant_id TEXT PRIMARY KEY,   -- either CIViC ca_id, or your own generated UID
civic_ca_id TEXT,
hgnc_id TEXT,                  -- HGNC stable ID for the gene (if known)
gene_symbol TEXT NOT NULL,     -- e.g. "ALK"
label_display TEXT NOT NULL,   -- raw variant string, e.g. "ALK T1151dup"
label_gene_variant_norm TEXT NOT NULL,
hgvs_p TEXT,                   -- normalized protein-level HGVS if available
hgvs_c TEXT,                   -- optional: cDNA HGVS
confidence TEXT                -- HIGH/MED/LOW for mapping certainty
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


