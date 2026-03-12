# Abschluss: GitHub Push & CV-Ergänzung

---

## 1. Lokale Ordnerstruktur nach dem heutigen Tag

```
data-architecture-portfolio/
├── README.md                          ← ersetzen mit dem neuen Portfolio README
├── mini-lakehouse-kafka/              ← unverändert
├── mongo-nosql-poc/                   ← unverändert
├── terraform-data-platform-skeleton/  ← unverändert
├── data-lineage-design/               ← NEU (Component 4)
│   ├── README.md
│   ├── architecture.md
│   └── docs/
│       └── ADR-001-lineage-granularity.md
└── metadata-schema-evolution/         ← NEU (Component 5)
    ├── README.md
    ├── architecture.md
    └── docs/
        └── ADR-001-versioning-approach.md
```

---

## 2. GitHub Push — Befehle

```bash
cd data-architecture-portfolio

# Status prüfen
git status

# Beide neuen Ordner stagen
git add data-lineage-design/
git add metadata-schema-evolution/

# Aktualisiertes Root README stagen
git add README.md

# Commit
git commit -m "Add data lineage design and schema evolution strategy (components 4 & 5)

- data-lineage-design: end-to-end lineage mapping across real pipeline code
  - column-level mappings with actual field names (event_id, amount, status)
  - status derivation from eventType as primary column-level example
  - infrastructure context via terraform retention policy
  - ADR: dataset-level first, column-level selective

- metadata-schema-evolution: schema evolution strategy across all layers
  - four breakpoint analysis (StructType, .select(), DuckDB SQL, $switch)
  - versioning approach via event_version / eventVersion field
  - backward compatibility rules and migration pattern
  - ADR: convention-based versioning without Schema Registry"

# Push
git push origin main
```

---

## 3. CV-Ergänzungen

Die folgenden Skills kannst du deinem CV hinzufügen —
formuliert so, dass sie für Recruiter und technische Entscheider lesbar sind.

### Skills-Sektion (technisch)

**Data Architecture & Modeling**
- Event-driven data modeling (Event Store, CQRS-style Read Models)
- Medallion Architecture (Bronze / Silver / Gold) with Apache Kafka and Spark
- Data Lineage Design: dataset-level and column-level traceability
- Schema Evolution Strategy across streaming, document, and batch layers

**Data Engineering**
- Apache Kafka: event production, consumer groups, offset management, idempotent delivery
- Apache Spark Structured Streaming: Kafka ingestion, Parquet sink, checkpointing, deduplication
- MongoDB: append-only event modeling, aggregation pipelines, `$merge` projections, TTL control
- DuckDB: analytical queries over Parquet files (Silver layer)

**Infrastructure as Code**
- Terraform: modular design (network / storage / compute), environment layering (dev/prod)
- Remote state strategy with S3 + DynamoDB / Azure Blob Storage
- Architecture Decision Records (ADR) for infrastructure trade-offs

**Architecture Documentation**
- Architecture Decision Records (ADR)
- Trade-off documentation and explainability-first design
- Conceptual data lineage and schema evolution documentation

---

### Portfolio-Satz für LinkedIn / CV (Kurzform)

> Built a five-component data architecture portfolio demonstrating
> event-driven streaming pipelines (Kafka + Spark), NoSQL event modeling
> (MongoDB CQRS), Infrastructure as Code (Terraform), data lineage design,
> and schema evolution strategy across all layers.

### Portfolio-Link

```
github.com/awehro/data-architecture-portfolio
```

---

### Für den CV-Abschnitt "Projekte" oder "Weiterbildung"

**Data Architecture Portfolio** | 2026 | Eigenentwicklung

Eigenständig entwickeltes Portfolio zur Vertiefung von Data Architecture
und Data Engineering Kompetenzen. Fünf aufeinander aufbauende Komponenten:

- Streaming-Pipeline mit Kafka und Spark Structured Streaming (Bronze/Silver/Gold)
- NoSQL Event Store und Read Model mit MongoDB (CQRS-Pattern)
- Infrastructure as Code für eine modulare Datenplattform mit Terraform
- Konzeptuelles Data Lineage Design mit echten Feldnamen und Transformationen
- Schema Evolution Strategie mit Breakpoint-Analyse und Migrationsansatz

Technologien: Python · Apache Kafka · Apache Spark · MongoDB · DuckDB ·
Terraform · Docker · Architecture Decision Records

GitHub: github.com/awehro/data-architecture-portfolio
