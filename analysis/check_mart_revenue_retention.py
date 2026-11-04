import duckdb
import pandas as pd

con = duckdb.connect("warehouse.duckdb", read_only=True)

print("Rows (months):", con.execute("select count(*) from main.mart_revenue_retention").fetchone()[0])
print("GRR above 100% (must be 0):", con.execute(
    "select count(*) from main.mart_revenue_retention where grr_ttm > 1").fetchone()[0])
print("GRR above NRR (must be 0):", con.execute(
    "select count(*) from main.mart_revenue_retention where grr_ttm > nrr_ttm").fetchone()[0])
print()
print(con.execute("""
    select month_start, opening_customers, retained_customers,
           round(nrr_ttm, 3) as nrr_ttm, round(grr_ttm, 3) as grr_ttm,
           round(customer_churn_ttm, 3) as cust_churn_ttm
    from main.mart_revenue_retention
    order by month_start desc
    limit 6
""").df().to_string(index=False))

# Independent check of the last month with pandas on the truth table
truth = pd.read_csv("data_generator/truth_subscription_months.csv")
t = truth.pivot(index="account_id", columns="month_idx", values="mrr").reindex(columns=range(36)).fillna(0)
old, cur = t[23], t[35]
grp = old > 0
print()
print("Pandas check, month 35:  NRR =", round(cur[grp].sum() / old[grp].sum(), 3),
      "| GRR =", round(pd.concat([cur[grp], old[grp]], axis=1).min(axis=1).sum() / old[grp].sum(), 3))
con.close()