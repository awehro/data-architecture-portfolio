# Data Architecture Portfolio

A structured collection of focused architecture components demonstrating
different data system design patterns.

The goal is not feature depth — but architectural clarity, modeling decisions,
and explainable trade-offs.

---

## How the Components Connect

​```
┌─────────────────────────────────────────────────────────────────┐
│  terraform-data-platform-skeleton                               │
│  Infrastructure layer: storage, compute, network                │
│  Hosts everything below                                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼───────┐             ┌───────▼───────┐
│ mini-lakehouse│             │ mongo-nosql   │
│ -kafka        │             │ -poc          │
│               │             │               │
│ Kafka →       │             │ Event Store → │
│ Bronze →      │             │ Read Model    │
│ Silver →      │             │ (CQRS-style)  │
│ DuckDB        │             │               │
└───────┬───────┘             └───────┬───────┘
        │                             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  data-lineage-design        │
        │  Observability layer:       │
        │  traces field-level         │
        │  transformations across     │
        │  both pipelines             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  metadata-schema-evolution  │
        │  (coming next)              │
        │  Schema versioning,         │
        │  evolution strategies,      │
        │  governance patterns        │
        └─────────────────────────────┘
​```

---

## Components

### 1. Streaming & Lakehouse Architecture
**Folder:** `mini-lakehouse-kafka`

- Event ingestion via Kafka (`events-orders` topic)
- Spark Structured Streaming → Bronze Parquet layer
- Bronze → Silver: deduplication on `event_id`, timestamp typing
- DuckDB query layer over Silver Parquet
- ADRs: local Kafka setup, Spark streaming to Bronze

Focus: Streaming pipelines and layered data architecture.

---

### 2. NoSQL Event Modeling Component
**Folder:** `mongo-nosql-poc`

- Append-only Event Store (`poc.events`)
- Read Model projection via MongoDB aggregation + `$merge` (`poc.orders_read`)
- Idempotent writes via unique index on `eventId`
- `status` field derived from `eventType` via conditional mapping
- ADR: modeling decisions and trade-offs

Focus: Document database modeling and read/write separation (CQRS-style).

---

### 3. Infrastructure as Code — Data Platform Skeleton
**Folder:** `terraform-data-platform-skeleton`

- Modular Terraform: network / storage / compute separation
- Environment layering: dev (`retention_days=7`, `small`) vs prod
- Input/output contracts: `variables.tf` and `outputs.tf` per module
- Remote state strategy: S3 + DynamoDB or Azure Blob (ADR-001)

Focus: Infrastructure as Code design patterns for a minimal data platform.

---

### 4. Conceptual Data Lineage Design
**Folder:** `data-lineage-design`

- End-to-end lineage: Kafka → Bronze → Silver → DuckDB + Event Store → Read Model
- Column-level mappings using real field names from the codebase
- `status` derivation in `poc.orders_read` as the primary column-level example
- Terraform storage retention as a lineage boundary condition
- Documented limitations: no Gold layer, batch-only Read Model, pipelines not connected end-to-end

Focus: Data observability and explainability across the full pipeline.

---

### 5. Metadata & Schema Evolution Strategy
**Folder:** `metadata-schema-evolution` *(coming next)*

- Schema versioning patterns for Kafka events and MongoDB documents
- Evolution strategies: backward/forward compatibility
- `eventVersion` field usage already present in `poc.events`
- Impact of schema changes on downstream lineage

Focus: Governance and long-term maintainability of data contracts.

---

## Architectural Themes Across All Components

- Separation of concerns (write vs read, ingest vs transform vs serve)
- Explicit trade-off documentation via Architecture Decision Records
- Modular, independently understandable components
- Infrastructure as Code for reproducibility
- Data lineage and observability as first-class concerns
- Schema awareness and evolution planning

---

*Designed to show architectural reasoning rather than production hardening.*