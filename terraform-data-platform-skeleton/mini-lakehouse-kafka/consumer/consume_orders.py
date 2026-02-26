import os
import json
from confluent_kafka import Consumer, KafkaError

TOPIC = "events-orders"
GROUP_ID = os.getenv("GROUP_ID", "demo-orders-consumer")


def main():
    c = Consumer(
        {
            "bootstrap.servers": "localhost:9092",
            "group.id": GROUP_ID,
            "auto.offset.reset": "earliest",  # read from beginning if no committed offset
            "enable.auto.commit": True,
        }
    )

    c.subscribe([TOPIC])
    print(f"Consuming from topic={TOPIC} group.id={GROUP_ID} (Ctrl+C to stop)")

    try:
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                # ignore benign partition EOF errors
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"[ERROR] {msg.error()}")
                continue

            key = msg.key().decode("utf-8") if msg.key() else None
            val = msg.value().decode("utf-8") if msg.value() else None
            try:
                event = json.loads(val) if val else None
            except Exception:
                event = None

            print(
                f"[RECV] partition={msg.partition()} offset={msg.offset()} key={key} "
                f"event_id={event.get('event_id') if event else None} order_id={event.get('order_id') if event else None}"
            )
    except KeyboardInterrupt:
        print("\nStopping consumer...")
    finally:
        c.close()


if __name__ == "__main__":
    main()

