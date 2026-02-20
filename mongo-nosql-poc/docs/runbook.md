# Runbook — MongoDB NoSQL PoC (Event Store + Read Model)

## 0) Purpose
Local MongoDB PoC focused on **interview/CV credibility**:
- **Event Store** (`events`) as append-only source of truth
- **Read Model** (`orders_read`) as query-optimized projection
- Demonstrates: **Docker Compose**, **indexes**, **TTL (ephemeral only)**, **aggregation pipeline**, **projection via $merge**

This is intentionally not production-hardening.

---

## 1) Prerequisites
- Docker Desktop installed and running
- `docker compose` available
- macOS Terminal (or any shell)

---

## 2) Project layout
Create this structure:

```
mongo-nosql-poc/
  docker/
    mongo-init/
      00-create-users.js
      01-create-indexes.js
  docs/
    runbook.md
    adr-0001-modeling-decisions.md
  scripts/
  .env
  docker-compose.yml
  README.md
```

---

## 3) Configuration

### 3.1 `.env`
Create `.env` in project root:

```dotenv
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=rootpw

MONGO_APP_DB=poc
MONGO_APP_USER=app
MONGO_APP_PASSWORD=apppw

MONGO_PORT=27017
MONGO_EXPRESS_PORT=8081
```

Notes:
- For a public repo: do **not** commit `.env`. Use `.env.example` + `.gitignore`.

### 3.2 `docker-compose.yml`
Use a minimal setup: MongoDB + mongo-express.

```yaml
services:
  mongodb:
    image: mongo:7
    container_name: mongo-poc
    restart: unless-stopped
    ports:
      - "${MONGO_PORT:-27017}:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
    volumes:
      - mongo_data:/data/db
      - ./docker/mongo-init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD", "mongosh", "--quiet", "mongodb://localhost:27017/admin", "--eval", "db.runCommand({ ping: 1 }).ok"]
      interval: 10s
      timeout: 5s
      retries: 10

  mongo-express:
    image: mongo-express:1
    container_name: mongo-express-poc
    restart: unless-stopped
    depends_on:
      mongodb:
        condition: service_healthy
    ports:
      - "${MONGO_EXPRESS_PORT:-8081}:8081"
    environment:
      ME_CONFIG_MONGODB_SERVER: mongodb
      ME_CONFIG_MONGODB_ADMINUSERNAME: ${MONGO_INITDB_ROOT_USERNAME}
      ME_CONFIG_MONGODB_ADMINPASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
      ME_CONFIG_BASICAUTH: "false"

volumes:
  mongo_data:
```

---

## 4) Start / Stop

### 4.1 Start
From project root:

```bash
docker compose up -d
docker compose ps
```

Expected:
- `mongo-poc` is `healthy`
- `mongo-express-poc` is `running`

### 4.2 Open UI
Open in browser:

```
http://localhost:8081
```

### 4.3 Stop (keep data)
```bash
docker compose down
```

### 4.4 Stop + delete data (destructive)
```bash
docker compose down -v
```

---

## 5) Make DB `poc` visible (materialize)
MongoDB databases typically appear only after at least one document is written.

Run (from macOS shell):

```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");
dbp.getCollection("bootstrap").insertOne({ createdAt: new Date(), note: "bootstrap" });
print("insert ok");
'
```

Verify:

```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval 'show dbs'
```

Expected: `poc` appears.

---

## 6) Event Store setup (`events`)

### 6.1 Create collection + indexes
```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");

dbp.createCollection("events");

// idempotency / dedup
dbp.events.createIndex({ eventId: 1 }, { unique: true });

// fast replay by aggregate
dbp.events.createIndex({ aggregateType: 1, aggregateId: 1, occurredAt: 1 });

printjson(dbp.events.getIndexes());
'
```

---

## 7) Seed sample events (mongosh)
Insert 6 sample events for two orders:

```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");

dbp.events.insertMany([
  { eventId: "evt-001", aggregateType: "order", aggregateId: "ORD-1001", eventType: "OrderCreated", eventVersion: 1,
    occurredAt: new Date("2026-01-28T17:00:00Z"), recordedAt: new Date(),
    payload: { customerId: "C-1", items: [ { sku: "SKU-1", qty: 2, unitPrice: 12.5 } ], currency: "EUR" },
    metadata: { producer: "mongosh", correlationId: "corr-1001", causationId: null } },

  { eventId: "evt-002", aggregateType: "order", aggregateId: "ORD-1001", eventType: "OrderPaid", eventVersion: 1,
    occurredAt: new Date("2026-01-28T17:05:00Z"), recordedAt: new Date(),
    payload: { amount: 25.0, method: "card" },
    metadata: { producer: "mongosh", correlationId: "corr-1001", causationId: "evt-001" } },

  { eventId: "evt-003", aggregateType: "order", aggregateId: "ORD-1001", eventType: "OrderShipped", eventVersion: 1,
    occurredAt: new Date("2026-01-28T17:20:00Z"), recordedAt: new Date(),
    payload: { carrier: "DHL", tracking: "DHL-XYZ" },
    metadata: { producer: "mongosh", correlationId: "corr-1001", causationId: "evt-002" } },

  { eventId: "evt-004", aggregateType: "order", aggregateId: "ORD-1002", eventType: "OrderCreated", eventVersion: 1,
    occurredAt: new Date("2026-01-28T17:10:00Z"), recordedAt: new Date(),
    payload: { customerId: "C-2", items: [ { sku: "SKU-2", qty: 1, unitPrice: 99.0 } ], currency: "EUR" },
    metadata: { producer: "mongosh", correlationId: "corr-1002", causationId: null } },

  { eventId: "evt-005", aggregateType: "order", aggregateId: "ORD-1002", eventType: "OrderPaid", eventVersion: 1,
    occurredAt: new Date("2026-01-28T17:12:00Z"), recordedAt: new Date(),
    payload: { amount: 99.0, method: "paypal" },
    metadata: { producer: "mongosh", correlationId: "corr-1002", causationId: "evt-004" } },

  { eventId: "evt-006", aggregateType: "order", aggregateId: "ORD-1002", eventType: "OrderCancelled", eventVersion: 1,
    occurredAt: new Date("2026-01-28T17:15:00Z"), recordedAt: new Date(),
    payload: { reason: "customer_request" },
    metadata: { producer: "mongosh", correlationId: "corr-1002", causationId: "evt-005" } }
]);

print("events count: " + dbp.events.countDocuments({ aggregateType: "order" }));
'
```

Expected: `events count: 6`

---

## 8) Aggregation example: current status per order
This shows how to compute a “current view” directly from the Event Store.

```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");

const pipeline = [
  { $match: { aggregateType: "order" } },
  { $sort: { aggregateId: 1, occurredAt: 1 } },
  {
    $group: {
      _id: "$aggregateId",
      lastEventType: { $last: "$eventType" },
      lastOccurredAt: { $last: "$occurredAt" },
      eventCount: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
];

printjson(dbp.events.aggregate(pipeline).toArray());
'
```

Expected:
- `ORD-1001 -> OrderShipped`
- `ORD-1002 -> OrderCancelled`
- `eventCount` is 3 for each

---

## 9) Read Model setup (`orders_read`)

### 9.1 Create collection + indexes
```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");

dbp.createCollection("orders_read");

// 1 document per order
dbp.orders_read.createIndex({ orderId: 1 }, { unique: true });

// typical queries
dbp.orders_read.createIndex({ customerId: 1, updatedAt: -1 });
dbp.orders_read.createIndex({ status: 1, updatedAt: -1 });

printjson(dbp.orders_read.getIndexes());
'
```

### 9.2 Full rebuild projection via `$merge`
```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");

dbp.events.aggregate([
  { $match: { aggregateType: "order" } },
  { $sort: { aggregateId: 1, occurredAt: 1 } },

  {
    $group: {
      _id: "$aggregateId",
      customerId: {
        $first: {
          $cond: [
            { $eq: ["$eventType", "OrderCreated"] },
            "$payload.customerId",
            "$$REMOVE"
          ]
        }
      },
      currency: {
        $first: {
          $cond: [
            { $eq: ["$eventType", "OrderCreated"] },
            "$payload.currency",
            "$$REMOVE"
          ]
        }
      },
      lastEventType: { $last: "$eventType" },
      updatedAt: { $last: "$occurredAt" }
    }
  },

  {
    $addFields: {
      orderId: "$_id",
      status: {
        $switch: {
          branches: [
            { case: { $eq: ["$lastEventType", "OrderCreated"] }, then: "CREATED" },
            { case: { $eq: ["$lastEventType", "OrderPaid"] }, then: "PAID" },
            { case: { $eq: ["$lastEventType", "OrderShipped"] }, then: "SHIPPED" },
            { case: { $eq: ["$lastEventType", "OrderCancelled"] }, then: "CANCELLED" }
          ],
          default: "UNKNOWN"
        }
      }
    }
  },

  { $project: { _id: 0, orderId: 1, customerId: 1, currency: 1, status: 1, updatedAt: 1 } },

  {
    $merge: {
      into: "orders_read",
      on: "orderId",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
]);

print("orders_read count: " + dbp.orders_read.countDocuments({}));
'
```

Expected: `orders_read count: 2`

---

## 10) TTL demo (ephemeral only; NOT on `events`)
TTL is demonstrated on a separate collection because TTL on an event store would destroy auditability and replay.

### 10.1 Create collection + TTL index
```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");

dbp.createCollection("events_debug");
dbp.events_debug.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });

printjson(dbp.events_debug.getIndexes());
'
```

### 10.2 Insert expiring document (TTL cleanup is async)
```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");

dbp.events_debug.insertOne({
  message: "this will expire",
  createdAt: new Date(),
  expiresAt: new Date(Date.now() + 30 * 1000)
});

print("events_debug count now: " + dbp.events_debug.countDocuments({}));
'
```

Re-check later:

```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin --eval '
const dbp = db.getSiblingDB("poc");
print("events_debug count later: " + dbp.events_debug.countDocuments({}));
'
```

Expected: document disappears after a short while.

---

## 11) Troubleshooting

### 11.1 `use` not found
If you see `zsh: command not found: use`, you are not inside `mongosh`. Enter `mongosh` like:

```bash
docker exec -it mongo-poc mongosh -u root -p rootpw --authenticationDatabase admin
```

### 11.2 More-line prompt (`...`)
If you see `...` in `mongosh`, you are in multi-line input mode.
Press `Ctrl + C` to cancel and return to a normal prompt.

### 11.3 Database not visible in mongo-express
Materialize it by inserting at least one document (see section 5).

