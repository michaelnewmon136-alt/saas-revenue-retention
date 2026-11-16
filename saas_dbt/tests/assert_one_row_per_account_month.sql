select account_id, month_start, count(*) as n
from {{ ref('int_subscription_months') }}
group by account_id, month_start
having count(*) > 1