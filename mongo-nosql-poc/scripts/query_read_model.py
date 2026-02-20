from __future__ import annotations

from datetime import datetime, timezone
from pymongo import MongoClient


MONGO_URI = "mongodb://app:apppw@localhost:27017/poc?authSource=poc"


def main() -> None:
    client = MongoClient(MONGO_URI)
    db = client["poc"]
    orders = db["orders_read"]

    print("=== newest orders (orders_read) ===")
    newest = list(orders.find({}, {"_id": 0}).sort("updatedAt", -1).limit(10))
    for doc in newest:
        print(doc)

    status = "CANCELLED"
    print(f"\n=== orders with status={status} ===")
    cancelled = list(orders.find({"status": status}, {"_id": 0}).sort("updatedAt", -1))
    for doc in cancelled:
        print(doc)

    customer_id = "C-1"
    print(f"\n=== orders for customerId={customer_id} ===")
    by_customer = list(
        orders.find({"customerId": customer_id}, {"_id": 0}).sort("updatedAt", -1)
    )
    for doc in by_customer:
        print(doc)

    print(f"\nquery time: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()

