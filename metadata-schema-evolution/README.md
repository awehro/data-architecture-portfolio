# Metadata & Schema Evolution Strategy

**Portfolio Component:** 5 of 5  
**Type:** Conceptual Architecture Document  
**Status:** Complete

---

## What This Is

This is the final component of the portfolio. It addresses the question
that every data platform faces over time:

> *"What happens when the data contract changes — and how do we
> make sure nothing breaks silently?"*

The document identifies the exact breakpoints in the existing pipeline code
where schema changes cause failures or silent data corruption, and defines
a versioning and migration strategy to manage them.

---

## Connection to Other Components

This component closes the loop across the entire portfolio:

```
mini-lakehouse-kafka
  spark_streaming_kafka_to_parquet.py  ← Breakpoint 1: StructType
  spark_bronze_to_silver_orders.py     ← Breakpoint 2: .select()
  warehouse_query_duckdb.py            ← Breakpoint 3: SQL column names

mongo-nosql-poc
  project_read_model.py                ← Breakpoint 4: $switch on eventType
  seed_events.py                       ← eventVersion field already present

data-lineage-design
  architecture.md Limitation 5        ← the $switch gap is resolved here
```

---

## Contents

| File | Purpose |
|---|---|
| `architecture.md` | Full strategy: breakpoints, versioning rules, migration approach, limitations |
| `docs/ADR-001-versioning-approach.md` | Decision: convention-based versioning without Schema Registry |

---

## Key Concepts Demonstrated

**Breakpoint analysis** — identifying the exact code locations where
schema changes cause failures, rather than speaking about evolution abstractly.

**Backward vs breaking changes** — a clear rule set for what requires
a version increment and what does not.

**Dual-write migration pattern** — a phased approach to introduce breaking
changes without pipeline downtime or data loss.

**Bronze as schema archive** — append-only Bronze partitions retain their
original schema forever; Silver is the normalization boundary that absorbs
version complexity.

**eventVersion as the cross-layer thread** — the same versioning field
connects Kafka, Spark, and MongoDB into a coherent evolution strategy.

---

*Part of the [Data Architecture Portfolio](../README.md)*
