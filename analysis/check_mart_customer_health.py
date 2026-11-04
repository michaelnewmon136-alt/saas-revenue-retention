import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

print("Rows (paying accounts):", con.execute("select count(*) from main.mart_customer_health").fetchone()[0])
print("Total MRR in table:", int(con.execute("select sum(mrr) from main.mart_customer_health").fetchone()[0]))
print("Revenue shares sum to:", round(con.execute("select sum(revenue_share) from main.mart_customer_health").fetchone()[0], 4))
print("Accounts with no usage data:", con.execute(
    "select count(*) from main.mart_customer_health where avg_logins_last_3m is null").fetchone()[0])
print()
print(con.execute(
    "select risk_flag, count(*) as accounts, sum(mrr) as mrr from main.mart_customer_health group by 1 order by 2 desc"
).df().to_string(index=False))
print()
print("Top 5 accounts by revenue share:")
print(con.execute(
    "select account_id, segment, plan, mrr, round(revenue_share, 4) as share "
    "from main.mart_customer_health order by mrr desc limit 5"
).df().to_string(index=False))
con.close()