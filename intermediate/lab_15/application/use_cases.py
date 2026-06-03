from intermediate.lab_15.domain.entities import Order, OrderItem
from intermediate.lab_15.domain.exceptions import OrderNotFoundError
from intermediate.lab_15.domain.ports import NotificationPort, OrderRepository


class CreateOrderUseCase:
    def __init__(self, repo: OrderRepository, notifier: NotificationPort) -> None:
        self._repo = repo
        self._notifier = notifier

    def execute(self, customer: str, items: list[dict]) -> Order:
        order_items = [
            OrderItem(
                product=item["product"],
                price=item["price"],
                quantity=item.get("quantity", 1),
            )
            for item in items
        ]
        order = Order(customer=customer, items=order_items)
        saved = self._repo.save(order)
        self._notifier.send(
            to=customer,
            message=f"Orden #{saved.id} creada por ${saved.total:,.2f}",
        )
        return saved


class CompleteOrderUseCase:
    def __init__(self, repo: OrderRepository, notifier: NotificationPort) -> None:
        self._repo = repo
        self._notifier = notifier

    def execute(self, order_id: int) -> Order:
        order = self._repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        order.complete()
        self._repo.save(order)
        self._notifier.send(
            to=order.customer,
            message=f"Orden #{order.id} completada",
        )
        return order


class CancelOrderUseCase:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def execute(self, order_id: int) -> Order:
        order = self._repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        order.cancel()
        self._repo.save(order)
        return order


class ListOrdersUseCase:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def execute(self, status: str | None = None) -> list[Order]:
        if status:
            return self._repo.find_by_status(status)
        return self._repo.find_all()


class GetOrderUseCase:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def execute(self, order_id: int) -> Order:
        order = self._repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        return order
