with health as (
    select sum(mrr) as health_mrr
    from {{ ref('mart_customer_health') }}
),
bridge as (
    select closing_mrr
    from {{ ref('fct_mrr_movements') }}
    order by month_start desc
    limit 1
)
select health.health_mrr, bridge.closing_mrr
from health cross join bridge
where health.health_mrr <> bridge.closing_mrr