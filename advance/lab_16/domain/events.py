from dataclasses import dataclass, field
from datetime import datetime, timezone

# Cada evento anuncia lo que pasó No tienen lógica


@dataclass
class DomainEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OrderCreated(DomainEvent):
    order_id: int = 0
    customer: str = ""
    total: float = 0.0


@dataclass
class OrderCompleted(DomainEvent):
    order_id: int = 0
    customer: str = ""


@dataclass
class OrderCancelled(DomainEvent):
    order_id: int = 0
    customer: str = ""
