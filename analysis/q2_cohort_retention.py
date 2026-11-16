import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

df = con.execute("""
    with first_month as (
        select account_id, min(month_start) as first_paid
        from main.int_subscription_months
        where mrr > 0
        group by 1
    ),
    at_12 as (
        select f.account_id, f.first_paid,
               coalesce(m.mrr, 0) as mrr_12
        from first_month f
        left join main.int_subscription_months m
          on m.account_id = f.account_id
         and m.month_start = f.first_paid + interval 12 month
        where f.first_paid <= date '2024-12-01'
    )
    select
        year(a.first_paid) as cohort_year,
        s.segment,
        count(*) as accounts,
        sum(case when a.mrr_12 > 0 then 1 else 0 end) as still_paying_12m,
        round(sum(case when a.mrr_12 > 0 then 1 else 0 end) * 1.0 / count(*), 3) as logo_retention_12m
    from at_12 a
    join main.stg_accounts s using (account_id)
    group by 1, 2
    order by 1, 2
""").df()
con.close()
print(df.to_string(index=False))