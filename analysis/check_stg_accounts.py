import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

print("Rows:", con.execute("select count(*) from main.stg_accounts").fetchone()[0])
print("Distinct account_ids:",
      con.execute("select count(distinct account_id) from main.stg_accounts").fetchone()[0])
print()
print(con.execute(
    "select segment, count(*) as n from main.stg_accounts group by 1 order by 2 desc"
).df().to_string(index=False))
print()
print("Unknown industry:",
      con.execute("select count(*) from main.stg_accounts where industry = 'Unknown'").fetchone()[0])
print("NULL industry:",
      con.execute("select count(*) from main.stg_accounts where industry is null").fetchone()[0])
con.close()