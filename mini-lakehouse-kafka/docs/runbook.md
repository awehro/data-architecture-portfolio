# Runbook — Local Kafka

## Start/Stop
- Start: `docker compose -f docker/compose.yml up -d`
- Stop:  `docker compose -f docker/compose.yml down`
- Full reset (destroys data): `docker compose -f docker/compose.yml down -v`

## Health checks
- `docker compose -f docker/compose.yml ps`
- `docker compose -f docker/compose.yml logs --tail 80 kafka`

## Create topic: events-orders
Run inside the container:
```bash
docker exec -it kafka bash

kafka-topics --bootstrap-server localhost:9092 \
  --create --topic events-orders \
  --partitions 3 --replication-factor 1 \
  --config retention.ms=86400000 \
  --config cleanup.policy=delete

exit
```
## Describe topic
```bash
docker exec -it kafka bash -lc "kafka-topics --bootstrap-server localhost:9092 --describe --topic events-orders"
```
## Verify topic configs
```bash
docker exec -it kafka bash -lc "kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name events-orders --describe"
```
## Python setup (producer/consumer)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install confluent-kafka
```
## Produce demo events
```bash
source .venv/bin/activate
python adapters/produce_orders.py
```
## Consume with default grup (continues from committed offsets)
```bash
source .venv/bin/activate
python consumer/consume_orders.py
```
## Consume with a NEW group (reads from earliest due to auto.offset.reset)
```bash
source .venv/bin/activate
GROUP_ID=demo-orders-consumer-v2 python consumer/consume_orders.py
```

## Spark streaming: Kafka -> Parquet (Bronze)
Start streaming job (includes Kafka connector package):
```bash
source .venv/bin/activate
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1 \
pipelines/spark_streaming_kafka_to_parquet.py

```
Stop the job:
Press Ctrl + C in the terminal running spark-submit

Notes:
- startingOffsets=earliest is only used on first start.
- With an existing checkpoint, Spark resumes from stored offsets.

## Architecture decisions
- ADR-002: Kafka + Spark Structured Streaming to build Bronze Parquet layer

## Silver streaming: Bronze -> Silver (dedupe by event_id)
Start Silver job:
```bash
source .venv/bin/activate
spark-submit --driver-memory 2g pipelines/spark_bronze_to_silver_orders.py
``` 

## Dedupe demo (send same event twice): 
```bash
source .venv/bin/activate
python adapters/produce_duplicate_event.py
```

## Verify in Silver (expected count = 1):
```bash
source .venv/bin/activate
python3 - <<'PY'
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
spark = SparkSession.builder.master("local[*]").getOrCreate()
df = spark.read.parquet("data/silver/orders")
print(df.where(col("event_id") == "DUPLICATE-DEMO-0001").count())
spark.stop()
PY
```

## Warehouse queries (DuckDB)
```bash
source .venv/bin/activate
python3 warehouse/warehouse_query_duckdb.py
```

