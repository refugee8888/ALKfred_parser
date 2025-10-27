import argparse
from calendar import c
from sys import argv
import sys


from pytest import ExitCode
import alkfred.config
import sqlite3
import utils
import alkfred.config
from alkfred.etl import civic_fetch
import logging



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


def query_choices(variant_cli_choice: str, limit:int):
    
    gene_symbol = "ALK"
    if gene_symbol in variant_cli_choice or gene_symbol.lower() in variant_cli_choice:
        variant_cli_choice = utils.normalize_label(variant_cli_choice)
    else:
        variant_cli_choice = gene_symbol + " " + variant_cli_choice
        variant_cli_choice = utils.normalize_label(variant_cli_choice)
    
    conn = alkfred.config.get_conn(alkfred.config.default_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""SELECT f.eid, f.doid, f.therapy_id, f.variant_id, t.label_display, d.label_disease_norm, e.significance FROM fact_evidence AS f
                JOIN dim_evidence AS e ON e.eid = f.eid
                JOIN dim_disease AS d ON d.doid = f.doid
                JOIN dim_gene_variant AS v ON v.variant_id = f.variant_id
                JOIN dim_therapy AS t ON t.therapy_id = f.therapy_id
                WHERE v.label_gene_variant_norm = ? AND e.significance = "RESISTANCE"
                ORDER BY LOWER(t.label_display), f.eid 
                LIMIT ?
                 """,(variant_cli_choice, limit),)
    
    rows = cur.fetchall()
    row_count = len(rows)
    query_list = []
    for row in rows:
        query_list.append(dict(row))
      
   




    conn.close()
    return query_list, row_count

    
    
        
        
    
    
    
    

def build_query_parser()-> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    
    subparser = p.add_subparsers(dest="command", help="Available subcommands")
    create_parser = subparser.add_parser("query", help="Query command")
    create_parser.add_argument("--variant", type= str, required= True)
    create_parser.add_argument("--limit", type= int, default = 25)
    create_parser.add_argument("--verbose", action="store_true" )
    
    
    
    
    return p
    
    

def main(argv=None):
    
    parser = build_query_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    
    try:
        rows, rows_count = query_choices(args.variant, args.limit)
        if rows_count == 0:
            print("No rows found.")
            sys.exit(2)
        print(f"Number of rows: {rows_count}")
        for r in rows:
            print(r)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    
    
    
        
        
    
        
        
        


if __name__ == "__main__":
    main()   