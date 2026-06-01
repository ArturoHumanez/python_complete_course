import pytest

from intermediate.lab_15.application.use_cases import (
    CompleteOrderUseCase,
    CreateOrderUseCase,
    ListOrdersUseCase,
)
from intermediate.lab_15.domain.exceptions import OrderNotFoundError
from intermediate.lab_15.infrastructure.adapters.http_notifier import FakeNotifier
from intermediate.lab_15.infrastructure.adapters.memory_repo import (
    InMemoryOrderRepository,
)

SAMPLE_ITEMS = [
    {"product": "Laptop", "price": 25000, "quantity": 1},
    {"product": "Mouse", "price": 350, "quantity": 2},
]


@pytest.fixture
def repo():
    return InMemoryOrderRepository()


@pytest.fixture
def notifier():
    return FakeNotifier()


class TestCreateOrder:
    def test_creates_with_pending_status(self, repo, notifier):
        uc = CreateOrderUseCase(repo=repo, notifier=notifier)
        order = uc.execute("Juan", SAMPLE_ITEMS)

        assert order.id is not None
        assert order.status == "pending"
        assert order.total == 25700

    def test_sends_notification(self, repo, notifier):
        uc = CreateOrderUseCase(repo=repo, notifier=notifier)
        uc.execute("Juan", SAMPLE_ITEMS)

        assert len(notifier.sent) == 1
        assert notifier.sent[0]["to"] == "Juan"

    def test_persists_in_repo(self, repo, notifier):
        uc = CreateOrderUseCase(repo=repo, notifier=notifier)
        order = uc.execute("Juan", SAMPLE_ITEMS)

        found = repo.find_by_id(order.id)
        assert found is not None
        assert found.customer == "Juan"


class TestCompleteOrder:
    def test_completes_order(self, repo, notifier):
        create_uc = CreateOrderUseCase(repo=repo, notifier=notifier)
        order = create_uc.execute("Juan", SAMPLE_ITEMS)

        complete_uc = CompleteOrderUseCase(repo=repo, notifier=notifier)
        completed = complete_uc.execute(order.id)

        assert completed.status == "completed"

    def test_not_found_raises(self, repo, notifier):
        uc = CompleteOrderUseCase(repo=repo, notifier=notifier)

        with pytest.raises(OrderNotFoundError):
            uc.execute(999)


class TestListOrders:
    def test_filter_by_status(self, repo, notifier):
        create_uc = CreateOrderUseCase(repo=repo, notifier=notifier)
        order1 = create_uc.execute("Juan", SAMPLE_ITEMS)
        create_uc.execute("María", SAMPLE_ITEMS)

        complete_uc = CompleteOrderUseCase(repo=repo, notifier=notifier)
        complete_uc.execute(order1.id)

        list_uc = ListOrdersUseCase(repo=repo)

        completed = list_uc.execute(status="completed")
        assert len(completed) == 1
        assert completed[0].customer == "Juan"

        pending = list_uc.execute(status="pending")
        assert len(pending) == 1