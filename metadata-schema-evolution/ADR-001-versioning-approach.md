# ADR-001: Convention-Based Schema Versioning Without Schema Registry

**Status:** Accepted  
**Date:** 2026-03-12  
**Context:** Metadata & Schema Evolution Strategy — Portfolio Component 5

---

## Context

Schema changes in a streaming-to-lakehouse pipeline can break downstream
consumers silently. A mechanism is needed to communicate schema versions
across Kafka, Spark, and MongoDB without introducing a Schema Registry
as an additional infrastructure dependency.

---

## Decision

Use an explicit `event_version` / `eventVersion` integer field embedded
in every event payload. Increment it only for breaking changes.
Maintain version-indexed schemas in Spark (`SCHEMAS = {1: ..., 2: ...}`).

---

## Rationale

A Schema Registry (Confluent, AWS Glue, Karapace) is the production-grade
answer — but it introduces a new infrastructure component, serialization
format requirements (Avro/Protobuf), and operational overhead.

For a portfolio that demonstrates architectural reasoning over production
hardening, convention-based versioning achieves the same conceptual goal:
every schema change is explicit, traceable, and version-stamped in the data.

The `eventVersion` field is already present in `mongo-nosql-poc/scripts/seed_events.py`.
Extending this convention to Kafka events creates a consistent versioning
thread across all three layers.

---

## Consequences

**Positive:**
- No additional infrastructure required
- Version is visible in the data itself — lineage-friendly
- `eventVersion` already exists in MongoDB; Kafka alignment is a small addition
- Schema archive (old StructType definitions) serves as documentation

**Negative:**
- No automatic enforcement — relies on producer discipline
- Compatibility checking is manual, not automated
- Accumulation of version-handling logic in Silver over time

---

## Migration Trigger

A new version number is required when:
- A field is renamed or removed
- A field's type changes
- An `eventType` is renamed

A new version is NOT required when:
- A new optional field is added
- A new `eventType` is introduced (handled by extending the `$switch`)
- An enum value is extended (new `status` or `source` values)

---

## Related

- `architecture.md` — full evolution strategy with breakpoint analysis
- `../../mini-lakehouse-kafka/pipelines/spark_streaming_kafka_to_parquet.py` — Breakpoint 1
- `../../mongo-nosql-poc/scripts/project_read_model.py` — Breakpoint 4
- `../../data-lineage-design/architecture.md` — Limitation 5 (status gap)
