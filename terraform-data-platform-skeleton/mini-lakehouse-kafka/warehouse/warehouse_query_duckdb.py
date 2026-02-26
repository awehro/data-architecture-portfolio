import duckdb

SILVER_PATH = "data/silver/orders/*.parquet"

con = duckdb.connect(database=":memory:")

con.execute(f"""
CREATE VIEW silver_orders AS
SELECT * FROM read_parquet('{SILVER_PATH}');
""")

print("Rows in silver_orders:", con.execute(
    "SELECT count(*) FROM silver_orders"
).fetchone()[0])

print("\nTop 10 orders by amount:")
print(con.execute("""
SELECT order_id, max(amount) AS max_amount, count(*) AS events
FROM silver_orders
GROUP BY order_id
ORDER BY max_amount DESC
LIMIT 10
""").fetchdf())

print("\nRevenue by status:")
print(con.execute("""
SELECT status, sum(amount) AS revenue, count(*) AS events
FROM silver_orders
GROUP BY status
ORDER BY revenue DESC
""").fetchdf())

