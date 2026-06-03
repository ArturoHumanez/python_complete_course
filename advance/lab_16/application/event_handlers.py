import logging

from advance.lab_16.domain.events import (
    DomainEvent,
    OrderCancelled,
    OrderCompleted,
    OrderCreated,
)

logger = logging.getLogger(__name__)


class EventBus:
    """Despacha eventos a sus manejadores."""

    def __init__(self) -> None:
        self._handlers: dict[type, list] = {}

    def register(self, event_type: type, handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, events: list[DomainEvent]) -> None:
        for event in events:
            handlers = self._handlers.get(type(event), [])
            for handler in handlers:
                handler(event)


# === Handlers concretos ===


def on_order_created(event: OrderCreated) -> None:
    logger.info(
        "Evento OrderCreated: orden #%d de %s por $%.2f",
        event.order_id,
        event.customer,
        event.total,
    )


def on_order_completed(event: OrderCompleted) -> None:
    logger.info(
        "Evento OrderCompleted: orden #%d de %s",
        event.order_id,
        event.customer,
    )


def on_order_cancelled(event: OrderCancelled) -> None:
    logger.info(
        "Evento OrderCancelled: orden #%d de %s",
        event.order_id,
        event.customer,
    )


def create_event_bus() -> EventBus:
    """Crea el event bus con todos los handlers registrados."""
    bus = EventBus()
    bus.register(OrderCreated, on_order_created)
    bus.register(OrderCompleted, on_order_completed)
    bus.register(OrderCancelled, on_order_cancelled)
    return bus
