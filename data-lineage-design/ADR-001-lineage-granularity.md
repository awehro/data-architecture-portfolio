# ADR-001: Lineage Granularity — Dataset-Level First, Column-Level Selective

**Status:** Accepted  
**Date:** 2026-03-12  
**Deciders:** Data Architecture Team  
**Context:** Conceptual Data Lineage Design for streaming-to-read-model pipeline

---

## Context

When designing lineage for a streaming pipeline (Kafka → Spark → Lakehouse → Read Model),
two levels of granularity are possible: dataset-level and column-level.

Both provide value, but they differ significantly in implementation effort,
maintenance cost, and the problems they solve.

The question is: **where should we start, and how much lineage is enough?**

---

## Decision

We adopt a **dataset-level lineage baseline** as the foundation, with column-level
lineage applied **selectively** to fields that are:

1. Derived or transformed (not pass-throughs)
2. Used in downstream KPIs or business metrics
3. Subject to regulatory or compliance requirements

---

## Rationale

### Why Dataset-Level First

Dataset-level lineage (tracking table-to-table and topic-to-table dependencies)
delivers immediate value with low overhead:

- It can be documented in Markdown or a lightweight catalog
- It answers the most common question: "if I change X, what breaks?"
- It provides the dependency graph needed for orchestration and impact analysis
- It does not require schema change tracking or transformation metadata extraction

### Why Column-Level Selectively (Not Always)

Column-level lineage is significantly more expensive to produce and maintain:

- It requires either manual documentation or automated extraction from transformation code
- It breaks silently when transformations change (renamed fields, new derivation logic)
- Most data consumers and incident investigations do not need field-level precision
- Over-engineering lineage at field level for every column creates documentation
  debt that is worse than no lineage at all

### The Middle Ground

The approach is not binary. By identifying the 20% of columns that carry 80%
of the analytical risk (derived calculations, regulatory fields, KPIs), column-level
lineage can be applied precisely where it adds trust without drowning in maintenance.

---

## Consequences

**Positive:**
- Lineage is immediately usable and documented from day one
- Column-level investment is focused on high-value fields
- The team builds the habit of lineage thinking without tooling dependency
- Lineage can be incrementally enriched over time (start static, move to catalog)

**Negative:**
- Not all columns have traceable lineage — gaps are intentional but must be acknowledged
- Column-level documentation for selected fields requires discipline to keep current
- Without tooling, lineage may drift from the actual pipeline implementation

---

## Alternatives Considered

### Full Column-Level Lineage from Day One
**Rejected.** The maintenance burden outweighs the benefit at this stage.
Most fields in the pipeline are pass-throughs where column-level adds no
extra insight beyond dataset-level.

### Lineage Tooling Only (e.g., OpenLineage / DataHub)
**Deferred.** Tooling is the right long-term answer but introduces platform
dependencies that are out of scope for a conceptual design portfolio.
The patterns established here would translate directly into tool configuration.

### No Formal Lineage
**Rejected.** Lineage is a first-class architectural concern, not a reporting
afterthought. A platform without lineage awareness accumulates hidden technical debt
that surfaces as unexplainable data quality incidents.

---

## Related Documents

- `architecture.md` — full lineage design with diagram and column mapping table
- `../../mini-lakehouse-kafka/` — upstream pipeline this lineage model references
- `../../mongo-nosql-poc/` — downstream read model at the lineage terminal node
