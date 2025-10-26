import argparse
from calendar import c
import alkfred.config
import sqlite3
import utils

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


def query_choices(choice: str) -> list:
    # gene_symbol = "ALK"
    # if gene_symbol not in choice or gene_symbol.lower() not in choice:
    #     choice = gene_symbol + " " + choice
    #     choice = utils.normalize_label(choice)
    # else:
    #     choice = utils.normalize_label(choice)
    
    conn = alkfred.config.get_conn(alkfred.config.default_db_path())
    cur = conn.cursor()
    
    cur.execute("""SELECT label_gene_variant_norm FROM dim_gene_variant""")
    
    rows = [dict[str,str](r) for r in cur.fetchall()]
    variant_display_name_choices = []
    for row in rows:
        x = row.get("label_gene_variant_norm","") or None
        variant_display_name_choices.append(x)
    print(variant_display_name_choices)
    if choice in variant_display_name_choices:
        return True
    else:
        raise ValueError("Wrong variant name")

def build_query_parser():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command", help="Available subcommands")
    create_parser = subparser.add_parser("query", help="Query command")
    create_parser.add_argument("--variant", choices=input() )
    create_parser.add_argument("name", choices=input(f"") )
    

def main():
    query("dim_disease","3908")


if __name__ == "__main__":
    main()  