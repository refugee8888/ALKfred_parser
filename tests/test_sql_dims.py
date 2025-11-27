# tests/test_dim_disease_unit.py
import sqlite3

def test_dim_disease_insert_and_select(tmp_path):
    # Use an isolated DB per test
    db = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE civic_dim_disease (
            doid TEXT PRIMARY KEY,
            disease_name TEXT NOT NULL,
            disease_name_norm TEXT NOT NULL,
            synonyms_json TEXT CHECK (json_valid(synonyms_json)),
            mondo_id TEXT,
            ncit_id TEXT,
            lineage_json TEXT NOT NULL DEFAULT '[]'
        );
    """)
    # Insert a complete row that satisfies NOT NULL constraints
    cur.execute(
        "INSERT INTO civic_dim_disease (doid, disease_name, disease_name_norm) VALUES (?,?,?)",
        ("3908", "Lung Non-small Cell Carcinoma", "lung_non-small_cell_carcinoma"),
    )
    conn.commit()

    cur.execute("SELECT doid, disease_name FROM civic_dim_disease WHERE doid = ?", ("3908",))
    row = cur.fetchone()
    assert row is not None
    assert row[0] == "3908"
    assert row[1] == "Lung Non-small Cell Carcinoma"

    conn.close()

    

    




