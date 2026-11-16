import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

print(con.execute("""
    select table_name, table_type
    from information_schema.tables
    where table_schema = 'main'
      and (table_name like 'fct_%' or table_name like 'mart_%')
    order by 1
""").df().to_string(index=False))
print()
print("Final closing MRR:", int(con.execute(
    "select closing_mrr from main.fct_mrr_movements order by month_start desc limit 1").fetchone()[0]))
print("Bridge months not reconciling:", con.execute(
    "select count(*) from main.fct_mrr_movements where bridge_check <> 0").fetchone()[0])
con.close()