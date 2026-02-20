# ADR-0001: Event Store + Read Model in MongoDB

## Status
Accepted

## Context
This PoC is designed for interview and CV credibility, not production hardening.

The goal is to demonstrate:
- NoSQL data modeling skills
- Event-driven thinking
- Clear separation between write and read concerns
- Explainable trade-offs

MongoDB is used locally via Docker Compose.

## Decision
We store domain changes as immutable events in an **Event Store** (`events`)
and derive a query-optimized **Read Model** (`orders_read`) from those events.

The Event Store is append-only and acts as the source of truth.
The Read Model is rebuilt via aggregation pipelines and `$merge`.

## Rationale

### Why Event Store?
- Provides a complete audit trail of domain changes
- Enables replay and rebuild of derived views
- Makes temporal queries and debugging possible
- Forces explicit modeling of domain changes

### Why separate Read Model?
- Event data is inefficient for typical read queries
- Read access patterns differ from write patterns
- Allows indexes tailored for queries (status, customer, recency)
- Demonstrates CQRS-style separation without extra infrastructure

### Why MongoDB for this PoC?
- Flexible schema fits event payload evolution
- Aggregation pipelines support in-database projections
- `$merge` enables simple projector-style logic
- TTL indexes allow controlled demonstration of data lifecycle
- Easy local setup via Docker

### Why not use TTL on the Event Store?
- Deleting events breaks auditability and replay
- TTL is therefore demonstrated only on explicitly ephemeral collections
  (e.g. `events_debug`)

## Consequences

### Positive
- Clear, explainable architecture
- Simple local setup
- Easy to demonstrate aggregation and projections
- Interview-friendly design

### Negative / Trade-offs
- No strong schema enforcement (by design)
- No real-time projector (batch rebuild only)
- Not suitable for high-throughput production workloads

These trade-offs are accepted because the PoC focuses on clarity and explainability.

