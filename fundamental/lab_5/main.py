from typing import Literal, Protocol, TypedDict

# === TypedDict para datos crudos (como vendrían de un JSON) ===


class RawOrderItem(TypedDict):
    product: str
    price: float
    quantity: int


class RawOrder(TypedDict):
    id: int
    customer: str
    status: str
    items: list[RawOrderItem]


# === Protocol — contrato para cualquier repositorio de órdenes ===


class OrderRepository(Protocol):
    def save(self, order: RawOrder) -> None: ...
    def find_by_id(self, order_id: int) -> RawOrder | None: ...
    def find_by_status(self, status: str) -> list[RawOrder]: ...


# === Implementación en memoria (cumple el Protocol sin heredar) ===


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[int, RawOrder] = {}

    def save(self, order: RawOrder) -> None:
        self._orders[order["id"]] = order

    def find_by_id(self, order_id: int) -> RawOrder | None:
        return self._orders.get(order_id)

    def find_by_status(self, status: str) -> list[RawOrder]:
        return [o for o in self._orders.values() if o["status"] == status]


# === Función que depende del Protocol, no de la implementación ===

Status = Literal["pending", "completed", "cancelled"]


def get_orders_summary(repo: OrderRepository, status: Status) -> dict[str, float]:
    """Obtiene resumen de totales por cliente para un estatus dado."""
    orders = repo.find_by_status(status)
    summary: dict[str, float] = {}
    for order in orders:
        customer = order["customer"]
        total = sum(item["price"] * item["quantity"] for item in order["items"])
        summary[customer] = summary.get(customer, 0.0) + total
    return summary


if __name__ == "__main__":
    # Crear repositorio y agregar órdenes
    repo = InMemoryOrderRepository()

    repo.save(
        {
            "id": 1,
            "customer": "Juan",
            "status": "completed",
            "items": [{"product": "Laptop", "price": 25000.0, "quantity": 1}],
        }
    )
    repo.save(
        {
            "id": 2,
            "customer": "María",
            "status": "completed",
            "items": [{"product": "Mouse", "price": 350.0, "quantity": 2}],
        }
    )
    repo.save(
        {
            "id": 3,
            "customer": "Juan",
            "status": "pending",
            "items": [{"product": "Teclado", "price": 800.0, "quantity": 1}],
        }
    )

    # Esto funciona — "completed" es un Status válido
    summary = get_orders_summary(repo, "completed")
    print("Completadas:", summary)

    # Esto mypy lo marcaría como error:
    # summary_refounded = get_orders_summary(repo, "refunded")
    # print("summary_refounded:", summary_refounded)
