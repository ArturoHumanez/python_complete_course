from datetime import datetime

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), default=None)  # ← nuevo

    orders: Mapped[list["Order"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, name='{self.name}')"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def __repr__(self) -> str:
        return (
            f"Order(id={self.id}, user='{self.user_id}', "
            f"status='{self.status}')"
        )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product: Mapped[str] = mapped_column(String(200))
    price: Mapped[float]
    quantity: Mapped[int] = mapped_column(default=1)

    order: Mapped["Order"] = relationship(back_populates="items")

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

    def __repr__(self) -> str:
        return f"OrderItem('{self.product}', ${self.price} x{self.quantity})"