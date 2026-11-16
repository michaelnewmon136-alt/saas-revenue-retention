import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

df = con.execute("""
    select
        year(month_start) as year,
        sum(new_mrr) as new_mrr,
        sum(expansion_mrr) as expansion_mrr,
        sum(reactivation_mrr) as reactivation_mrr,
        sum(contraction_mrr) as contraction_mrr,
        sum(churn_mrr) as churn_mrr
    from main.fct_mrr_movements
    where month_start >= date '2023-02-01'
    group by 1
    order by 1
""").df()
con.close()

df["gross_added"] = df["new_mrr"] + df["expansion_mrr"] + df["reactivation_mrr"]
df["gross_lost"] = df["contraction_mrr"] + df["churn_mrr"]
df["net_change"] = df["gross_added"] + df["gross_lost"]
df["new_share_of_added"] = (df["new_mrr"] / df["gross_added"]).round(3)
df["expansion_share_of_added"] = (df["expansion_mrr"] / df["gross_added"]).round(3)
df["lost_as_share_of_added"] = (-df["gross_lost"] / df["gross_added"]).round(3)

pd_opts = dict(index=False)
print(df.to_string(**pd_opts))