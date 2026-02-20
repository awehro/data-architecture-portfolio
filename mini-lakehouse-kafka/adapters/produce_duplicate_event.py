import json
from datetime import datetime, timezone
from confluent_kafka import Producer

TOPIC = "events-orders"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def delivery_report(err, msg):
    if err is not None:
        print(f"[DELIVERY ERROR] {err}")
    else:
        print(f"[DELIVERED] partition={msg.partition()} offset={msg.offset()} key={msg.key().decode('utf-8')}")

def main():
    p = Producer(
        {
            "bootstrap.servers": "localhost:9092",
            "acks": "all",
            "enable.idempotence": True,
        }
    )

    fixed_event_id = "DUPLICATE-DEMO-0001"
    event = {
        "event_id": fixed_event_id,
        "event_time": now_iso(),
        "order_id": "ORD-9999",
        "customer_id": "CUST-999",
        "amount": 42.0,
        "currency": "EUR",
        "status": "CREATED",
        "source": "demo",
        "seq": 9999,
    }

    key = event["order_id"].encode("utf-8")
    value = json.dumps(event).encode("utf-8")

    print("Sending the SAME event twice (same event_id)...")
    for i in range(2):
        p.produce(TOPIC, key=key, value=value, on_delivery=delivery_report)
        p.flush(10)

    print("Done. event_id=", fixed_event_id)

if __name__ == "__main__":
    main()

