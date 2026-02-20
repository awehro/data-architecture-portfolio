import json
import time
import uuid
import random
from datetime import datetime, timezone

from confluent_kafka import Producer


TOPIC = "events-orders"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_event(i: int) -> dict:
    order_id = f"ORD-{random.randint(1000, 1005)}"  # small range to show key/partition behavior
    return {
        "event_id": str(uuid.uuid4()),
        "event_time": now_iso(),
        "order_id": order_id,
        "customer_id": f"CUST-{random.randint(1, 50)}",
        "amount": round(random.uniform(10, 300), 2),
        "currency": "EUR",
        "status": random.choice(["CREATED", "PAID", "SHIPPED"]),
        "source": random.choice(["web", "mobile"]),
        "seq": i,
    }


def delivery_report(err, msg):
    if err is not None:
        print(f"[DELIVERY ERROR] {err}")
        return
    print(
        f"[DELIVERED] topic={msg.topic()} partition={msg.partition()} offset={msg.offset()} "
        f"key={msg.key().decode('utf-8') if msg.key() else None}"
    )


def main():
    producer = Producer(
        {
            "bootstrap.servers": "localhost:9092",
            # good demo defaults:
            "acks": "all",
            "enable.idempotence": True,  # reduces duplicates on retries (still not magic EOS end-to-end)
            "linger.ms": 10,
        }
    )

    print("Producing events to", TOPIC)
    for i in range(1, 31):
        event = make_event(i)
        key = event["order_id"].encode("utf-8")
        value = json.dumps(event).encode("utf-8")

        producer.produce(TOPIC, key=key, value=value, on_delivery=delivery_report)
        producer.poll(0)  # trigger callbacks

        time.sleep(0.1)

    producer.flush(10)
    print("Done.")


if __name__ == "__main__":
    main()

