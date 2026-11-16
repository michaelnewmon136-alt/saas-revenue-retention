with int_total as (
    select sum(mrr) as total_mrr
    from {{ ref('int_subscription_months') }}
),
mart_total as (
    select sum(closing_mrr) as total_mrr
    from {{ ref('fct_mrr_movements') }}
)
select int_total.total_mrr as int_mrr, mart_total.total_mrr as mart_mrr
from int_total cross join mart_total
where int_total.total_mrr <> mart_total.total_mrr