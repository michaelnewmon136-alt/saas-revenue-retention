import duckdb
import pandas as pd

con = duckdb.connect("warehouse.duckdb", read_only=True)
truth = pd.read_csv("data_generator/truth_subscription_months.csv")

n = con.execute("select count(*) from main.stg_subscription_months").fetchone()[0]
print("Rows in model:", n, "| rows in truth:", len(truth))

dups = con.execute(
    "select count(*) from (select account_id, month_start from main.stg_subscription_months "
    "group by 1, 2 having count(*) > 1)"
).fetchone()[0]
print("Account-months with more than one row:", dups)

print("NULL mrr:", con.execute(
    "select count(*) from main.stg_subscription_months where mrr is null").fetchone()[0])
print("Active rows with mrr = 0:", con.execute(
    "select count(*) from main.stg_subscription_months where status = 'active' and mrr = 0").fetchone()[0])
print("Cancelled rows with mrr > 0:", con.execute(
    "select count(*) from main.stg_subscription_months where status = 'cancelled' and mrr > 0").fetchone()[0])

# Compare MRR month by month against the truth
model = con.execute(
    "select cast(month_start as varchar) as month_start, sum(mrr) as model_mrr "
    "from main.stg_subscription_months group by 1"
).df()
truth_m = truth.groupby("month_start", as_index=False)["mrr"].sum().rename(columns={"mrr": "truth_mrr"})
cmp = model.merge(truth_m, on="month_start", how="outer").fillna(0)
cmp["diff"] = cmp["model_mrr"] - cmp["truth_mrr"]
print()
print("Months compared:", len(cmp))
print("Months where model MRR differs from truth:", int((cmp["diff"] != 0).sum()))
print("Total MRR, model:", int(cmp["model_mrr"].sum()), "| truth:", int(cmp["truth_mrr"].sum()))
print()
print("Last 3 months:")
print(cmp.sort_values("month_start").tail(3).to_string(index=False))
con.close()