# Terraform Data Platform Skeleton

A modular, environment-layered Terraform structure representing a minimal 
data platform architecture. Built as a portfolio demonstration of Infrastructure 
as Code best practices.

## Structure
```
├── modules/
│   ├── network/    # Virtual network abstraction
│   ├── storage/    # Data lake / blob storage layer
│   └── compute/    # Processing cluster abstraction
├── envs/
│   ├── dev/        # Development environment (small, short retention)
│   └── prod/       # Production environment (large, long retention)
└── docs/
    └── adr/        # Architecture Decision Records
```

## Design Decisions

**Module separation** follows the principle of single responsibility: each module 
owns one infrastructure concern. This allows teams to update storage configs 
without touching network logic.

**Environment layering** via `envs/` means the same module code runs in dev and 
prod – only the input variables differ. No code duplication, no drift risk.

**Cloud-agnostic approach**: `null_resource` is used as a placeholder. 
Replace with `aws_vpc`, `azurerm_storage_account`, etc. for real deployments.

## Remote State Strategy

See [ADR 001](docs/adr/001-remote-state-strategy.md) for the full rationale.

Short version: use S3+DynamoDB (AWS) or Azure Blob Storage for state backends 
with per-environment isolation and locking enabled. Local backend is used here 
for portfolio demonstration purposes.

## Usage
```bash
cd envs/dev
terraform init
terraform validate
terraform plan
```

## Skills Demonstrated

- Terraform module design and composition
- Environment isolation patterns (dev/prod)
- Input validation and output contracts
- Remote state architecture and locking strategy
- Architecture Decision Records (ADR)
=======
# Data Architecture Portfolio

This repository represents a structured collection of focused architecture components
demonstrating different data system design patterns.

The goal is not feature depth — but architectural clarity, modeling decisions,
and explainable trade-offs.

---

## Architectural Scope

This portfolio currently includes:

### 1. Streaming & Lakehouse Architecture  
**Folder:** `mini-lakehouse-kafka`

Demonstrates:
- Event ingestion via Kafka
- Stream processing
- Bronze / Silver layering
- Structured transformation patterns
- Separation of ingestion and processing concerns

Focus: Streaming data pipelines and layered data architecture.

---

### 2.  NoSQL Event Modeling Component  
**Folder:** `mongo-nosql-poc`

Demonstrates:
- Append-only Event Store modeling
- Read Model projection (CQRS-style)
- Idempotent event writes
- Aggregation-based materialization
- Controlled TTL usage
- Explicit trade-offs in data lifecycle design

Focus: Document database modeling and read/write separation.

---

## Architectural Themes Across Projects

Across these components, the following principles are intentionally demonstrated:

- Separation of concerns
- Explicit write vs read responsibilities
- Reproducible local environments (Docker-based)
- Clear indexing strategy
- Controlled trade-offs
- Modular system thinking

Each project is intentionally isolated to keep architectural concepts focused and explainable.

---

## Positioning

This portfolio demonstrates:

- Data modeling across storage paradigms
- Event-driven thinking
- Stream processing patterns
- Projection-based read optimization
- Practical infrastructure reproducibility

It is designed to show architectural reasoning rather than production hardening.

---

## Future Extensions

Potential future components may include:

- Real-time projection via streaming
- Cloud-native deployment patterns
- Observability & monitoring integration
- Schema evolution strategies
- Data governance examples

