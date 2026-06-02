from advance.lab_16.application.event_handlers import create_event_bus
from advance.lab_16.application.use_cases import (
    CancelOrderUseCase,
    CompleteOrderUseCase,
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase,
)
from advance.lab_16.infrastructure.adapters.memory_repo import (
    InMemoryOrderRepository,
)
from advance.lab_16.infrastructure.adapters.memory_uow import InMemoryUnitOfWork

# === Wiring ===

_repo = InMemoryOrderRepository()
_uow = InMemoryUnitOfWork(repo=_repo)
_event_bus = create_event_bus()


def get_create_order_uc() -> CreateOrderUseCase:
    return CreateOrderUseCase(uow=_uow, publisher=_event_bus)


def get_complete_order_uc() -> CompleteOrderUseCase:
    return CompleteOrderUseCase(uow=_uow, publisher=_event_bus)


def get_cancel_order_uc() -> CancelOrderUseCase:
    return CancelOrderUseCase(uow=_uow, publisher=_event_bus)


def get_list_orders_uc() -> ListOrdersUseCase:
    return ListOrdersUseCase(uow=_uow)


def get_get_order_uc() -> GetOrderUseCase:
    return GetOrderUseCase(uow=_uow)