This is the desired architecture of the ALKfred pipeline.

[API_GraphiQL] -> [RAW_DATA] -> [staging_tables] -> [dim_tables] -> [bridge_table]
-> [fact_table] -> [marts] or/and [view_tables]


No foreign keys will be used in staging tables.