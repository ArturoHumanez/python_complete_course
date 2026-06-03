import pytest

from advance.lab_16.application.event_handlers import EventBus
from advance.lab_16.application.use_cases import (
    CancelOrderUseCase,
    CompleteOrderUseCase,
    CreateOrderUseCase,
    ListOrdersUseCase,
)
from advance.lab_16.domain.events import OrderCancelled, OrderCompleted, OrderCreated
from advance.lab_16.domain.exceptions import OrderNotFoundError
from advance.lab_16.infrastructure.adapters.memory_repo import InMemoryOrderRepository
from advance.lab_16.infrastructure.adapters.memory_uow import InMemoryUnitOfWork

SAMPLE_ITEMS = [
    {"product": "Laptop", "price": 25000, "quantity": 1},
    {"product": "Mouse", "price": 350, "quantity": 2},
]


@pytest.fixture
def repo():
    return InMemoryOrderRepository()


@pytest.fixture
def uow(repo):
    return InMemoryUnitOfWork(repo=repo)


@pytest.fixture
def captured_events():
    return []


@pytest.fixture
def event_bus(captured_events):
    bus = EventBus()
    bus.register(OrderCreated, lambda e: captured_events.append(e))
    bus.register(OrderCompleted, lambda e: captured_events.append(e))
    bus.register(OrderCancelled, lambda e: captured_events.append(e))
    return bus


class TestCreateOrder:
    def test_creates_pending_order(self, uow, event_bus):
        uc = CreateOrderUseCase(uow=uow, publisher=event_bus)
        order = uc.execute("Juan", SAMPLE_ITEMS)

        assert order.id is not None
        assert order.status == "pending"
        assert order.total == 25700

    def test_emits_created_event(self, uow, event_bus, captured_events):
        uc = CreateOrderUseCase(uow=uow, publisher=event_bus)
        uc.execute("Juan", SAMPLE_ITEMS)

        assert len(captured_events) == 1
        assert isinstance(captured_events[0], OrderCreated)
        assert captured_events[0].customer == "Juan"


class TestCompleteOrder:
    def test_completes_order(self, uow, event_bus):
        create_uc = CreateOrderUseCase(uow=uow, publisher=event_bus)
        order = create_uc.execute("Juan", SAMPLE_ITEMS)

        complete_uc = CompleteOrderUseCase(uow=uow, publisher=event_bus)
        completed = complete_uc.execute(order.id)

        assert completed.status == "completed"

    def test_emits_completed_event(self, uow, event_bus, captured_events):
        create_uc = CreateOrderUseCase(uow=uow, publisher=event_bus)
        order = create_uc.execute("Juan", SAMPLE_ITEMS)

        complete_uc = CompleteOrderUseCase(uow=uow, publisher=event_bus)
        complete_uc.execute(order.id)

        assert any(isinstance(e, OrderCompleted) for e in captured_events)

    def test_cannot_complete_cancelled(self, uow, event_bus):
        create_uc = CreateOrderUseCase(uow=uow, publisher=event_bus)
        order = create_uc.execute("Juan", SAMPLE_ITEMS)

        cancel_uc = CancelOrderUseCase(uow=uow, publisher=event_bus)
        cancel_uc.execute(order.id)

        complete_uc = CompleteOrderUseCase(uow=uow, publisher=event_bus)
        with pytest.raises(ValueError, match="cancelada"):
            complete_uc.execute(order.id)


class TestCancelOrder:
    def test_not_found_raises(self, uow, event_bus):
        uc = CancelOrderUseCase(uow=uow, publisher=event_bus)
        with pytest.raises(OrderNotFoundError):
            uc.execute(999)


class TestListOrders:
    def test_filter_by_status(self, uow, event_bus):
        create_uc = CreateOrderUseCase(uow=uow, publisher=event_bus)
        order1 = create_uc.execute("Juan", SAMPLE_ITEMS)
        create_uc.execute("María", SAMPLE_ITEMS)

        complete_uc = CompleteOrderUseCase(uow=uow, publisher=event_bus)
        complete_uc.execute(order1.id)

        list_uc = ListOrdersUseCase(uow=uow)
        completed = list_uc.execute(status="completed")

        assert len(completed) == 1
        assert completed[0].customer == "Juan"
