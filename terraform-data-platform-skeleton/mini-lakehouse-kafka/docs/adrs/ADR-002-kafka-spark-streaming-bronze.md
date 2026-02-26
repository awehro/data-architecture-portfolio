# ADR-002: Kafka + Spark Structured Streaming to build Bronze Parquet layer

## Status
Accepted

## Context
This PoC demonstrates a credible near-real-time ingestion pattern:
Kafka receives order events, Spark consumes them as a stream and persists them to a Bronze layer.

Requirements:
- reproducible local setup
- ability to replay events for demos
- visible consumer group + offset behavior
- restart-safe streaming job (no full reprocessing on restart)

Out of scope:
- multi-broker HA, security hardening, schema registry, exactly-once end-to-end guarantees

## Decision
Use:
- Kafka (KRaft, single broker) as ingestion/event buffer
- Spark Structured Streaming to consume from Kafka
- Parquet files as Bronze storage sink
- Spark checkpointing to resume processing after restarts

Implementation notes:
- Spark reads from Kafka using `format("kafka")`
- A `checkpointLocation` is used to store progress (per-partition offsets + state)
- `startingOffsets=earliest` is used only for the first run; afterwards the checkpoint is authoritative

## Rationale
- Kafka decouples producers from downstream consumers and enables replay with retention.
- Spark Structured Streaming provides a simple, industry-standard way to process Kafka topics with recoverability.
- Parquet is a lightweight, widely supported columnar format suitable for Bronze/raw layers.
- Checkpointing makes the job restart-safe and avoids reprocessing the entire topic on every restart.

## Alternatives considered
- Batch ingestion (periodic polling): simpler but not near-real-time and weak for restart/replay demos.
- Writing directly to a database from the producer: couples producer to storage and removes buffering/replay.
- Flink/Kafka Streams: strong options but higher setup complexity for this PoC’s scope.

## Consequences / Trade-offs
- Parquet sink provides durability but no built-in upserts/deduplication (handled in Silver/Gold).
- Single broker + PLAINTEXT is PoC-only (no HA/security).
- End-to-end exactly-once is not guaranteed; we rely on checkpointing and downstream idempotence patterns later.
- Duplicate events are expected in at-least-once pipelines; deduplication is implemented in the Silver layer using watermark + event_id.

