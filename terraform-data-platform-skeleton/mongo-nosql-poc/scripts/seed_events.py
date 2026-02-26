from __future__ import annotations

from datetime import datetime, timezone
from pymongo import MongoClient, errors


MONGO_URI = "mongodb://app:apppw@localhost:27017/poc?authSource=poc"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def main() -> None:
    client = MongoClient(MONGO_URI)
    db = client["poc"]
    events = db["events"]

    now = utc_now()

    seed_events = [
        {
            "eventId": "py-evt-001",
            "aggregateType": "order",
            "aggregateId": "ORD-2001",
            "eventType": "OrderCreated",
            "eventVersion": 1,
            "occurredAt": now,
            "recordedAt": now,
            "payload": {
                "customerId": "C-3",
                "items": [{"sku": "SKU-9", "qty": 1, "unitPrice": 49.0}],
                "currency": "EUR",
            },
            "metadata": {
                "producer": "seed_events.py",
                "correlationId": "corr-2001",
                "causationId": None,
            },
        },
        {
            "eventId": "py-evt-002",
            "aggregateType": "order",
            "aggregateId": "ORD-2001",
            "eventType": "OrderPaid",
            "eventVersion": 1,
            "occurredAt": now,
            "recordedAt": now,
            "payload": {"amount": 49.0, "method": "card"},
            "metadata": {
                "producer": "seed_events.py",
                "correlationId": "corr-2001",
                "causationId": "py-evt-001",
            },
        },
    ]

    inserted = 0
    skipped = 0

    for event in seed_events:
        try:
            events.insert_one(event)
            inserted += 1
            print(f"inserted: {event['eventId']}")
        except errors.DuplicateKeyError:
            skipped += 1
            print(f"skipped (duplicate): {event['eventId']}")

    print(f"done (inserted={inserted}, skipped={skipped})")


if __name__ == "__main__":
    main()

