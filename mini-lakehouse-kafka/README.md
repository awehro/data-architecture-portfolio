# Mini Lakehouse – Kafka & Spark Structured Streaming PoC

## What this is
A small but realistic **end-to-end streaming data platform PoC** demonstrating how near-real-time events flow from Kafka through Spark Structured Streaming into a Lakehouse-style architecture (Bronze/Silver) and are queried via a lightweight warehouse layer (DuckDB).

The focus is **architecture, semantics, and operability**, not UI or cloud tooling.

---

## Architecture (logical)

```
Event Sources (Adapters)
        |
        v
+-----------------------+
| Kafka                 |
| Topic: events-orders  |
| - partitions          |
| - retention           |
+-----------+-----------+
            |
            v
+---------------------------------------+
| Spark Structured Streaming            |
|                                       |
| Bronze Layer (Parquet)                |
| - raw events                          |
| - at-least-once                       |
| - checkpointed                        |
|                                       |
| Silver Layer (Parquet)                |
| - watermark                           |
| - dedupe by event_id                  |
+-----------------------+---------------+
                        |
                        v
+-------------------------------+
| Warehouse / Serving           |
| DuckDB                        |
| - aggregations                |
| - ad-hoc queries              |
+-------------------------------+

```

---

## Repository Structure

```
adapters/    # Event sources (Kafka producers, later public APIs)
pipelines/   # Spark streaming jobs (Bronze / Silver)
warehouse/   # Analytics & serving (DuckDB queries)
docs/        # Runbook & Architecture Decision Records
docker/      # Local Kafka setup
```

This structure allows new sources (e.g. public energy price feeds) to be added by implementing **only a new adapter**, without changing downstream pipelines.

---

## Key Concepts Demonstrated

- Kafka topics, partitions, keys, retention
- Consumer groups & offset behavior
- Spark Structured Streaming
- Checkpointing & restart semantics
- At-least-once processing
- Watermark-based deduplication
- Bronze / Silver layering
- Warehouse-style analytical queries on Parquet

---

## Quick Start (Local Demo)

### 1. Start Kafka
```bash
docker compose -f docker/compose.yml up -d
```

### 2. Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install confluent-kafka duckdb pandas numpy
```

### 3. Produce demo events
```bash
source .venv/bin/activate
python adapters/produce_orders.py
```

### 4. Start Bronze streaming (Kafka → Parquet)
```bash
source .venv/bin/activate
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1 \
  pipelines/spark_streaming_kafka_to_parquet.py
```

Stop with **Ctrl+C**.

---

### 5. Start Silver streaming (Bronze → Silver, deduplication)
```bash
source .venv/bin/activate
spark-submit --driver-memory 2g pipelines/spark_bronze_to_silver_orders.py
```

Stop with **Ctrl+C**.

---

## Deduplication Demo

Send the same event twice (same `event_id`):

```bash
source .venv/bin/activate
python adapters/produce_duplicate_event.py
```

Verify in Silver layer:

```bash
source .venv/bin/activate
python3 - <<'PY'
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.master("local[*]").getOrCreate()
df = spark.read.parquet("data/silver/orders")
print("Count for DUPLICATE-DEMO-0001 =",
      df.where(col("event_id") == "DUPLICATE-DEMO-0001").count())
spark.stop()
PY
```

Expected result:
```
Count = 1
```

---

## Warehouse Queries (DuckDB)

Run analytical queries on top of the Silver layer:

```bash
source .venv/bin/activate
python3 warehouse/warehouse_query_duckdb.py
```

Example outputs:
- Total rows in Silver
- Top orders by amount
- Revenue by order status

---

## Design Decisions

Key architectural decisions are documented as **Architecture Decision Records (ADRs)** in `docs/adrs/`, including:
- Why Kafka + Spark Structured Streaming
- Why Bronze/Silver layering
- Why deduplication is implemented in the Silver layer

---

## Scope & Non-Goals

- Not a production system
- No UI, no orchestration framework
- Cloud services are intentionally omitted

The goal is to demonstrate **sound data architecture patterns**, not platform-specific tooling.

---

## Possible Extensions

- Add public event feeds (e.g. energy prices) via new adapters
- Add a Gold layer with business aggregates
- Deploy pipelines to managed Spark (e.g. Databricks)
- Replace DuckDB with Athena / BigQuery / Snowflake

