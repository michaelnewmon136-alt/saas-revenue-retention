import duckdb, json

con = duckdb.connect("warehouse.duckdb", read_only=True)
out = {}
out["bridge"] = con.execute("""
    select cast(month_start as varchar) m, opening_mrr, new_mrr, expansion_mrr,
           reactivation_mrr, contraction_mrr, churn_mrr, closing_mrr, arr
    from main.fct_mrr_movements order by 1""").df().to_dict("records")
out["retention"] = con.execute("""
    select cast(month_start as varchar) m, nrr_ttm, grr_ttm, customer_churn_ttm
    from main.mart_revenue_retention order by 1""").df().to_dict("records")
out["health_flags"] = con.execute("""
    select risk_flag, count(*) accounts, sum(mrr) mrr
    from main.mart_customer_health group by 1""").df().to_dict("records")
out["segments"] = con.execute("""
    select segment, count(*) accounts, sum(mrr) mrr
    from main.mart_customer_health group by 1""").df().to_dict("records")
con.close()
json.dump(out, open("dashboard/data.json", "w"), default=float)
print("Saved dashboard/data.json |", {k: len(v) for k, v in out.items()})