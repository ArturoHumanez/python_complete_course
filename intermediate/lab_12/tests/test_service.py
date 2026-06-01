import pytest

from intermediate.lab_12.adapters import (
    FakeNotifier,
    InMemoryOrderRepository,
    SqlOrderRepository,
)
from intermediate.lab_12.service import OrderService

SAMPLE_ITEMS = [
    {"product": "Laptop", "price": 25000, "quantity": 1},
    {"product": "Mouse", "price": 350, "quantity": 2},
]

# === LSP: el mismo test corre con ambos repositorios ===

@pytest.fixture(params=["memory", "sql"])
def repo(request):
    if request.param == "memory":
        return InMemoryOrderRepository()
    return SqlOrderRepository()

@pytest.fixture
def notifier():
    return FakeNotifier()

@pytest.fixture
def service(repo, notifier):
    return OrderService(repo=repo, notifier=notifier)

class TestOrderServiceLSP:
    """Todos estos tests pasan con InMemory y SQL — LSP."""
    def test_create_order(self, service):
        order = service.create_order("Juan", SAMPLE_ITEMS)
    
        assert order.id is not None
        assert order.customer == "Juan"    
        assert order.status == "pending"
        assert order.total == 25700
    
    def test_complete_order(self, service):
        order = service.create_order("Juan", SAMPLE_ITEMS)
        completed = service.complete_order(order.id)

        assert completed.status == "completed"

    def test_complete_nonexistent_order(self, service):
        with pytest.raises(ValueError, match="no encontrada"):
            service.complete_order(999)
            
    def test_get_completed_orders(self, service):
        service.create_order("Juan", SAMPLE_ITEMS)
        order2 = service.create_order("María", SAMPLE_ITEMS)
        service.complete_order(order2.id)

        completed = service.get_completed_orders()
        assert len(completed) == 1
        assert completed[0].customer == "María"
        
    def test_notification_sent_on_create(self, service, notifier):
        service.create_order("Juan", SAMPLE_ITEMS)

        assert len(notifier.sent) == 1
        assert notifier.sent[0]["to"] == "Juan"
        
    def test_notification_sent_on_complete(self, service, notifier):
        order = service.create_order("Juan", SAMPLE_ITEMS)
        service.complete_order(order.id)

        assert len(notifier.sent) == 2
        assert notifier.sent[1]["to"] == "Juan"