import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

print("USAGE")
print("Rows:", con.execute("select count(*) from main.stg_product_usage").fetchone()[0])
print("Logins missing:", con.execute(
    "select count(*) from main.stg_product_usage where logins_missing").fetchone()[0])

print()
print("TICKETS")
print("Rows:", con.execute("select count(*) from main.stg_support_tickets").fetchone()[0])
print(con.execute(
    "select priority, count(*) as n from main.stg_support_tickets group by 1 order by 2 desc"
).df().to_string(index=False))
print("Priority inferred:", con.execute(
    "select count(*) from main.stg_support_tickets where priority_was_inferred").fetchone()[0])
print("Escalated tickets:", con.execute(
    "select count(*) from main.stg_support_tickets where escalated").fetchone()[0])
con.close()