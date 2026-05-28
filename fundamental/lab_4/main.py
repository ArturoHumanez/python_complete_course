from dataclasses import dataclass, field
from pydantic import BaseModel, Field, field_validator


# === Entidades de dominio (dataclasses) ===

@dataclass
class OrderItem:
    product: str
    price: float
    quantity: int = 1

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


@dataclass(order=True)
class Order:
    id: int
    customer: str
    items: list[OrderItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)


    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)


    def __str__(self) -> str:
        return (
            f"Order({self.id}, {self.customer}, "
            f"{len(self.items)} items, ${self.total:,.2f})"
        )
        
# === Modelos de entrada/salida (Pydantic) ===

class OrderItemIn(BaseModel):
    product: str
    price: float = Field(gt=0)
    quantity: int = Field(default=1, ge=1)


class OrderIn(BaseModel):
    customer: str
    items: list[OrderItemIn] = Field(min_length=1)

    @field_validator("customer")
    @classmethod
    def customer_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El cliente no puede estar vacío")
        return v.strip()


class OrderOut(BaseModel):
    id: int
    customer: str
    items: list[OrderItemIn]
    total: float
    item_count: int

# === Conversión entre modelos ===

def create_order(id: int, order_in: OrderIn) -> Order:
    """Convierte un OrderIn (Pydantic) a una entidad Order (dataclass)."""
    items = [
        OrderItem(
            product=item.product,
            price=item.price,
            quantity=item.quantity,
        )
        for item in order_in.items
    ]
    return Order(id=id, customer=order_in.customer, items=items)


def order_to_out(order: Order) -> OrderOut:
    """Convierte una entidad Order a OrderOut para respuesta."""
    return OrderOut(
        id=order.id,
        customer=order.customer,
        items=[
            OrderItemIn(product=i.product, price=i.price, quantity=i.quantity)
            for i in order.items
        ],
        total=order.total,
        item_count=order.item_count,
    )
    
if __name__ == "__main__":
    from pydantic import ValidationError
    
    print("=== Creación de órdenes ===")
    raw_data = {
        "customer": "Juan",
        "items": [
            {"product": "Laptop", "price": 25000, "quantity": 1},
            {"product": "Mouse", "price": "350", "quantity": 2},
        ],
    }
    
    order_in = OrderIn(**raw_data)
    order = create_order(id=1, order_in=order_in)
    
    # === price="350" se convirtió a float automáticamente ===
    print(f"Precio del mouse: {order.items[1].price} (tipo: {type(order.items[1].price).__name__})")

    # === Conversión a modelo de salida ===
    print(f"\nJSON de salida:\n{order_to_out(order).model_dump_json(indent=2)}")

    print("\n=== Probando validaciones ===")
    bad_cases = [
        {"customer": "", "items": [{"product": "X", "price": 100}]},
        {"customer": "Ana", "items": [{"product": "X", "price": -5}]},
        {"customer": "Ana", "items": []},
    ]
    
    for i, bad in enumerate(bad_cases, 1):
        try:
            OrderIn(**bad)
            print(f"  Caso {i}: pasó (¿inesperado?)")
        except ValidationError as e:
            print(f"  Caso {i}: {e.error_count()} error(es) — {e.errors()[0]['msg']}")