from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    category_id: int | None = None
    mrp: float
    price: float
    cost_price: float = 0
    sp: float
    stock: int
    image: str | None = None
    is_active: bool
    is_offer: bool


class ProductIn(BaseModel):
    name: str
    description: str | None = None
    category_id: int | None = None
    mrp: float = 0
    price: float = 0
    cost_price: float = 0
    sp: float = 0
    stock: int = 0
    image: str | None = None
    is_active: bool = True
    is_offer: bool = False
