
      -- back compat for old kwarg name
  
  
        
            
                
                
            
                
                
            
        
    

    

    merge into "alkfred"."public"."bridge_evidence_variant" as DBT_INTERNAL_DEST
        using "bridge_evidence_variant__dbt_tmp100316869509" as DBT_INTERNAL_SOURCE
        on (
                    DBT_INTERNAL_SOURCE.eid = DBT_INTERNAL_DEST.eid
                ) and (
                    DBT_INTERNAL_SOURCE.variant_sk = DBT_INTERNAL_DEST.variant_sk
                )

    
    when matched then update set
        "eid" = DBT_INTERNAL_SOURCE."eid","variant_sk" = DBT_INTERNAL_SOURCE."variant_sk","ingestion_run_id" = DBT_INTERNAL_SOURCE."ingestion_run_id","ingested_at_utc" = DBT_INTERNAL_SOURCE."ingested_at_utc"
    

    when not matched then insert
        ("eid", "variant_sk", "ingestion_run_id", "ingested_at_utc")
    values
        ("eid", "variant_sk", "ingestion_run_id", "ingested_at_utc")


  