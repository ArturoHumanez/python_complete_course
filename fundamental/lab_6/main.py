import csv
import json
import logging
from datetime import datetime
from pathlib import Path

# === Configuración de logging ===
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def load_orders_csv(filepath: Path) -> list[dict]:
    """Lee un CSV de órdenes y convierte tipos."""
    if not filepath.exists():
        logger.error("Archivo no encontrado: %s", filepath)
        return []

    orders = []
    with filepath.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                order = {
                    "id": int(row["id"]),
                    "customer": row["customer"],
                    "product": row["product"],
                    "price": float(row["price"]),
                    "quantity": int(row["quantity"]),
                    "status": row["status"],
                    "date": datetime.strptime(row["date"], "%Y-%m-%d"),
                    "subtotal": float(row["price"]) * int(row["quantity"]),
                }
                orders.append(order)
            except (ValueError, KeyError) as e:
                logger.warning("Fila inválida ignorada: %s — %s", row, e)

    logger.info("Se cargaron %d órdenes desde %s", len(orders), filepath.name)
    return orders


def calculate_metrics(orders: list[dict]) -> dict:
    """Calcula métricas de las órdenes completadas."""
    completed = [o for o in orders if o["status"] == "completed"]
    logger.debug("Órdenes completadas: %d de %d", len(completed), len(orders))

    if not completed:
        logger.warning("No hay órdenes completadas para calcular métricas")
        return {}

    # Total por cliente
    by_customer: dict[str, float] = {}
    for order in completed:
        customer = order["customer"]
        by_customer[customer] = by_customer.get(customer, 0.0) + order["subtotal"]

    # Producto más vendido (por cantidad)
    by_product: dict[str, int] = {}
    for order in completed:
        product = order["product"]
        by_product[product] = by_product.get(product, 0) + order["quantity"]

    top_product = max(by_product, key=by_product.get)

    # Resumen general
    totals = [o["subtotal"] for o in completed]
    metrics = {
        "total_orders": len(completed),
        "total_revenue": sum(totals),
        "average_order": sum(totals) / len(totals),
        "top_product": top_product,
        "by_customer": by_customer,
        "by_product": by_product,
    }

    logger.info("Métricas calculadas — revenue total: $%.2f", metrics["total_revenue"])
    return metrics

def export_to_json(data: dict, filepath: Path) -> None:
    """Exporta datos a JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    logger.info("Métricas exportadas a %s", filepath)
    
    
if __name__ == "__main__":
    logger.info("=== Inicio del procesamiento ===")

    csv_path = Path("fundamental/lab_6/orders.csv")
    output_path = Path("fundamental/lab_6/metrics.json")

    orders = load_orders_csv(csv_path)

    if orders:
        metrics = calculate_metrics(orders)
        export_to_json(metrics, output_path)

        print("\n--- Resumen ---")
        print(f"Órdenes procesadas: {metrics['total_orders']}")
        print(f"Revenue total: ${metrics['total_revenue']:,.2f}")
        print(f"Ticket promedio: ${metrics['average_order']:,.2f}")
        print(f"Producto estrella: {metrics['top_product']}")

    logger.info("=== Fin del procesamiento ===")