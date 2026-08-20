from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CartItemIn(BaseModel):
    product_id: int
    quantity: int = 1


class OrderIn(BaseModel):
    items: list[CartItemIn]
    address: str | None = None


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    price: float
    sp: float
    quantity: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    subtotal: float
    total: float
    total_sp: float
    status: str
    payment_status: str
    created_at: datetime
    items: list[OrderItemOut] = []
