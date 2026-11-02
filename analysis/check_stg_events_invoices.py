import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

print("EVENTS")
print("Rows:", con.execute("select count(*) from main.stg_subscription_events").fetchone()[0])
print(con.execute(
    "select event_type, count(*) as n from main.stg_subscription_events group by 1 order by 2 desc"
).df().to_string(index=False))
print("new_mrr missing:", con.execute(
    "select count(*) from main.stg_subscription_events where new_mrr_missing").fetchone()[0])

print()
print("INVOICES")
print("Rows:", con.execute("select count(*) from main.stg_invoices").fetchone()[0])
print(con.execute(
    "select status, count(*) as n from main.stg_invoices group by 1 order by 2 desc"
).df().to_string(index=False))
print(con.execute(
    "select billing_cycle, count(*) as n from main.stg_invoices group by 1 order by 2 desc"
).df().to_string(index=False))
print("Total cash (paid rows):", int(con.execute(
    "select sum(cash_amount) from main.stg_invoices").fetchone()[0]))
con.close()