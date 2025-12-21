
      -- back compat for old kwarg name
  
  
        
            
                
                
            
                
                
            
                
                
            
        
    

    

    merge into "alkfred"."public"."fact_evidence_assoc" as DBT_INTERNAL_DEST
        using "fact_evidence_assoc__dbt_tmp190054390237" as DBT_INTERNAL_SOURCE
        on (
                    DBT_INTERNAL_SOURCE.eid = DBT_INTERNAL_DEST.eid
                ) and (
                    DBT_INTERNAL_SOURCE.doid = DBT_INTERNAL_DEST.doid
                ) and (
                    DBT_INTERNAL_SOURCE.molecular_profile_id = DBT_INTERNAL_DEST.molecular_profile_id
                )

    
    when matched then update set
        "eid" = DBT_INTERNAL_SOURCE."eid","doid" = DBT_INTERNAL_SOURCE."doid","molecular_profile_id" = DBT_INTERNAL_SOURCE."molecular_profile_id","direction" = DBT_INTERNAL_SOURCE."direction","significance" = DBT_INTERNAL_SOURCE."significance","pub_year" = DBT_INTERNAL_SOURCE."pub_year","ingestion_run_id" = DBT_INTERNAL_SOURCE."ingestion_run_id","ingested_at_utc" = DBT_INTERNAL_SOURCE."ingested_at_utc"
    

    when not matched then insert
        ("eid", "doid", "molecular_profile_id", "direction", "significance", "pub_year", "ingestion_run_id", "ingested_at_utc")
    values
        ("eid", "doid", "molecular_profile_id", "direction", "significance", "pub_year", "ingestion_run_id", "ingested_at_utc")


  