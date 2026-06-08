import logging
from concurrent import futures

import grpc

from advance.lab_19 import orders_pb2, orders_pb2_grpc

logger = logging.getLogger(__name__)

# Datos en memoria para el ejemplo
ORDERS_DB: dict[int, dict] = {
    1: {
        "id": 1,
        "customer": "Juan",
        "status": "completed",
        "items": [
            {"product": "Laptop", "price": 25000, "quantity": 1, "subtotal": 25000},
            {"product": "Mouse", "price": 350, "quantity": 2, "subtotal": 700},
        ],
    },
    2: {
        "id": 2,
        "customer": "Maria",
        "status": "pending",
        "items": [
            {"product": "Teclado", "price": 800, "quantity": 1, "subtotal": 800},
        ],
    },
}

NEXT_ID = 3


class OrderServiceServicer(orders_pb2_grpc.OrderServiceServicer):
    def GetOrder(self, request, context):
        order = ORDERS_DB.get(request.order_id)
        if not order:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Orden {request.order_id} no encontrada")
            return orders_pb2.OrderResponse()
        return self._to_response(order)

    def ListOrders(self, request, context):
        orders = ORDERS_DB.values()
        if request.status:
            orders = [o for o in orders if o["status"] == request.status]
        return orders_pb2.ListOrdersResponse(
            orders=[self._to_response(o) for o in orders]
        )

    def CreateOrder(self, request, context):
        global NEXT_ID
        items = [
            {
                "product": item.product,
                "price": item.price,
                "quantity": item.quantity,
                "subtotal": item.price * item.quantity,
            }
            for item in request.items
        ]
        order = {
            "id": NEXT_ID,
            "customer": request.customer,
            "status": "pending",
            "items": items,
        }
        ORDERS_DB[NEXT_ID] = order
        NEXT_ID += 1
        logger.info("Orden #%d creada via gRPC", order["id"])
        return self._to_response(order)

    def _to_response(self, order: dict) -> orders_pb2.OrderResponse:
        items = [
            orders_pb2.OrderItem(
                product=i["product"],
                price=i["price"],
                quantity=i["quantity"],
                subtotal=i["subtotal"],
            )
            for i in order["items"]
        ]
        total = sum(i["subtotal"] for i in order["items"])
        return orders_pb2.OrderResponse(
            id=order["id"],
            customer=order["customer"],
            status=order["status"],
            total=total,
            item_count=sum(i["quantity"] for i in order["items"]),
            items=items,
        )


def serve():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrderServiceServicer_to_server(OrderServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    logger.info("Servidor gRPC corriendo en puerto 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
