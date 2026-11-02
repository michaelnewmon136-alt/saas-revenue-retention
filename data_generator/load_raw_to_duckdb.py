"""
Loads the seven messy raw CSV files into a DuckDB database.
All data is synthetic. Run from the project root folder.
"""
import duckdb

DB_PATH = "warehouse.duckdb"
TABLES = [
    "accounts",
    "subscriptions",
    "subscription_events",
    "subscription_months",
    "invoices",
    "product_usage",
    "support_tickets",
]

con = duckdb.connect(DB_PATH)
con.execute("CREATE SCHEMA IF NOT EXISTS raw")

for name in TABLES:
    con.execute(f"DROP TABLE IF EXISTS raw.{name}")
    con.execute(
        f"CREATE TABLE raw.{name} AS "
        f"SELECT * FROM read_csv_auto('data_generator/raw_{name}.csv')"
    )
    n = con.execute(f"SELECT COUNT(*) FROM raw.{name}").fetchone()[0]
    print(f"raw.{name}: {n} rows")

con.close()
print()
print("Done. Database file:", DB_PATH)