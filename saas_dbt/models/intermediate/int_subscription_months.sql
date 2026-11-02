with months as (

    select * from {{ ref('stg_subscription_months') }}

),

accounts as (

    select * from {{ ref('stg_accounts') }}

),

joined as (

    select
        m.account_id,
        m.month_start,
        m.plan,
        m.status,
        m.mrr,
        a.segment,
        a.industry,
        a.channel,
        a.signup_date
    from months m
    left join accounts a using (account_id)

),

with_history as (

    select
        *,
        date_diff('month', signup_date, month_start) as tenure_months,
        lag(mrr) over (partition by account_id order by month_start) as prev_mrr,
        max(mrr) over (
            partition by account_id
            order by month_start
            rows between unbounded preceding and 1 preceding
        ) as max_prior_mrr
    from joined

),

classified as (

    select
        *,
        case
            when prev_mrr is null and mrr > 0 then 'new'
            when prev_mrr = 0 and mrr > 0 and max_prior_mrr > 0 then 'reactivation'
            when prev_mrr > 0 and mrr = 0 then 'churn'
            when prev_mrr > 0 and mrr > prev_mrr then 'expansion'
            when prev_mrr > 0 and mrr > 0 and mrr < prev_mrr then 'contraction'
            else 'none'
        end as movement_type
    from with_history

)

select * from classified