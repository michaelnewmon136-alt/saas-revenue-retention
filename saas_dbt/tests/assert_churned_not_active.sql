select account_id, month_start, status, mrr
from {{ ref('int_subscription_months') }}
where (status = 'cancelled' and mrr > 0)
   or (status = 'active' and mrr = 0)