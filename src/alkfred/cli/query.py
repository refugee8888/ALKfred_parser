import argparse
import alkfred.config
import sqlite3

ALLOWED = {"dim_disease", "dim_evidence", "dim_gene_variant"}
#we want to query by cli flags so we want a flag to represent a module

def query(table,*args) -> str:
    conn = alkfred.config.get_conn(db_path ="/app/data/alkfred.sqlite")
    cur = conn.cursor()
    
    if table not in ALLOWED:
        raise ValueError("Couldn't match a table to the query")

    cur.execute(f"SELECT * FROM {table} WHERE doid = ?", args)
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        print (r)
    cur.close()





# def build_query_parser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--effect",)

def main():
    query("dim_disease","3908")


if __name__ == "__main__":
    main()  