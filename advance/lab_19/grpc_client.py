import logging

import grpc

from advance.lab_19 import orders_pb2, orders_pb2_grpc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = orders_pb2_grpc.OrderServiceStub(channel)

    # === Listar órdenes ===
    print("=== Listar todas las órdenes ===")
    response = stub.ListOrders(orders_pb2.ListOrdersRequest())
    for order in response.orders:
        print(
            f"  Orden #{order.id}: {order.customer} — ${order.total:,.2f} ({order.status})"
        )

    # === Obtener una orden ===
    print("\n=== Obtener orden #1 ===")
    order = stub.GetOrder(orders_pb2.GetOrderRequest(order_id=1))
    print(f"  Cliente: {order.customer}")
    print(f"  Status: {order.status}")
    print(f"  Total: ${order.total:,.2f}")
    for item in order.items:
        print(f"    - {item.product} x{item.quantity} = ${item.subtotal:,.2f}")

    # === Crear orden ===
    print("\n=== Crear nueva orden ===")
    new_order = stub.CreateOrder(
        orders_pb2.CreateOrderRequest(
            customer="Pedro",
            items=[
                orders_pb2.OrderItem(product="Monitor", price=8500, quantity=1),
                orders_pb2.OrderItem(product="Cable HDMI", price=150, quantity=3),
            ],
        )
    )
    print(f"  Orden #{new_order.id} creada: ${new_order.total:,.2f}")

    # === Listar de nuevo ===
    print("\n=== Listar después de crear ===")
    response = stub.ListOrders(orders_pb2.ListOrdersRequest())
    for order in response.orders:
        print(
            f"  Orden #{order.id}: {order.customer} — ${order.total:,.2f} ({order.status})"
        )

    # === Filtrar por status ===
    print("\n=== Solo pendientes ===")
    response = stub.ListOrders(orders_pb2.ListOrdersRequest(status="pending"))
    for order in response.orders:
        print(f"  Orden #{order.id}: {order.customer} — ${order.total:,.2f}")

    # === Orden no encontrada ===
    print("\n=== Buscar orden inexistente ===")
    try:
        stub.GetOrder(orders_pb2.GetOrderRequest(order_id=999))
    except grpc.RpcError as e:
        print(f"  Error: {e.code().name} — {e.details()}")


if __name__ == "__main__":
    run()
