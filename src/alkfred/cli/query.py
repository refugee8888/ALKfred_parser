import argparse
from calendar import c
from sys import argv
import sys
from typing import Any, AnyStr

from pytest import ExitCode
import alkfred.config
import sqlite3
import utils
import alkfred.config
from alkfred.etl import civic_fetch
import logging

logger = logging.getLogger(__name__)

def query_choices(variant_cli_choice: str, limit:int, significance: str, disease: str):

    significance_list = ["RESISTANCE", "SENSITIVITY"]
    if significance.lower() == significance_list[0].lower() or significance.lower() in significance_list[0].lower():
        significance = "RESISTANCE"
    elif significance.lower() == significance_list[1].lower() or significance.lower() in significance_list[1].lower():
        significance = "SENSITIVITY"
    elif significance.lower() == "" or significance.lower() == "all":
        significance = "all"
    else:
        raise ValueError("Please input relevant significance information")
    

    
    gene_symbol = "ALK"
    if gene_symbol in variant_cli_choice or gene_symbol.lower() in variant_cli_choice:
        variant_cli_choice = utils.normalize_label(variant_cli_choice)
    else:
        variant_cli_choice = gene_symbol + " " + variant_cli_choice
        variant_cli_choice = utils.normalize_label(variant_cli_choice)
    logger.info("Final query input: %s", variant_cli_choice)
    
    try:
        conn = alkfred.config.get_conn(alkfred.config.default_db_path())
        logger.info("Connected to database: %s", alkfred.config.default_db_path())
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        

        #query by all significance and all disease and all significance with user input disease
        if significance == "" or significance == "all":
            if disease == "" or disease == "all":
                query = """SELECT f.eid, f.doid, f.therapy_id, f.variant_id, t.label_display, d.label_disease_norm, e.significance FROM fact_evidence AS f
                    JOIN dim_evidence AS e ON e.eid = f.eid
                    JOIN dim_disease AS d ON d.doid = f.doid
                    JOIN dim_gene_variant AS v ON v.variant_id = f.variant_id
                    JOIN dim_therapy AS t ON t.therapy_id = f.therapy_id
                    WHERE v.label_gene_variant_norm = ?
                    ORDER BY LOWER(t.label_display), f.eid 
                    LIMIT ?

                    """
                params = [variant_cli_choice, limit]
                cur.execute(query,params)
                rows = cur.fetchall()
                row_count = len(rows)
                query_list = []
                for row in rows:
                    query_list.append(dict(row))

            else:
                query = """SELECT f.eid, f.doid, f.therapy_id, f.variant_id, t.label_display, d.label_disease_norm, e.significance FROM fact_evidence AS f
                    JOIN dim_evidence AS e ON e.eid = f.eid
                    JOIN dim_disease AS d ON d.doid = f.doid
                    JOIN dim_gene_variant AS v ON v.variant_id = f.variant_id
                    JOIN dim_therapy AS t ON t.therapy_id = f.therapy_id
                    WHERE v.label_gene_variant_norm = ? AND d.label_disease_norm = ?
                    ORDER BY LOWER(t.label_display), f.eid 
                    LIMIT ?

                    """
                params = [variant_cli_choice, disease, limit]
                cur.execute(query,params)
                rows = cur.fetchall()
                row_count = len(rows)
                query_list = []
                for row in rows:
                    query_list.append(dict(row))
        #query for input significance but all disease and input significance and specified disease
        if significance == "RESISTANCE" or significance == "SENSITIVITY":
            if disease == "" or disease == "all":
                query = """SELECT f.eid, f.doid, f.therapy_id, f.variant_id, t.label_display, d.label_disease_norm, e.significance FROM fact_evidence AS f
                            JOIN dim_evidence AS e ON e.eid = f.eid
                            JOIN dim_disease AS d ON d.doid = f.doid
                            JOIN dim_gene_variant AS v ON v.variant_id = f.variant_id
                            JOIN dim_therapy AS t ON t.therapy_id = f.therapy_id
                            WHERE v.label_gene_variant_norm = ? AND e.significance = ?
                            ORDER BY LOWER(t.label_display), f.eid 
                            LIMIT ?
                            """
                params = [variant_cli_choice, significance,limit]

                cur.execute(query,params)
                rows = cur.fetchall()
                row_count = len(rows)
                query_list = []
                for row in rows:
                    query_list.append(dict(row))
            else:
                query = """SELECT f.eid, f.doid, f.therapy_id, f.variant_id, t.label_display, d.label_disease_norm, e.significance FROM fact_evidence AS f
                            JOIN dim_evidence AS e ON e.eid = f.eid
                            JOIN dim_disease AS d ON d.doid = f.doid
                            JOIN dim_gene_variant AS v ON v.variant_id = f.variant_id
                            JOIN dim_therapy AS t ON t.therapy_id = f.therapy_id
                            WHERE v.label_gene_variant_norm = ? AND e.significance = ? AND d.label_disease_norm = ?
                            ORDER BY LOWER(t.label_display), f.eid 
                            LIMIT ?
                            """
                params = [variant_cli_choice, significance, disease, limit]

                cur.execute(query,params)
                rows = cur.fetchall()
                row_count = len(rows)
                query_list = []
                for row in rows:
                    query_list.append(dict(row))

      
    finally:
        conn.close()
    return query_list, row_count

    
    

def build_query_parser()-> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    
    subparser = p.add_subparsers(dest="command", help="Available subcommands")
    create_parser = subparser.add_parser("query", help="Query command")
    create_parser.add_argument("--variant", type= str, required= True)
    create_parser.add_argument("--limit", type= int, default = 25)
    create_parser.add_argument("--verbose", action="store_true" )
    create_parser.add_argument("--significance", type= str, default= "all")
    create_parser.add_argument("--disease", type=str, default= "all")
    
    return p
    
    

def main(argv=None):
    
    parser = build_query_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    if args.command != "query":
        parser.print_help()
        sys.exit(2)
    if args.limit < 1:
        print(f"Invalid limit size", file=sys.stderr)
        sys.exit(2)
    

    try:
        rows, rows_count = query_choices(args.variant, args.limit, args.significance, args.disease)
        if rows_count == 0:
            print("No rows found.")
            sys.exit(2)
        
        
        for r in rows:
            print(r)
        print(f"Number of rows: {rows_count}")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)



if __name__ == "__main__":
    main()   