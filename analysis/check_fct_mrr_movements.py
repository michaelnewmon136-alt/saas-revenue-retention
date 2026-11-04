import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

print("Rows (months):", con.execute("select count(*) from main.fct_mrr_movements").fetchone()[0])
print("Months where bridge_check is not 0:", con.execute(
    "select count(*) from main.fct_mrr_movements where bridge_check <> 0").fetchone()[0])
print()
print(con.execute("""
    select month_start, opening_mrr, new_mrr, expansion_mrr, reactivation_mrr,
           contraction_mrr, churn_mrr, closing_mrr, arr
    from main.fct_mrr_movements
    order by month_start desc
    limit 3
""").df().to_string(index=False))
con.close()