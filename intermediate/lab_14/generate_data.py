import csv
import random
from pathlib import Path


def generate_orders(n: int = 500) -> list[dict]:
    """Genera órdenes sintéticas para entrenar el modelo."""
    customers = ["Juan", "María", "Ana", "Pedro", "Lucía", "Carlos"]
    products = {
        "Laptop": 25000,
        "Mouse": 350,
        "Teclado": 800,
        "Monitor": 8500,
        "Webcam": 1200,
        "Audífonos": 600,
        "Cable HDMI": 150,
    }

    orders = []
    for i in range(1, n + 1):
        num_items = random.randint(1, 5)
        selected = random.choices(list(products.items()), k=num_items)
        total = sum(price * random.randint(1, 3) for _, price in selected)
        customer = random.choice(customers)

        # Lógica: órdenes caras o con muchos items tienden a cancelarse más
        cancel_prob = 0.1 + (total / 100000) + (num_items / 20)
        status = "cancelled" if random.random() < cancel_prob else "completed"

        orders.append(
            {
                "id": i,
                "customer": customer,
                "num_items": num_items,
                "total": round(total, 2),
                "has_laptop": any(name == "Laptop" for name, _ in selected),
                "status": status,
            }
        )

    return orders


if __name__ == "__main__":
    output = Path("intermediate/lab_14/orders_dataset.csv")
    orders = generate_orders(500)

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=orders[0].keys())
        writer.writeheader()
        writer.writerows(orders)

    completed = sum(1 for o in orders if o["status"] == "completed")
    print(f"Dataset generado: {len(orders)} órdenes")
    print(f"  Completadas: {completed}")
    print(f"  Canceladas: {len(orders) - completed}")
