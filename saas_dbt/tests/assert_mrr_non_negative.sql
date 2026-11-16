select account_id, month_start, mrr
from {{ ref('int_subscription_months') }}
where mrr < 0