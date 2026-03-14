

CREATE SCHEMA IF NOT EXISTS public;
--insert correct username before grantic access; 
GRANT ALL ON SCHEMA public TO alkfred_paul;


BEGIN;

-- Raw tables BRONZE layer

CREATE TABLE IF NOT EXISTS civic_raw_evidence (
    evidence_count BIGSERIAL PRIMARY KEY,
    eid            INTEGER NOT NULL,
    direction      TEXT,
    significance   TEXT,
    evidence_level TEXT,
    evidence_type  TEXT,
    rating         INTEGER,
    status         TEXT,
    pmids_json     TEXT NOT NULL DEFAULT '[]',
    pub_year       INTEGER,
    description    TEXT,
    ingestion_run_id UUID NOT NULL,
    ingested_at_utc TEXT
   
);

CREATE INDEX IF NOT EXISTS idx_civic_raw_evidence_eid
    ON civic_raw_evidence(eid);


CREATE TABLE IF NOT EXISTS civic_raw_disease(
    disease_count BIGSERIAL PRIMARY KEY,
    eid           INTEGER NOT NULL,
    doid          TEXT,
    disease_name  TEXT NOT NULL,
    synonyms_json TEXT NOT NULL DEFAULT '[]',
    ingestion_run_id UUID NOT NULL,
    ingested_at_utc TEXT

);

CREATE INDEX IF NOT EXISTS idx_civic_raw_disease_count
    ON civic_raw_disease(disease_count);

CREATE INDEX IF NOT EXISTS idx_civic_raw_disease_eid
    ON civic_raw_disease(eid);

CREATE INDEX IF NOT EXISTS idx_civic_raw_disease_doid
    ON civic_raw_disease(doid);


CREATE TABLE IF NOT EXISTS civic_raw_molecular_profile (
    molecular_profile_count BIGSERIAL PRIMARY KEY,
    molecular_profile_id    INTEGER NOT NULL,
    eid                     INTEGER NOT NULL,
    mp_name                 TEXT NOT NULL,
    ingestion_run_id UUID NOT NULL,
    ingested_at_utc TEXT
);
CREATE INDEX IF NOT EXISTS idx_civic_raw_mp_molecular_profile_count
    ON civic_raw_molecular_profile(molecular_profile_count);
CREATE INDEX IF NOT EXISTS idx_civic_raw_mp_molecular_profile_id
    ON civic_raw_molecular_profile(molecular_profile_id);

CREATE INDEX IF NOT EXISTS idx_civic_raw_mp_eid
    ON civic_raw_molecular_profile(eid);


CREATE TABLE IF NOT EXISTS civic_raw_gene_variant (
    variant_id          BIGSERIAL PRIMARY KEY,
    eid                 INTEGER NOT NULL,
    molecular_profile_id INTEGER NOT NULL,
    civic_ca_id         TEXT,
    gene_symbol         TEXT,
    variant_name        TEXT,
    ingestion_run_id UUID NOT NULL,
    ingested_at_utc TEXT
);

CREATE INDEX IF NOT EXISTS idx_civic_raw_gv_eid
    ON civic_raw_gene_variant(eid);

CREATE INDEX IF NOT EXISTS idx_civic_raw_gv_variant_id
    ON civic_raw_gene_variant(variant_id);

CREATE INDEX IF NOT EXISTS idx_civic_raw_gv_molecular_profile_id
    ON civic_raw_gene_variant(molecular_profile_id);


CREATE TABLE IF NOT EXISTS civic_raw_therapy (
    therapy_id          BIGSERIAL PRIMARY KEY,
    eid                 INTEGER NOT NULL,
    molecular_profile_id INTEGER NOT NULL,
    ncit_id             TEXT,
    therapy_name        TEXT,
    ingestion_run_id UUID NOT NULL,
    ingested_at_utc TEXT
);

CREATE INDEX IF NOT EXISTS idx_civic_raw_th_therapy_id
    ON civic_raw_therapy(therapy_id);

CREATE INDEX IF NOT EXISTS idx_civic_raw_th_molecular_profile_id
    ON civic_raw_therapy(molecular_profile_id);

CREATE INDEX IF NOT EXISTS idx_civic_raw_th_eid
    ON civic_raw_therapy(eid);

COMMIT;