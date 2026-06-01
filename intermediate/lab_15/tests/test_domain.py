import pytest

from intermediate.lab_15.domain.entities import Order, OrderItem


class TestOrderItem:
    def test_subtotal(self):
        item = OrderItem(product="Laptop", price=25000, quantity=2)
        assert item.subtotal == 50000

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="positivo"):
            OrderItem(product="X", price=-5, quantity=1)

    def test_zero_quantity_raises(self):
        with pytest.raises(ValueError, match=">= 1"):
            OrderItem(product="X", price=100, quantity=0)


class TestOrder:
    @pytest.fixture
    def items(self):
        return [
            OrderItem(product="Laptop", price=25000, quantity=1),
            OrderItem(product="Mouse", price=350, quantity=2),
        ]

    def test_total(self, items):
        order = Order(customer="Juan", items=items)
        assert order.total == 25700

    def test_complete(self, items):
        order = Order(customer="Juan", items=items)
        order.complete()
        assert order.status == "completed"

    def test_cannot_complete_cancelled(self, items):
        order = Order(customer="Juan", items=items)
        order.cancel()
        with pytest.raises(ValueError, match="cancelada"):
            order.complete()

    def test_cannot_cancel_completed(self, items):
        order = Order(customer="Juan", items=items)
        order.complete()
        with pytest.raises(ValueError, match="completada"):
            order.cancel()

    def test_empty_customer_raises(self, items):
        with pytest.raises(ValueError, match="vacío"):
            Order(customer="", items=items)

    def test_empty_items_raises(self):
        with pytest.raises(ValueError, match="al menos un item"):
            Order(customer="Juan", items=[])