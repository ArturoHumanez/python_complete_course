import logging

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from intermediate.lab_8.models import Base, Order, OrderItem, User

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_tables(engine) -> None:
    """Crea todas las tablas en la base de datos."""
    Base.metadata.create_all(engine)
    logger.info("Tablas creadas")


# === CRUD Operations ===


def create_user(session: Session, name: str, email: str) -> User:
    user = User(name=name, email=email)
    session.add(user)
    session.flush()  # genera el ID sin hacer commit todavía
    logger.info("Usuario creado: %s", user)
    return user


def create_order(session: Session, user: User, items: list[dict]) -> Order:
    order = Order(
        user=user,
        status="pending",
        items=[
            OrderItem(
                product=item["product"],
                price=item["price"],
                quantity=item.get("quantity", 1),
            )
            for item in items
        ],
    )
    session.add(order)
    session.flush()
    logger.info("Orden creada: %s — total: $%.2f", order, order.total)
    return order


def get_user_orders(session: Session, user_id: int) -> list[Order]:
    stmt = select(Order).where(Order.user_id == user_id)
    return list(session.scalars(stmt))


def update_order_status(session: Session, order_id: int, status: str) -> Order | None:
    order = session.get(Order, order_id)
    if order:
        order.status = status
        logger.info("Orden %d actualizada a '%s'", order_id, status)
    return order


def delete_order(session: Session, order_id: int) -> bool:
    order = session.get(Order, order_id)
    if order:
        session.delete(order)
        logger.info("Orden %d eliminada (con %d items)", order_id, len(order.items))
        return True
    return False


if __name__ == "__main__":
    # SQLite en memoria — perfecto para pruebas
    engine = create_engine("sqlite:///:memory:", echo=False)
    create_tables(engine)

    with Session(engine) as session:
        with session.begin():  # transacción automática
            # === Create ===
            print("\n=== Creando datos ===")
            juan = create_user(session, "Juan", "juan@mail.com")
            maria = create_user(session, "María", "maria@mail.com")

            order1 = create_order(
                session,
                juan,
                [
                    {"product": "Laptop", "price": 25000, "quantity": 1},
                    {"product": "Mouse", "price": 350, "quantity": 2},
                ],
            )
            order2 = create_order(
                session,
                juan,
                [
                    {"product": "Monitor", "price": 8500, "quantity": 1},
                ],
            )
            order3 = create_order(
                session,
                maria,
                [
                    {"product": "Teclado", "price": 800, "quantity": 1},
                    {"product": "Webcam", "price": 1200, "quantity": 1},
                ],
            )

        # === Read ===
        print("\n=== Leyendo datos ===")
        with session.begin():
            juan_orders = get_user_orders(session, juan.id)
            print(f"Órdenes de Juan: {len(juan_orders)}")
            for order in juan_orders:
                print(f"  {order} — total: ${order.total:,.2f}")
                for item in order.items:
                    print(f"    {item}")

        # === Update ===
        print("\n=== Actualizando ===")
        with session.begin():
            update_order_status(session, order1.id, "completed")
            update_order_status(session, order3.id, "completed")

        # === Verificar ===
        print("\n=== Estado actual ===")
        with session.begin():
            all_orders = list(session.scalars(select(Order)))
            for order in all_orders:
                print(f"  {order.user.name} — {order} — ${order.total:,.2f}")

        # === Delete ===
        print("\n=== Eliminando ===")
        with session.begin():
            delete_order(session, order2.id)

        # Verificar que se eliminó con sus items
        with session.begin():
            remaining = list(session.scalars(select(Order)))
            print(f"\nÓrdenes restantes: {len(remaining)}")
            for order in remaining:
                print(f"  {order}")

    print("\n✓ Lab 8 completo — CRUD con SQLAlchemy")
