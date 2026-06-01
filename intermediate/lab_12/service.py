from intermediate.lab_12.ports import NotificationPort, Order, OrderRepository


class OrderService:
    """Servicio que depende de puertos, no de implementaciones."""

    def __init__(
        self,
        repo: OrderRepository,
        notifier: NotificationPort,
    ) -> None:
        self._repo = repo
        self._notifier = notifier

    def create_order(self, customer: str, items: list[dict]) -> Order:
        order = Order(customer=customer, items=items)
        saved = self._repo.save(order)
        self._notifier.send(
            to=customer,
            message=f"Tu orden #{saved.id} por ${saved.total:,.2f} fue creada",
        )
        return saved

    def complete_order(self, order_id: int) -> Order:
        order = self._repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"Orden {order_id} no encontrada")
        order.status = "completed"
        self._repo.save(order)
        self._notifier.send(
            to=order.customer,
            message=f"Tu orden #{order.id} fue completada",
        )
        return order

    def get_completed_orders(self) -> list[Order]:
        return self._repo.find_by_status("completed")