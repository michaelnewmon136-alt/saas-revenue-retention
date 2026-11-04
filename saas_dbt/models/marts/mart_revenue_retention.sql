with months as (

    select account_id, month_start, mrr
    from {{ ref('int_subscription_months') }}

),

pairs as (

    select
        cur.month_start,
        old.mrr as opening_mrr,
        cur.mrr as current_mrr
    from months cur
    join months old
        on old.account_id = cur.account_id
        and old.month_start = cur.month_start - interval 12 month
    where old.mrr > 0

)

select
    month_start,
    count(*) as opening_customers,
    sum(case when current_mrr > 0 then 1 else 0 end) as retained_customers,
    sum(opening_mrr) as opening_mrr,
    sum(current_mrr) as current_mrr_from_cohort,
    sum(least(current_mrr, opening_mrr)) as retained_mrr_no_expansion,
    sum(current_mrr) * 1.0 / sum(opening_mrr) as nrr_ttm,
    sum(least(current_mrr, opening_mrr)) * 1.0 / sum(opening_mrr) as grr_ttm,
    1 - sum(case when current_mrr > 0 then 1 else 0 end) * 1.0 / count(*) as customer_churn_ttm
from pairs
group by month_start
order by month_start