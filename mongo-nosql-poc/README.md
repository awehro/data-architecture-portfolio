# MongoDB NoSQL PoC --- Event Store + Read Model

## Overview

This repository is a focused NoSQL portfolio component demonstrating:

-   Event Store modeling (append-only events)
-   Read Model projection for query-optimized access (CQRS-style)
-   Indexing for idempotency and replay
-   Controlled use of TTL (only on ephemeral data)
-   Minimal but real Python scripts (seed, project, query)

The goal is architectural clarity and explainability --- not production
hardening.

See also: - docs/architecture.md - docs/adr-0001-modeling-decisions.md -
docs/runbook.md

------------------------------------------------------------------------

## Architecture (Short Overview)

Write operations append immutable domain events to an Event Store. A
projection step derives a query-optimized Read Model from those events.

seed_events.py -\> events (append-only) -\> project_read_model.py -\>
orders_read -\> query_read_model.py

This demonstrates a simplified CQRS-style separation without additional
infrastructure.

------------------------------------------------------------------------

## How to Run (Local)

### 1) Prepare environment

Copy configuration:

    cp .env.example .env

Adjust values if needed.

### 2) Start MongoDB

    docker compose up -d

Mongo Express UI:

    http://localhost:8081

### 3) Seed events (Python)

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python scripts/seed_events.py

Re-running the script is safe (idempotent) because `eventId` is unique.

### 4) Build / Rebuild Read Model

    python scripts/project_read_model.py

### 5) Query Read Model

    python scripts/query_read_model.py

------------------------------------------------------------------------

## Data Model (MongoDB)

### Collections

-   `events` --- Event Store (append-only, source of truth)
-   `orders_read` --- Read Model / Projection (optimized for queries)
-   `events_debug` --- Ephemeral demo collection (TTL)

------------------------------------------------------------------------

## Event Store: `events` Document Schema

Each domain event is stored as one document (append-only).

### Required fields

-   `eventId` (string): globally unique event identifier (idempotency /
    dedup)
-   `aggregateType` (string): e.g. `order`
-   `aggregateId` (string): business identifier of the aggregate,
    e.g. `ORD-100045`
-   `eventType` (string): e.g. `OrderCreated`, `OrderPaid`
-   `eventVersion` (int): schema evolution for a given `eventType`
-   `occurredAt` (date): business time (when it happened)
-   `recordedAt` (date): system time (when it was written)
-   `payload` (object): event-specific data (varies per event type)
-   `metadata` (object): tracing/operational context (producer,
    correlation/causation)

### Example

{ "eventId": "01J...ULID", "aggregateType": "order", "aggregateId":
"ORD-100045", "eventType": "OrderCreated", "eventVersion": 1,
"occurredAt": "2026-01-28T17:30:00.000Z", "recordedAt":
"2026-01-28T17:30:01.234Z", "payload": { "customerId": "C-9001",
"items": \[ { "sku": "SKU-1", "qty": 2, "unitPrice": 12.5 } \],
"currency": "EUR" }, "metadata": { "producer": "seed_events.py",
"correlationId": "CORR-123", "causationId": null } }

------------------------------------------------------------------------

## Modeling Decisions (Why This Shape?)

-   Idempotency: `eventId` is unique so producers/consumers can retry
    without duplicating events.
-   Replayability: `{ aggregateType, aggregateId, occurredAt }` supports
    fast rebuild per aggregate.
-   Schema evolution: `eventType` + `eventVersion` allows controlled
    payload changes over time.
-   Audit & backfills: separating `occurredAt` (business time) from
    `recordedAt` (system time) makes late events explainable.
-   Clean separation: domain data stays in `payload`; operational
    context stays in `metadata`.

------------------------------------------------------------------------

## Indexes (Event Store)

-   Unique index: `{ eventId: 1 }`
-   Replay / ordering index:
    `{ aggregateType: 1, aggregateId: 1, occurredAt: 1 }`

------------------------------------------------------------------------

## Note on TTL

TTL indexes are intentionally NOT applied to the event store because
deleting events breaks auditability and replay capability.

TTL is demonstrated only on explicitly ephemeral collections
(e.g. `events_debug`).

------------------------------------------------------------------------

## Intentional Trade-offs

This PoC focuses on clarity and explainability. It intentionally
excludes:

-   Real-time streaming projector
-   Schema validation enforcement
-   Horizontal scaling considerations
-   Production-grade security hardening

The emphasis is on modeling, separation of concerns, and architectural
reasoning.

