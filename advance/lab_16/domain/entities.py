from dataclasses import dataclass, field
from datetime import datetime, timezone

from advance.lab_16.domain.events import (
    DomainEvent,
    OrderCancelled,
    OrderCompleted,
    OrderCreated,
)

@dataclass
class OrderItem:
    product: str
    price: float
    quantity: int = 1

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError(f"Precio debe ser positivo, recibido: {self.price}")
        if self.quantity < 1:
            raise ValueError(f"Cantidad debe ser >= 1, recibido: {self.quantity}")

@dataclass
class Order:
    customer: str
    items: list[OrderItem]
    id: int | None = None
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    events: list[DomainEvent] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def mark_created(self) -> None:
        """Registra el evento de creación."""
        self.events.append(
            OrderCreated(
                order_id=self.id or 0,
                customer=self.customer,
                total=self.total,
            )
        )

    def complete(self) -> None:
        if self.status == "cancelled":
            raise ValueError("No se puede completar una orden cancelada")
        self.status = "completed"
        self.events.append(
            OrderCompleted(order_id=self.id or 0, customer=self.customer)
        )

    def cancel(self) -> None:
        if self.status == "completed":
            raise ValueError("No se puede cancelar una orden completada")
        self.status = "cancelled"
        self.events.append(
            OrderCancelled(order_id=self.id or 0, customer=self.customer)
        )

    def collect_events(self) -> list[DomainEvent]:
        """Extrae y limpia los eventos pendientes."""
        events = self.events.copy()
        self.events.clear()
        return events

    def __post_init__(self) -> None:
        if not self.customer.strip():
            raise ValueError("Customer no puede estar vacío")
        if not self.items:
            raise ValueError("La orden debe tener al menos un item")