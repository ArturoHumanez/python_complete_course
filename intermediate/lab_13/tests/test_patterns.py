import pytest

from intermediate.lab_13.patterns import (
    CachedRepository,
    ExternalPricingAdapter,
    ExternalPricingApi,
    InMemoryOrderRepository,
    Order,
    StandardPricing,
    VipPricing,
    WholesalePricing,
)

SAMPLE_ITEMS = [
    {"product": "Laptop", "price": 10000, "quantity": 1},
    {"product": "Mouse", "price": 500, "quantity": 2},
]


# === Strategy tests ===


class TestPricingStrategy:
    @pytest.fixture
    def order(self):
        return Order(customer="Juan", items=SAMPLE_ITEMS)

    def test_standard_pricing(self, order):
        pricing = StandardPricing()
        assert pricing.calculate(order) == 11000.0

    def test_vip_pricing(self, order):
        pricing = VipPricing()
        assert pricing.calculate(order) == 11000.0 * 0.85

    def test_wholesale_under_threshold(self, order):
        pricing = WholesalePricing()
        # 3 items total, no aplica descuento
        assert pricing.calculate(order) == 11000.0

    def test_wholesale_over_threshold(self):
        big_order = Order(
            customer="Empresa",
            items=[{"product": "Cable", "price": 100, "quantity": 15}],
        )
        pricing = WholesalePricing()
        assert pricing.calculate(big_order) == 1500.0 * 0.75


# === Decorator tests ===


class TestCachedRepository:
    def test_find_by_id_caches(self):
        repo = InMemoryOrderRepository()
        cached = CachedRepository(repo)

        order = Order(customer="Juan", items=SAMPLE_ITEMS)
        saved = cached.save(order)

        # Primera búsqueda — viene del caché (se guardó en save)
        cached.find_by_id(saved.id)
        assert cached.cache_hits == 1

    def test_find_by_id_misses_then_caches(self):
        repo = InMemoryOrderRepository()
        order = Order(customer="Juan", items=SAMPLE_ITEMS)
        repo.save(order)  # guardado directo, sin pasar por caché

        cached = CachedRepository(repo)

        # Primera vez — miss, va al repo
        cached.find_by_id(order.id)
        assert cached.cache_misses == 1

        # Segunda vez — hit, viene del caché
        cached.find_by_id(order.id)
        assert cached.cache_hits == 1


# === Adapter tests ===


class TestExternalPricingAdapter:
    @pytest.fixture
    def order(self):
        return Order(customer="Juan", items=SAMPLE_ITEMS)

    def test_gold_tier(self, order):
        api = ExternalPricingApi()
        adapter = ExternalPricingAdapter(api, tier="gold")
        assert adapter.calculate(order) == 11000.0 * 0.9

    def test_platinum_tier(self, order):
        api = ExternalPricingApi()
        adapter = ExternalPricingAdapter(api, tier="platinum")
        assert adapter.calculate(order) == 11000.0 * 0.8

    def test_unknown_tier_uses_standard(self, order):
        api = ExternalPricingApi()
        adapter = ExternalPricingAdapter(api, tier="unknown")
        assert adapter.calculate(order) == 11000.0
