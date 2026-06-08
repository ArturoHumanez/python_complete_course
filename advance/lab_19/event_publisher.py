import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RedisEventPublisher:
    """Publica eventos de dominio en Redis Pub/Sub."""

    def __init__(self, redis_client):
        self._redis = redis_client

    def publish_order_created(self, order_id: int, customer: str, total: float):
        event = {
            "event_type": "OrderCreated",
            "order_id": order_id,
            "customer": customer,
            "total": total,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }
        self._redis.publish("orders.events", json.dumps(event))
        logger.info("Evento publicado: OrderCreated #%d", order_id)

    def publish_order_completed(self, order_id: int, customer: str):
        event = {
            "event_type": "OrderCompleted",
            "order_id": order_id,
            "customer": customer,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }
        self._redis.publish("orders.events", json.dumps(event))
        logger.info("Evento publicado: OrderCompleted #%d", order_id)


class FakeRedis:
    """Simula Redis para cuando no hay servidor disponible."""

    def __init__(self):
        self.published: list[tuple[str, str]] = []

    def publish(self, channel: str, message: str):
        self.published.append((channel, message))
        logger.info("FakeRedis [%s]: %s", channel, message)


class RedisEventSubscriber:
    """Escucha eventos de Redis Pub/Sub."""

    def __init__(self, redis_client):
        self._redis = redis_client

    def listen(self, channel: str = "orders.events"):
        pubsub = self._redis.pubsub()
        pubsub.subscribe(channel)
        logger.info("Escuchando eventos en '%s'...", channel)
        for message in pubsub.listen():
            if message["type"] == "message":
                event = json.loads(message["data"])
                logger.info("Evento recibido: %s", event)
                yield event