import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

print("=== Q3: usage vs plan norm, by months before churn ===")
print("(ratio 1.0 = normal usage for that plan)")
print(con.execute("""
    with u as (
        select p.account_id, p.month_start, p.logins, s.plan
        from main.stg_product_usage p
        join main.int_subscription_months s
          on s.account_id = p.account_id and s.month_start = p.month_start
        where p.logins is not null
    ),
    plan_avg as (select plan, avg(logins) as avg_l from u group by 1),
    churn as (
        select account_id, month_start as churn_month
        from main.int_subscription_months where movement_type = 'churn'
    ),
    labeled as (
        select u.*, date_diff('month', u.month_start, c.churn_month) as months_before
        from u
        left join churn c
          on c.account_id = u.account_id
         and u.month_start < c.churn_month
         and u.month_start >= c.churn_month - interval 3 month
    )
    select
        coalesce(cast(months_before as varchar), 'not near churn') as months_before_churn,
        count(*) as account_months,
        round(avg(l.logins / a.avg_l), 3) as usage_ratio,
        round(avg(case when l.logins / a.avg_l < 0.7 then 1.0 else 0.0 end), 3) as share_below_70pct
    from labeled l
    join plan_avg a using (plan)
    group by 1
    order by 1
""").df().to_string(index=False))

print()
print("=== Q4: contraction and churn by the tier the account was LEAVING ===")
print(con.execute("""
    with x as (
        select account_id, month_start, mrr, prev_mrr, movement_type,
               lag(plan) over (partition by account_id order by month_start) as prev_plan
        from main.int_subscription_months
    )
    select
        prev_plan as tier,
        sum(case when movement_type = 'contraction' then 1 else 0 end) as downgrades,
        sum(case when movement_type = 'contraction' then prev_mrr - mrr else 0 end) as contraction_mrr,
        sum(case when movement_type = 'churn' then prev_mrr else 0 end) as churn_mrr,
        round(sum(case when movement_type = 'contraction' then prev_mrr - mrr else 0 end) * 1.0
              / sum(case when prev_mrr > 0 then prev_mrr else 0 end), 4) as contraction_rate
    from x
    where prev_plan is not null
    group by 1
    order by 3 desc
""").df().to_string(index=False))

print()
print("=== Q5: churn in the NEXT month after a ticket ===")
print(con.execute("""
    with t as (
        select ticket_id, account_id, escalated,
               date_trunc('month', created_date) as tm
        from main.stg_support_tickets
    ),
    ch as (
        select account_id, month_start as cm
        from main.int_subscription_months where movement_type = 'churn'
    )
    select
        t.escalated,
        count(*) as tickets,
        count(ch.cm) as churned_next_month,
        round(count(ch.cm) * 1.0 / count(*), 3) as churn_rate
    from t
    left join ch on ch.account_id = t.account_id and ch.cm = t.tm + interval 1 month
    group by 1
    order by 1
""").df().to_string(index=False))

base = con.execute("""
    select round(count(*) filter (where nxt = 'churn') * 1.0 / count(*), 3)
    from (
        select mrr, lead(movement_type) over (partition by account_id order by month_start) as nxt
        from main.int_subscription_months
    )
    where mrr > 0 and nxt is not null
""").fetchone()[0]
print("Baseline: share of all paying account-months followed by churn:", base)
con.close()