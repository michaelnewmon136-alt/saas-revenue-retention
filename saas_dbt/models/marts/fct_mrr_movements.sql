with movements as (

    select
        month_start,
        sum(mrr) as closing_mrr,
        sum(case when movement_type = 'new'          then mrr else 0 end) as new_mrr,
        sum(case when movement_type = 'expansion'    then mrr - prev_mrr else 0 end) as expansion_mrr,
        sum(case when movement_type = 'reactivation' then mrr else 0 end) as reactivation_mrr,
        sum(case when movement_type = 'contraction'  then mrr - prev_mrr else 0 end) as contraction_mrr,
        sum(case when movement_type = 'churn'        then -prev_mrr else 0 end) as churn_mrr
    from {{ ref('int_subscription_months') }}
    group by month_start

),

bridge as (

    select
        month_start,
        coalesce(lag(closing_mrr) over (order by month_start), 0) as opening_mrr,
        new_mrr,
        expansion_mrr,
        reactivation_mrr,
        contraction_mrr,
        churn_mrr,
        closing_mrr
    from movements

)

select
    *,
    closing_mrr * 12 as arr,
    opening_mrr + new_mrr + expansion_mrr + reactivation_mrr
        + contraction_mrr + churn_mrr - closing_mrr as bridge_check
from bridge
order by month_start