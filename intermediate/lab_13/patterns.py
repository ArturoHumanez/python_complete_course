from dataclasses import dataclass, field
from typing import Protocol

# === Entidad ===


@dataclass
class Order:
    id: int | None = None
    customer: str = ""
    items: list[dict] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(i.get("price", 0) * i.get("quantity", 0) for i in self.items)


# === Strategy: Pricing ===


class PricingStrategy(Protocol):
    def calculate(self, order: Order) -> float: ...


class StandardPricing:
    def calculate(self, order: Order) -> float:
        return order.total


class VipPricing:
    """VIPs obtienen 15% de descuento."""

    def calculate(self, order: Order) -> float:
        return order.total * 0.85


class WholesalePricing:
    """Mayoreo: 25% de descuento si hay más de 10 items."""

    def calculate(self, order: Order) -> float:
        total_qty = sum(i.get("quantity", 0) for i in order.items)
        if total_qty > 10:
            return order.total * 0.75
        return order.total


# === Repository Protocol ===


class OrderRepository(Protocol):
    def save(self, order: Order) -> Order: ...
    def find_by_id(self, order_id: int) -> Order | None: ...
    def find_by_status(self, status: str) -> list[Order]: ...

    # === Adaptador base en memoria ===


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._next_id = 1

    def save(self, order: Order) -> Order:
        if order.id is None:
            order.id = self._next_id
            self._next_id += 1
        self._orders[order.id] = order
        return order

    def find_by_id(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    def find_by_status(self, status: str) -> list[Order]:
        return [o for o in self._orders.values()]


# === Decorator: Cached Repository ===


class CachedRepository:
    """Decorator que agrega caché a cualquier repositorio."""

    def __init__(self, inner: OrderRepository) -> None:
        self._inner = inner
        self._cache: dict[int, Order] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def save(self, order: Order) -> Order:
        result = self._inner.save(order)
        self._cache[result.id] = result
        return result

    def find_by_id(self, order_id: int) -> Order | None:
        if order_id in self._cache:
            self.cache_hits += 1
            return self._cache[order_id]
        self.cache_misses += 1
        result = self._inner.find_by_id(order_id)
        if result:
            self._cache[order_id] = result
        return result

    def find_by_status(self, status: str) -> list[Order]:
        return self._inner.find_by_status(status)

    # === Adapter: External Provider ===


class ExternalPricingApi:
    """Simula una API externa de pricing con interfaz diferente."""

    def get_price_multiplier(self, customer_tier: str) -> float:
        tiers = {"standard": 1.0, "gold": 0.9, "platinum": 0.8}
        return tiers.get(customer_tier, 1.0)


class ExternalPricingAdapter:
    """Adapta la API externa al Protocol PricingStrategy."""

    def __init__(self, api: ExternalPricingApi, tier: str) -> None:
        self._api = api
        self._tier = tier

    def calculate(self, order: Order) -> float:
        multiplier = self._api.get_price_multiplier(self._tier)
        return order.total * multiplier
