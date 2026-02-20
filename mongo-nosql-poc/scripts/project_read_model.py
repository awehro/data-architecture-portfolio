from __future__ import annotations

from pymongo import MongoClient


MONGO_URI = "mongodb://app:apppw@localhost:27017/poc?authSource=poc"


def main() -> None:
    client = MongoClient(MONGO_URI)
    db = client["poc"]
    events = db["events"]

    pipeline = [
        {"$match": {"aggregateType": "order"}},
        {"$sort": {"aggregateId": 1, "occurredAt": 1}},
        {
            "$group": {
                "_id": "$aggregateId",
                "customerId": {
                    "$first": {
                        "$cond": [
                            {"$eq": ["$eventType", "OrderCreated"]},
                            "$payload.customerId",
                            "$$REMOVE",
                        ]
                    }
                },
                "currency": {
                    "$first": {
                        "$cond": [
                            {"$eq": ["$eventType", "OrderCreated"]},
                            "$payload.currency",
                            "$$REMOVE",
                        ]
                    }
                },
                "lastEventType": {"$last": "$eventType"},
                "updatedAt": {"$last": "$occurredAt"},
            }
        },
        {
            "$addFields": {
                "orderId": "$_id",
                "status": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$lastEventType", "OrderCreated"]}, "then": "CREATED"},
                            {"case": {"$eq": ["$lastEventType", "OrderPaid"]}, "then": "PAID"},
                            {"case": {"$eq": ["$lastEventType", "OrderShipped"]}, "then": "SHIPPED"},
                            {"case": {"$eq": ["$lastEventType", "OrderCancelled"]}, "then": "CANCELLED"},
                        ],
                        "default": "UNKNOWN",
                    }
                },
            }
        },
        {"$project": {"_id": 0, "orderId": 1, "customerId": 1, "currency": 1, "status": 1, "updatedAt": 1}},
        {
            "$merge": {
                "into": "orders_read",
                "on": "orderId",
                "whenMatched": "replace",
                "whenNotMatched": "insert",
            }
        },
    ]

    # Running the aggregation executes the merge on the server.
    # We don't need the returned documents.
    list(events.aggregate(pipeline))
    count = db["orders_read"].count_documents({})
    print(f"projection done. orders_read count={count}")


if __name__ == "__main__":
    main()

