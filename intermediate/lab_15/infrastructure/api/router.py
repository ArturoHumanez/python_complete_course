from fastapi import APIRouter, Depends, HTTPException

from intermediate.lab_15.application.dtos import (
    CreateOrderDTO,
    OrderItemDTO,
    OrderResponseDTO,
    UpdateOrderStatusDTO,
)
from intermediate.lab_15.application.use_cases import (
    CancelOrderUseCase,
    CompleteOrderUseCase,
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase,
)
from intermediate.lab_15.domain.exceptions import OrderNotFoundError
from intermediate.lab_15.infrastructure.api.dependencies import (
    get_cancel_order_use_case,
    get_complete_order_use_case,
    get_create_order_use_case,
    get_get_order_use_case,
    get_list_orders_use_case,
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
            OrderItemDTO(
                product=i.product,
                price=i.price,
                quantity=i.quantity,
            )
            for i in order.items
        ],
    )


@router.post("/", response_model=OrderResponseDTO, status_code=201)
def create_order(
    data: CreateOrderDTO,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
):
    items = [item.model_dump() for item in data.items]
    order = use_case.execute(data.customer, items)
    return _to_response(order)


@router.get("/", response_model=list[OrderResponseDTO])
def list_orders(
    status: str | None = None,
    use_case: ListOrdersUseCase = Depends(get_list_orders_use_case),
):
    orders = use_case.execute(status)
    return [_to_response(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponseDTO)
def get_order(
    order_id: int,
    use_case: GetOrderUseCase = Depends(get_get_order_use_case),
):
    try:
        order = use_case.execute(order_id)
        return _to_response(order)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Orden no encontrada")


@router.patch("/{order_id}", response_model=OrderResponseDTO)
def update_order_status(
    order_id: int,
    data: UpdateOrderStatusDTO,
    complete_uc: CompleteOrderUseCase = Depends(get_complete_order_use_case),
    cancel_uc: CancelOrderUseCase = Depends(get_cancel_order_use_case),
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
