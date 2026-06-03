class OrderNotFoundError(Exception):
    def __init__(self, order_id: int) -> None:
        self.order_id = order_id
        super().__init__(f"Orden {order_id} no encontrada")


class InvalidOrderError(Exception):
    pass
