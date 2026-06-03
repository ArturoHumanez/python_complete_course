from typing import Protocol

from dataclasses import dataclass, field

# === Entidad de dominio ===


@dataclass
class Order:
    id: int | None = None
    customer: str = ""
    status: str = "pending"
    items: list[dict] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(
            item.get("price", 0) * item.get("quantity", 0) for item in self.items
        )


# === Puertos (interfaces) ===


class OrderRepository(Protocol):
    def save(self, order: Order) -> Order: ...
    def find_by_id(self, order_id: int) -> Order | None: ...
    def find_by_status(self, status: str) -> list[Order]: ...


class NotificationPort(Protocol):
    def send(self, to: str, message: str) -> bool: ...
