from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from intermediate.lab_8.models import Order, OrderItem, User
from intermediate.lab_9.database import get_db
from intermediate.lab_9.schemas import (
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    OrderUpdate,
)
from intermediate.lab_9.auth import verify_token


router = APIRouter(prefix="/orders", tags=["Orders"])


def _get_or_create_user(db: Session, customer: str) -> User:
    """Busca un usuario por nombre o lo crea."""
    stmt = select(User).where(User.name == customer)
    user = db.scalars(stmt).first()
    if not user:
        user = User(name=customer, email=f"{customer.lower()}@example.com")
        db.add(user)
        db.flush()
    return user


def _order_to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer=order.user.name,
        status=order.status,
        total=order.total,
        items=[
            OrderItemResponse.model_validate(item) for item in order.items
        ],
    )


@router.get("/", response_model=list[OrderResponse])
def list_orders(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    """Lista todas las órdenes, con filtro opcional por status."""
    stmt = select(Order)
    if status:
        stmt = stmt.where(Order.status == status)
    orders = list(db.scalars(stmt))
    return [_order_to_response(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Obtiene una orden por ID."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return _order_to_response(order)


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    """Crea una nueva orden."""
    user = _get_or_create_user(db, data.customer)
    order = Order(
        user=user,
        status="pending",
        items=[
            OrderItem(
                product=item.product,
                price=item.price,
                quantity=item.quantity,
            )
            for item in data.items
        ],
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return _order_to_response(order)


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    data: OrderUpdate,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Actualiza el status de una orden."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    order.status = data.status
    db.commit()
    db.refresh(order)
    return _order_to_response(order)


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    """Elimina una orden."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    db.delete(order)
    db.commit()