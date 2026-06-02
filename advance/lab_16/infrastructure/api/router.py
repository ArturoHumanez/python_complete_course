from fastapi import APIRouter, Depends, HTTPException

from advance.lab_16.application.dtos import (
    CreateOrderDTO,
    OrderItemDTO,
    OrderResponseDTO,
    UpdateOrderStatusDTO,
)
from advance.lab_16.application.use_cases import (
    CancelOrderUseCase,
    CompleteOrderUseCase,
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase,
)
from advance.lab_16.domain.exceptions import OrderNotFoundError
from advance.lab_16.infrastructure.api.dependencies import (
    get_cancel_order_uc,
    get_complete_order_uc,
    get_create_order_uc,
    get_get_order_uc,
    get_list_orders_uc,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


def _to_response(order) -> OrderResponseDTO:
    return OrderResponseDTO(
        id=order.id,
        customer=order.customer,
        status=order.status,
        total=order.total,
        item_count=order.item_count,
        items=[
            OrderItemDTO(product=i.product, price=i.price, quantity=i.quantity)
            for i in order.items
        ],
    )


@router.post("/", response_model=OrderResponseDTO, status_code=201)
def create_order(
    data: CreateOrderDTO,
    uc: CreateOrderUseCase = Depends(get_create_order_uc),
):
    items = [item.model_dump() for item in data.items]
    order = uc.execute(data.customer, items)
    return _to_response(order)


@router.get("/", response_model=list[OrderResponseDTO])
def list_orders(
    status: str | None = None,
    uc: ListOrdersUseCase = Depends(get_list_orders_uc),
):
    orders = uc.execute(status)
    return [_to_response(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponseDTO)
def get_order(
    order_id: int,
    uc: GetOrderUseCase = Depends(get_get_order_uc),
):
    try:
        return _to_response(uc.execute(order_id))
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Orden no encontrada")


@router.patch("/{order_id}", response_model=OrderResponseDTO)
def update_status(
    order_id: int,
    data: UpdateOrderStatusDTO,
    complete_uc: CompleteOrderUseCase = Depends(get_complete_order_uc),
    cancel_uc: CancelOrderUseCase = Depends(get_cancel_order_uc),
):
    try:
        if data.status == "completed":
            order = complete_uc.execute(order_id)
        else:
            order = cancel_uc.execute(order_id)
        return _to_response(order)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))