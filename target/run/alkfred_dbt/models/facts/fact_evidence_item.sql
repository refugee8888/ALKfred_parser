
      -- back compat for old kwarg name
  
  
        
            
	    
	    
            
        
    

    

    merge into "alkfred"."public"."fact_evidence_item" as DBT_INTERNAL_DEST
        using "fact_evidence_item__dbt_tmp190054273669" as DBT_INTERNAL_SOURCE
        on ((DBT_INTERNAL_SOURCE.eid = DBT_INTERNAL_DEST.eid))

    
    when matched then update set
        "eid" = DBT_INTERNAL_SOURCE."eid","direction" = DBT_INTERNAL_SOURCE."direction","significance" = DBT_INTERNAL_SOURCE."significance","pub_year" = DBT_INTERNAL_SOURCE."pub_year","ingestion_run_id" = DBT_INTERNAL_SOURCE."ingestion_run_id","ingested_at_utc" = DBT_INTERNAL_SOURCE."ingested_at_utc"
    

    when not matched then insert
        ("eid", "direction", "significance", "pub_year", "ingestion_run_id", "ingested_at_utc")
    values
        ("eid", "direction", "significance", "pub_year", "ingestion_run_id", "ingested_at_utc")


  