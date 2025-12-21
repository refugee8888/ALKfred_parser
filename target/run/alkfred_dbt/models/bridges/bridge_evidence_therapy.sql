
      -- back compat for old kwarg name
  
  
        
            
                
                
            
                
                
            
        
    

    

    merge into "alkfred"."public"."bridge_evidence_therapy" as DBT_INTERNAL_DEST
        using "bridge_evidence_therapy__dbt_tmp190054415404" as DBT_INTERNAL_SOURCE
        on (
                    DBT_INTERNAL_SOURCE.eid = DBT_INTERNAL_DEST.eid
                ) and (
                    DBT_INTERNAL_SOURCE.ncit_id = DBT_INTERNAL_DEST.ncit_id
                )

    
    when matched then update set
        "eid" = DBT_INTERNAL_SOURCE."eid","ncit_id" = DBT_INTERNAL_SOURCE."ncit_id","ingestion_run_id" = DBT_INTERNAL_SOURCE."ingestion_run_id","ingested_at_utc" = DBT_INTERNAL_SOURCE."ingested_at_utc"
    

    when not matched then insert
        ("eid", "ncit_id", "ingestion_run_id", "ingested_at_utc")
    values
        ("eid", "ncit_id", "ingestion_run_id", "ingested_at_utc")


  