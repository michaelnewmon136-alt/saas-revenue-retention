import duckdb
import pandas as pd

con = duckdb.connect("warehouse.duckdb", read_only=True)
key = pd.read_csv("analysis/answer_key_bridge.csv")

rows = con.execute("select count(*) from main.int_subscription_months").fetchone()[0]
dups = con.execute(
    "select count(*) from (select account_id, month_start from main.int_subscription_months "
    "group by 1, 2 having count(*) > 1)"
).fetchone()[0]
print("Rows:", rows, "| account-months with more than one row:", dups)
print("Rows with no segment (failed join):", con.execute(
    "select count(*) from main.int_subscription_months where segment is null").fetchone()[0])

# Bridge by month, computed from the dbt model
bridge = con.execute("""
    select
        date_diff('month', date '2023-01-01', month_start) as month_idx,
        sum(case when movement_type = 'new'          then mrr else 0 end) as new,
        sum(case when movement_type = 'expansion'    then mrr - prev_mrr else 0 end) as expansion,
        sum(case when movement_type = 'reactivation' then mrr else 0 end) as reactivation,
        sum(case when movement_type = 'contraction'  then mrr - prev_mrr else 0 end) as contraction,
        sum(case when movement_type = 'churn'        then -prev_mrr else 0 end) as churn
    from main.int_subscription_months
    group by 1
    order by 1
""").df()
con.close()

bridge = bridge[bridge["month_idx"] >= 1]
cmp = key.merge(bridge, on="month_idx", suffixes=("_key", "_dbt"))

print()
print("Months compared:", len(cmp))
for col in ["new", "expansion", "reactivation", "contraction", "churn"]:
    diff = (cmp[col + "_key"] - cmp[col + "_dbt"]).abs()
    print(f"{col:13s} months that differ: {int((diff != 0).sum())} | total key: {int(cmp[col + '_key'].sum())} | total dbt: {int(cmp[col + '_dbt'].sum())}")