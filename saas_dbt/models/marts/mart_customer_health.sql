with latest as (

    select max(month_start) as m from {{ ref('int_subscription_months') }}

),

current_accounts as (

    select s.account_id, s.segment, s.plan, s.mrr, s.tenure_months
    from {{ ref('int_subscription_months') }} s
    join latest l on s.month_start = l.m
    where s.mrr > 0

),

usage as (

    select
        u.account_id,
        avg(case when u.month_start > l.m - interval 3 month then u.logins end) as avg_logins_last_3m,
        avg(case when u.month_start <= l.m - interval 3 month
                  and u.month_start > l.m - interval 6 month then u.logins end) as avg_logins_prior_3m
    from {{ ref('stg_product_usage') }} u
    cross join latest l
    group by u.account_id

),

tickets as (

    select
        t.account_id,
        count(*) as tickets_last_3m,
        sum(case when t.escalated then 1 else 0 end) as escalated_last_3m
    from {{ ref('stg_support_tickets') }} t
    cross join latest l
    where t.created_date > l.m - interval 3 month
    group by t.account_id

),

combined as (

    select
        c.account_id,
        c.segment,
        c.plan,
        c.mrr,
        c.tenure_months,
        c.mrr * 1.0 / sum(c.mrr) over () as revenue_share,
        u.avg_logins_last_3m,
        u.avg_logins_prior_3m,
        u.avg_logins_last_3m / nullif(u.avg_logins_prior_3m, 0) as usage_change,
        coalesce(t.tickets_last_3m, 0) as tickets_last_3m,
        coalesce(t.escalated_last_3m, 0) as escalated_last_3m
    from current_accounts c
    left join usage u using (account_id)
    left join tickets t using (account_id)

)

select
    *,
    case
        when usage_change < 0.70 or escalated_last_3m > 0 then 'high'
        when usage_change < 0.90 then 'watch'
        else 'ok'
    end as risk_flag
from combined