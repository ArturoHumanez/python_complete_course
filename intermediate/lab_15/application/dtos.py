from pydantic import BaseModel, Field


class OrderItemDTO(BaseModel):
    product: str
    price: float = Field(gt=0)
    quantity: int = Field(default=1, ge=1)


class CreateOrderDTO(BaseModel):
    customer: str
    items: list[OrderItemDTO] = Field(min_length=1)


class UpdateOrderStatusDTO(BaseModel):
    status: str = Field(pattern="^(completed|cancelled)$")


class OrderResponseDTO(BaseModel):
    id: int
    customer: str
    status: str
    total: float
    item_count: int
    items: list[OrderItemDTO]

    model_config = {"from_attributes": True}
