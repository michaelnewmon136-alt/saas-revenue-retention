import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

print("Rows:", con.execute("select count(*) from main.stg_subscriptions").fetchone()[0])
print("Distinct subscription_ids:",
      con.execute("select count(distinct subscription_id) from main.stg_subscriptions").fetchone()[0])
print()
print(con.execute(
    "select status, count(*) as n from main.stg_subscriptions group by 1 order by 2 desc"
).df().to_string(index=False))
print()
print("Ended with missing end date:", con.execute(
    "select count(*) from main.stg_subscriptions where end_date_missing").fetchone()[0])
print("Marked active but end date is earlier:", con.execute(
    "select count(*) from main.stg_subscriptions where active_but_ended_earlier").fetchone()[0])
con.close()