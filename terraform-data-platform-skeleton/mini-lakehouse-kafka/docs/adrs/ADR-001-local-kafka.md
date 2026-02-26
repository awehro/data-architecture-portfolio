# ADR-001: Local Kafka setup for streaming PoC

## Status
Accepted

## Context
The goal of this project is to build a small but credible streaming Proof of Concept
that demonstrates Kafka fundamentals for data platform and lakehouse architectures.

The setup must be:
- reproducible on a local machine
- simple enough for demos and interviews
- realistic enough to discuss architectural trade-offs

High availability, security hardening and multi-cluster setups are explicitly out of scope.

## Decision
We run Apache Kafka locally using Docker Compose in KRaft mode (no ZooKeeper).

A single broker is used with a baseline topic:

- Topic name: `events-orders`
- Partitions: 3
- Replication factor: 1
- Cleanup policy: `delete`
- Retention: 1 day (86400000 ms)

## Rationale
- Docker Compose provides reproducibility and fast setup for local development.
- KRaft is the current Kafka standard and avoids ZooKeeper dependency.
- Multiple partitions allow demonstrating parallel consumption and consumer groups.
- A short retention period limits disk usage while still allowing short-term reprocessing.
- A single broker and replication factor are acceptable for a local PoC.

## Trade-offs
- No fault tolerance due to single broker setup.
- No security configuration (PLAINTEXT only).
- Retention is too short for long-term replay scenarios.

These limitations are accepted to keep the PoC focused and lightweight.

