This is the desired architecture of the ALKfred pipeline.

[API_GraphiQL] [RAW_DATA] -> [staging_tables] -> [dim_tables] -> [bridge_table]
-> [fact_table] -> [marts] or/and [view_tables]


No foreign keys will be used in staging tables.

Analytics will be handled by pandas until other databases than CivicDB or Bioportal will be ingested. Then we'll move to PySpark.
The end game: data storage, transformation, analytics and orchestration will be handled by Databricks which seems to be the popular choice for futurre ML/AI learniming integration.

