select subscription_id, status, end_date, end_date_missing
from {{ ref('stg_subscriptions') }}
where status = 'ended'
  and end_date is null
  and end_date_missing is not true