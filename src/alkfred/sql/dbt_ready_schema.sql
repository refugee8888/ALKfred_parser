
-- Run with: psql "$PG_DSN" -f /app/src/alkfred/sql/dbt_ready_schema.sql
BEGIN;

DROP TABLE IF EXISTS civic_raw_therapy           CASCADE;
DROP TABLE IF EXISTS civic_raw_gene_variant      CASCADE;
DROP TABLE IF EXISTS civic_raw_molecular_profile CASCADE;
DROP TABLE IF EXISTS civic_raw_disease           CASCADE;
DROP TABLE IF EXISTS civic_raw_evidence          CASCADE;



-- Raw tables BRONZE layer

CREATE TABLE civic_raw_evidence (
    evidence_count TEXT PRIMARY KEY,
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
    created_at_utc TEXT,
    updated_at_utc TEXT
);

CREATE INDEX idx_civic_raw_evidence_eid
    ON civic_raw_evidence(eid);


CREATE TABLE civic_raw_disease(
    disease_count TEXT PRIMARY KEY,
    eid           INTEGER NOT NULL,
    doid          TEXT NOT NULL,
    disease_name  TEXT NOT NULL,
    synonyms_json TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX idx_civic_raw_disease_count
    ON civic_raw_disease(disease_count);

CREATE INDEX idx_civic_raw_disease_eid
    ON civic_raw_disease(eid);

CREATE INDEX idx_civic_raw_disease_doid
    ON civic_raw_disease(doid);


CREATE TABLE civic_raw_molecular_profile (
    molecular_profile_count TEXT PRIMARY KEY,
    molecular_profile_id    INTEGER NOT NULL,
    eid                     INTEGER NOT NULL,
    mp_name                 TEXT NOT NULL
);

CREATE INDEX idx_civic_raw_mp_molecular_profile_id
    ON civic_raw_molecular_profile(molecular_profile_id);

CREATE INDEX idx_civic_raw_mp_eid
    ON civic_raw_molecular_profile(eid);


CREATE TABLE civic_raw_gene_variant (
    variant_id          TEXT PRIMARY KEY,
    eid                 INTEGER NOT NULL,
    molecular_profile_id INTEGER NOT NULL,
    civic_ca_id         TEXT,
    gene_symbol         TEXT,
    variant_name        TEXT
);

CREATE INDEX idx_civic_raw_gv_eid
    ON civic_raw_gene_variant(eid);

CREATE INDEX idx_civic_raw_gv_variant_id
    ON civic_raw_gene_variant(variant_id);

CREATE INDEX idx_civic_raw_gv_molecular_profile_id
    ON civic_raw_gene_variant(molecular_profile_id);


CREATE TABLE civic_raw_therapy (
    therapy_id          TEXT PRIMARY KEY,
    eid                 INTEGER NOT NULL,
    molecular_profile_id INTEGER NOT NULL,
    ncit_id             TEXT,
    therapy_name        TEXT
);

CREATE INDEX idx_civic_raw_th_therapy_id
    ON civic_raw_therapy(therapy_id);

CREATE INDEX idx_civic_raw_th_molecular_profile_id
    ON civic_raw_therapy(molecular_profile_id);

CREATE INDEX idx_civic_raw_th_eid
    ON civic_raw_therapy(eid);

COMMIT;