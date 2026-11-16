select month_start, bridge_check
from {{ ref('fct_mrr_movements') }}
where bridge_check <> 0