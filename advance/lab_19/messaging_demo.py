import json
import logging

from advance.lab_19.event_publisher import FakeRedis, RedisEventPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def demo_with_fake_redis():
    """Demuestra el flujo de eventos sin necesitar Redis real."""
    fake_redis = FakeRedis()
    publisher = RedisEventPublisher(fake_redis)

    print("=== Publicando eventos con FakeRedis ===\n")

    publisher.publish_order_created(order_id=1, customer="Juan", total=25700)
    publisher.publish_order_created(order_id=2, customer="Maria", total=800)
    publisher.publish_order_completed(order_id=1, customer="Juan")

    print(f"\n=== {len(fake_redis.published)} eventos publicados ===\n")

    for channel, message in fake_redis.published:
        event = json.loads(message)
        print(f"  Canal: {channel}")
        print(f"  Tipo: {event['event_type']}")
        print(f"  Orden: #{event['order_id']} — {event['customer']}")
        print()

    # Demostrar que con Redis real sería:
    print("=== Para usar con Redis real ===")
    print("  import redis")
    print("  client = redis.Redis(host='localhost', port=6379)")
    print("  publisher = RedisEventPublisher(client)")
    print("  publisher.publish_order_created(1, 'Juan', 25700)")


def demo_with_real_redis():
    """Conecta a Redis real si está disponible."""
    try:
        import redis

        client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        client.ping()
        logger.info("Conectado a Redis")

        publisher = RedisEventPublisher(client)
        publisher.publish_order_created(order_id=1, customer="Juan", total=25700)
        publisher.publish_order_completed(order_id=1, customer="Juan")

    except Exception as e:
        logger.warning("Redis no disponible: %s — usando FakeRedis", e)
        demo_with_fake_redis()


if __name__ == "__main__":
    demo_with_fake_redis()
