from intermediate.lab_15.application.use_cases import (
    CancelOrderUseCase,
    CompleteOrderUseCase,
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase,
)
from intermediate.lab_15.infrastructure.adapters.http_notifier import LogNotifier
from intermediate.lab_15.infrastructure.adapters.memory_repo import (
    InMemoryOrderRepository,
)

# === Wiring: aquí se decide qué implementaciones usar ===

_repo = InMemoryOrderRepository()
_notifier = LogNotifier()


def get_create_order_use_case() -> CreateOrderUseCase:
    return CreateOrderUseCase(repo=_repo, notifier=_notifier)


def get_complete_order_use_case() -> CompleteOrderUseCase:
    return CompleteOrderUseCase(repo=_repo, notifier=_notifier)


def get_cancel_order_use_case() -> CancelOrderUseCase:
    return CancelOrderUseCase(repo=_repo)


def get_list_orders_use_case() -> ListOrdersUseCase:
    return ListOrdersUseCase(repo=_repo)


def get_get_order_use_case() -> GetOrderUseCase:
    return GetOrderUseCase(repo=_repo)
