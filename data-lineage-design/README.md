# Data Lineage Design

**Type:** Conceptual Architecture Document  
**Status:** Complete  
**Related Projects:** [`mini-lakehouse-kafka`](../mini-lakehouse-kafka) · [`mongo-nosql-poc`](../mongo-nosql-poc)

---

## What This Is

A conceptual lineage design for the streaming-to-read-model pipeline demonstrated
across this portfolio. It does not introduce new infrastructure — instead, it adds
the **observability layer** that ties the existing components together:

```
[Kafka Topic]  →  [Spark]  →  [Bronze]  →  [Silver]  →  [Gold]  →  [Read Model]
                              ↑ mini-lakehouse-kafka ↑              ↑ mongo-nosql-poc ↑
```

## Contents

| File | Purpose |
|---|---|
| [`architecture.md`](./architecture.md) | Full lineage design — diagram, column mapping, limitations |
| [`lineage-diagram.mmd`](./lineage-diagram.mmd) | Standalone Mermaid diagram (renderable in GitHub) |
| [`docs/ADR-001-lineage-granularity.md`](./docs/ADR-001-lineage-granularity.md) | Decision: dataset-level first, column-level selective |

## Key Concepts Demonstrated

**Dataset-level lineage** — tracks which tables/topics feed which downstream assets.
The baseline for impact analysis and pipeline dependency mapping.

**Column-level lineage** — tracks how specific fields are derived, transformed, or
aggregated as data moves through the pipeline. Applied selectively to high-value columns.

**Lineage trust boundaries** — each layer (Bronze / Silver / Gold / Read Model) has
different trust guarantees. Lineage without trust context is incomplete.

**Documented limitations** — schema evolution risks, streaming offset instability,
manual transformation gaps, and eventual consistency. Honest trade-off documentation
is part of the architecture.

## Architectural Reasoning

Lineage is not just a compliance artifact — it's the architectural mechanism
that makes a data platform **explainable**. When a business metric looks wrong,
lineage answers: where did this number come from, and what was done to it?

This design deliberately separates the *concept* of lineage from specific tooling,
making the patterns applicable whether the implementation uses OpenLineage, DataHub,
dbt lineage, or a manually-maintained catalog.

---

*Part of the [Data Architecture Portfolio](../README.md)*
