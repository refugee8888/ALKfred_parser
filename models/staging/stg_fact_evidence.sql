select *
from {{ source('alkfred', 'fact_evidence') }}
