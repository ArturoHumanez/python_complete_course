import json
from pathlib import Path


def load_orders(filepath: str) -> list[dict]:
    """Lee un archivo JSON y devuelve la lista de órdenes."""
    path = Path(filepath)
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{filepath}'")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: El archivo no es JSON válido — {e}")
        return []

    if not isinstance(data, list):
        print("Error: Se esperaba una lista de órdenes")
        return []

    return data


def calculate_order_total(order: dict) -> float:
    """Calcula el total de una orden, manejando datos inválidos."""
    total = 0.0
    for item in order.get("items", []):
        try:
            total += item["price"] * item["quantity"]
        except TypeError:
            print(
                f"  ⚠ Orden {order['id']}: precio inválido "
                f"en '{item.get('product', '?')}', se omite"
            )
        except KeyError as e:
            print(f"  ⚠ Orden {order['id']}: falta el campo {e}")
    return total


def filter_orders_by_status(orders: list[dict], status: str) -> list[dict]:
    """Filtra órdenes por estatus."""
    return [order for order in orders if order.get("status") == status]


def summarize_by_customer(orders: list[dict]) -> dict[str, float]:
    """Agrupa el total gastado por cada cliente."""
    summary: dict[str, float] = {}
    for order in orders:
        customer = order.get("customer", "Desconocido")
        total = calculate_order_total(order)
        summary[customer] = summary.get(customer, 0.0) + total
    return summary


def process_order(order: dict) -> str:
    """Clasifica una orden usando pattern matching."""
    match order:
        case {"status": "completed", "items": [_, _, *_]}:
            return f"Orden {order['id']}: completada con múltiples productos"
        case {"status": "completed", "items": [single]}:
            return f"Orden {order['id']}: completada — solo '{single['product']}'"
        case {"status": "pending"}:
            return f"Orden {order['id']}: pendiente de procesar"
        case {"status": "cancelled", "items": []}:
            return f"Orden {order['id']}: cancelada (sin productos)"
        case _:
            return f"Orden {order['id']}: caso no contemplado"


if __name__ == "__main__":
    # Caso bien
    orders = load_orders("fundamental/lab_2/orders.json")

    # Caso archivo no existe
    # orders = load_orders("fundamental/lab_2/orders2.json")
    print(f"Se cargaron {len(orders)} órdenes")

    # Filtrar solo las completadas
    completed = filter_orders_by_status(orders, "completed")
    print(f"Órdenes completadas: {len(completed)}")

    for order in completed:
        total = calculate_order_total(order)
        print(f"  Orden {order['id']} — {order['customer']}: ${total:,.2f}")

    # Resumen por cliente (solo completadas)
    print("\nResumen por cliente:")
    summary = summarize_by_customer(completed)
    for customer, total in summary.items():
        print(f"  {customer}: ${total:,.2f}")

    # Usar un set para ver clientes únicos de TODAS las órdenes
    all_customers = {order.get("customer", "?") for order in orders}
    print(f"\nClientes únicos en total: {all_customers}")

    # Pattern matching
    print("\nClasificación de órdenes:")
    for order in orders:
        print(f"  {process_order(order)}")
