import logging

from intermediate.lab_12.ports import Order

logger = logging.getLogger(__name__)

# === Adaptador en memoria ===

class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._next_id: int = 1

    def save(self, order: Order) -> Order:
        if order.id is None:
            order.id = self._next_id
            self._next_id += 1
        self._orders[order.id] = order
        logger.info("Orden %d guardada en memoria", order.id)
        return order

    def find_by_id(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    def find_by_status(self, status: str) -> list[Order]:
        return [o for o in self._orders.values() if o.status == status]

# === Adaptador SQL (simulado con dict pero misma interfaz) ===

class SqlOrderRepository:
    """Simula un repositorio SQL — misma interfaz que InMemory."""

    def __init__(self) -> None:
        self._storage: dict[int, dict] = {}
        self._next_id: int = 1

    def save(self, order: Order) -> Order:
        if order.id is None:
            order.id = self._next_id
            self._next_id += 1
        self._storage[order.id] = {
            "id": order.id,
            "customer": order.customer,
            "status": order.status,
            "items": order.items,
        }
        logger.info("Orden %d guardada en SQL", order.id)
        return order

    def find_by_id(self, order_id: int) -> Order | None:
        data = self._storage.get(order_id)
        if not data:
            return None
        return Order(**data)

    def find_by_status(self, status: str) -> list[Order]:
        return [
            Order(**data)
            for data in self._storage.values()
            if data["status"] == status
        ]

# === Adaptador de notificación ===

class ConsoleNotifier:
    def send(self, to: str, message: str) -> bool:
        logger.info("Notificación a %s: %s", to, message)
        return True


class FakeNotifier:
    """Para tests — registra las notificaciones sin enviar nada."""

    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send(self, to: str, message: str) -> bool:
        self.sent.append({"to": to, "message": message})
        return True