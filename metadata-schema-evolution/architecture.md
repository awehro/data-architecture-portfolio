# Metadata & Schema Evolution Strategy

**Portfolio Component:** 5 of 5  
**Depends on:** `mini-lakehouse-kafka` · `mongo-nosql-poc` · `data-lineage-design`

---

## What This Document Is

Every data platform eventually faces the same problem: the world changes,
and the data contracts that described it yesterday no longer match today.

A new field gets added to an order event. A status value is renamed.
A payload structure is reorganized. Without a deliberate schema evolution
strategy, these changes silently break downstream consumers, corrupt lineage
traces, or — worse — pass through undetected and produce wrong results.

This document defines the evolution strategy for the three layers where
schema changes happen in this portfolio's pipeline:

1. **Kafka events** — the entry point, where schema changes originate
2. **MongoDB documents** — the event store, where history is preserved
3. **Spark transformations** — the processing layer, where schema is enforced

All references to field names, scripts, and configurations correspond
to the actual code in this repository.

---

## Where Schema Changes Enter the System

```
[produce_orders.py]          ← schema change starts here (new field, renamed value)
        │
        ▼
[Kafka: events-orders]       ← topic carries old and new schema simultaneously
        │
        ▼
[spark_streaming_kafka_to_parquet.py]
        │
        │  ← StructType schema defined here — first hard breakpoint
        ▼
[Bronze: data/bronze/events_orders/]
        │
        ▼
[spark_bronze_to_silver_orders.py]
        │
        │  ← column selection and type casting — second breakpoint
        ▼
[Silver: data/silver/orders/]
        │
        ▼
[warehouse_query_duckdb.py]  ← SQL queries — third breakpoint

[seed_events.py]             ← MongoDB schema change starts here
        │
        ▼
[poc.events]                 ← eventVersion field is the evolution handle
        │
        ▼
[project_read_model.py]      ← $switch on eventType — fourth breakpoint
        │
        ▼
[poc.orders_read]            ← read model reflects aggregated state
```

---

## The Four Breakpoints — Where Evolution Breaks Things

These are the exact locations in the codebase where an unmanaged schema
change causes a failure or silent data corruption.

### Breakpoint 1: Spark StructType (Kafka → Bronze)

**File:** `spark_streaming_kafka_to_parquet.py`

```python
schema = StructType([
    StructField("event_id",    StringType(),  True),
    StructField("event_time",  StringType(),  True),
    StructField("order_id",    StringType(),  True),
    StructField("customer_id", StringType(),  True),
    StructField("amount",      DoubleType(),  True),
    StructField("currency",    StringType(),  True),
    StructField("status",      StringType(),  True),
    StructField("source",      StringType(),  True),
    StructField("seq",         LongType(),    True),
])
```

**What breaks:** If the producer adds a new field (e.g. `discount_pct`),
it is silently dropped — the schema does not include it. If a field is
renamed (e.g. `amount` → `gross_amount`), the old column arrives as `null`
in Bronze. Neither case raises an error; both corrupt downstream data silently.

---

### Breakpoint 2: Silver Column Selection (Bronze → Silver)

**File:** `spark_bronze_to_silver_orders.py`

```python
.select(
    "event_id", "event_time_ts", "ingest_time_ts",
    "order_id", "customer_id",
    col("amount").cast("double").alias("amount"),
    "currency", "status", "source", "seq",
    col("key").alias("kafka_key"),
    "topic", "partition", "offset",
)
```

**What breaks:** If Bronze gains a new column (because the schema was updated),
Silver does not automatically include it. New fields are explicitly excluded
by the `.select()`. This is intentional for data quality control — but it
means Silver must be updated deliberately when new fields are promoted.

---

### Breakpoint 3: DuckDB Queries (Silver → Query Layer)

**File:** `warehouse_query_duckdb.py`

```sql
SELECT order_id, max(amount) AS max_amount, count(*) AS events
FROM silver_orders GROUP BY order_id ORDER BY max_amount DESC

SELECT status, sum(amount) AS revenue, count(*) AS events
FROM silver_orders GROUP BY status ORDER BY revenue DESC
```

**What breaks:** If `amount` is renamed or split into `amount_gross` /
`amount_net`, both queries silently return wrong results or fail.
The `status` GROUP BY would produce unexpected groups if new status
values are introduced without updating the query.

---

### Breakpoint 4: MongoDB $switch on eventType (Event Store → Read Model)

**File:** `project_read_model.py`

```python
"$switch": {
    "branches": [
        {"case": {"$eq": ["$lastEventType", "OrderCreated"]},   "then": "CREATED"},
        {"case": {"$eq": ["$lastEventType", "OrderPaid"]},      "then": "PAID"},
        {"case": {"$eq": ["$lastEventType", "OrderShipped"]},   "then": "SHIPPED"},
        {"case": {"$eq": ["$lastEventType", "OrderCancelled"]}, "then": "CANCELLED"},
    ],
    "default": "UNKNOWN",
}
```

**What breaks:** Any new `eventType` (e.g. `OrderReturned`, `OrderRefunded`)
maps silently to `"UNKNOWN"` in the Read Model. The order appears to have
no meaningful status, even though the event was recorded correctly.
This is already the documented Limitation 5 in `data-lineage-design/architecture.md`.

---

## Versioning Approach

### Kafka Events: Version Field in Payload

The producer embeds a version in every event. This already exists as a
convention in the MongoDB event model (`eventVersion`) and should be
applied to Kafka events as well:

```python
# produce_orders.py — proposed addition
def make_event(i: int) -> dict:
    return {
        "event_id":      str(uuid.uuid4()),
        "event_version": 1,          # ← add this field
        "event_time":    now_iso(),
        "order_id":      ...,
        "customer_id":   ...,
        "amount":        ...,
        "currency":      "EUR",
        "status":        ...,
        "source":        ...,
        "seq":           i,
    }
```

**Rule:** `event_version` increments only when the payload structure changes
in a backward-incompatible way. Adding a new optional field is not a version
increment. Renaming or removing a field is.

---

### MongoDB Events: eventVersion Already Present

**File:** `seed_events.py`

```python
{
    "eventId":       "py-evt-001",
    "aggregateType": "order",
    "aggregateId":   "ORD-2001",
    "eventType":     "OrderCreated",
    "eventVersion":  1,              # ← already exists
    ...
}
```

The `eventVersion` field is already part of the event schema. The strategy
is to use it consistently: every event handler and projection must be
aware of the version it was written to handle.

---

### Spark Schema: Explicit Version-Aware StructType

Rather than one monolithic schema, maintain a schema per version:

```python
# spark_streaming_kafka_to_parquet.py — proposed pattern
SCHEMAS = {
    1: StructType([
        StructField("event_id",      StringType(), True),
        StructField("event_version", LongType(),   True),
        StructField("event_time",    StringType(), True),
        StructField("order_id",      StringType(), True),
        StructField("customer_id",   StringType(), True),
        StructField("amount",        DoubleType(), True),
        StructField("currency",      StringType(), True),
        StructField("status",        StringType(), True),
        StructField("source",        StringType(), True),
        StructField("seq",           LongType(),   True),
    ]),
    # 2: StructType([...]) when needed
}
```

The streaming job reads `event_version` first and selects the schema accordingly.
Unknown versions are routed to a dead-letter partition in Bronze for inspection.

---

## Backward Compatibility Rules

These rules define what is safe to change and what requires a version bump.

### Safe Changes (No Version Increment)

| Change | Reason Safe |
|---|---|
| Add a new optional field with a default | Consumers that don't know the field ignore it |
| Add a new `eventType` to MongoDB | Existing projections handle it via `default: "UNKNOWN"` until updated |
| Add a new `status` value in Kafka producer | Downstream queries that GROUP BY status will show a new group |
| Extend enum values (new `source` option) | String field — no type break |

### Breaking Changes (Version Increment Required)

| Change | Why It Breaks |
|---|---|
| Rename a field (`amount` → `gross_amount`) | Old consumers read `null` |
| Remove a field | Downstream selects and queries fail or return `null` |
| Change a field type (`amount`: Double → String) | Type cast in Silver fails or coerces incorrectly |
| Rename an `eventType` | The `$switch` mapping no longer matches; all affected orders → `"UNKNOWN"` |
| Change `aggregateId` format | All replay and grouping logic breaks |

---

## Migration Approach

### Strategy: Dual-Write During Transition

When a breaking change is needed, the safest pattern is dual-write:

```
Phase 1 — Introduce v2 alongside v1:
  Producer writes both event_version=1 and event_version=2 events
  (or: new field is added as optional alongside the old field)
  Consumers handle both versions

Phase 2 — Migrate consumers:
  Spark StructType updated for v2
  MongoDB $switch updated for new eventType
  DuckDB queries updated for new field names
  All consumers verified

Phase 3 — Retire v1:
  Producer stops writing v1 events
  Old schema definition archived but not deleted
  Bronze retains historical v1 data under its original schema
```

This approach ensures no data loss and no pipeline downtime during migration.

---

### Bronze as the Schema Archive

Bronze is append-only and schema-on-write. This has a direct consequence
for evolution: **old Bronze partitions retain their original schema forever**.

A Bronze partition written with `event_version=1` will always contain the
`amount` field. If v2 renames it to `gross_amount`, both field names exist
in Bronze — in different partitions. Silver must handle this explicitly:

```python
# spark_bronze_to_silver_orders.py — proposed evolution handling
from pyspark.sql.functions import coalesce

silver = bronze.withColumn(
    "amount",
    coalesce(col("gross_amount"), col("amount"))  # handle both v1 and v2
)
```

This makes Silver the normalization boundary — the layer that absorbs
backward compatibility complexity so Gold and Read Model consumers
do not have to.

---

### MongoDB: Projection Versioning

When a new `eventType` is introduced (e.g. `OrderReturned`),
the projection script must be updated before the new event type
appears in production:

```python
# project_read_model.py — after adding OrderReturned
"$switch": {
    "branches": [
        {"case": {"$eq": ["$lastEventType", "OrderCreated"]},   "then": "CREATED"},
        {"case": {"$eq": ["$lastEventType", "OrderPaid"]},      "then": "PAID"},
        {"case": {"$eq": ["$lastEventType", "OrderShipped"]},   "then": "SHIPPED"},
        {"case": {"$eq": ["$lastEventType", "OrderCancelled"]}, "then": "CANCELLED"},
        {"case": {"$eq": ["$lastEventType", "OrderReturned"]},  "then": "RETURNED"},  # ← new
    ],
    "default": "UNKNOWN",
}
```

The rule: projection updates must be deployed before the new event type
is produced. If they are deployed after, a manual rebuild of `orders_read`
via `project_read_model.py` corrects the `"UNKNOWN"` values retroactively —
this is the replayability guarantee of the append-only event store.

---

## How eventVersion Connects the Three Layers

```
Kafka event produced with event_version=1
         │
         ▼
Spark reads with SCHEMAS[event_version]  ←  schema lookup by version
         │
         ▼
Bronze stores event_version as a column  ←  version preserved in storage
         │
         ▼
Silver normalizes across versions        ←  coalesce handles renamed fields
         │
         ▼
MongoDB event stored with eventVersion=1 ←  same version concept, same value
         │
         ▼
Projection handles known eventTypes      ←  version-aware switch statement
```

The `event_version` / `eventVersion` field is the thread that connects
schema evolution awareness across all three layers. It makes the version
explicit in the data itself — not just in the code.

---

## Limitations

### 1. No Schema Registry
This portfolio does not use a Schema Registry (e.g. Confluent Schema Registry
with Avro or Protobuf). The versioning strategy described here is
**convention-based**: it relies on producer discipline and consumer awareness.
A Schema Registry would enforce compatibility rules automatically and block
incompatible schema changes at publish time.

### 2. Bronze Partitions Are Not Re-Schemed
Historical Bronze data retains its original schema. There is no
mechanism to retroactively apply a new schema to old partitions.
The `coalesce` pattern in Silver absorbs this, but it requires
explicit maintenance as more versions accumulate.

### 3. MongoDB Has No Schema Enforcement by Default
MongoDB is schemaless. The `eventVersion` field is a convention,
not enforced by the database. A producer that writes an event without
`eventVersion` is valid from MongoDB's perspective. Schema validation
rules (JSON Schema in MongoDB) would harden this, but are intentionally
out of scope here.

### 4. Dual-Write Increases Complexity
The migration pattern requires producers to write two event formats
simultaneously. For a single-team, single-producer setup this is manageable.
For multiple producers (microservices), coordinating dual-write phases
across teams adds significant operational complexity.
