# Architecture Overview — MongoDB NoSQL PoC

## Position within Portfolio

This repository represents a focused NoSQL architecture component
demonstrating:

- Event-based write modeling
- Read-optimized projections
- Explicit separation of write and read concerns (CQRS-style)
- Controlled use of MongoDB indexing and TTL

It is intentionally isolated from streaming or distributed systems
to highlight data modeling decisions clearly.

---

## High-Level Architecture

         +----------------------+
         |   seed_events.py     |
         |  (write operations)  |
         +----------+-----------+
                    |
                    v
           +------------------+
           |     events       |
           | (Event Store)    |
           |  append-only     |
           +------------------+
                    |
                    | aggregation + $merge
                    v
      +-----------------------------+
      |  project_read_model.py      |
      |  (projection / rebuild)     |
      +---------------+-------------+
                      |
                      v
            +-------------------+
            |   orders_read     |
            | (Read Model)      |
            +-------------------+
                      |
                      v
            +-------------------+
            | query_read_model  |
            +-------------------+

---

## Architectural Concepts Demonstrated

### 1. Append-only Event Store
- Immutable event history
- Idempotent writes via unique index on `eventId`
- Replay capability via compound index

### 2. Explicit Projection Layer
- Read model derived from events
- `$merge` used as a controlled materialization mechanism
- Rebuildable at any time

### 3. Read/Write Separation
- Write model optimized for audit & history
- Read model optimized for query patterns
- Indexes tailored per responsibility

### 4. Data Lifecycle Control
- TTL applied only to explicitly ephemeral collections
- Event store remains permanent for auditability

---

## Design Trade-offs (Intentional)

- No real-time projector (batch rebuild only)
- No schema validation enforcement
- No production-grade security hardening
- No distributed deployment

These trade-offs are accepted because the focus is on
clear modeling and explainability.

---

## How This Would Evolve in Production

- Add schema validation rules
- Introduce streaming-based projector (Kafka / change streams)
- Add monitoring and metrics
- Harden authentication & secret management
- Add migration/versioning strategy for event evolution

