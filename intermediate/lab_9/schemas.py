from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product: str
    price: float = Field(gt=0)
    quantity: int = Field(default=1, ge=1)


class OrderCreate(BaseModel):
    customer: str
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    id: int
    product: str
    price: float
    quantity: int

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    customer: str
    status: str
    total: float
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}


class OrderUpdate(BaseModel):
    status: str = Field(pattern="^(pending|completed|cancelled)$")