from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    products = relationship("Product", back_populates="category")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), index=True)
    category = relationship("Category", back_populates="products")

    mrp: Mapped[float] = mapped_column(Numeric(12, 2), default=0)       # retail price
    price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)     # DP = distributor/discount price (base)
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # company product cost
    sp: Mapped[float] = mapped_column(Numeric(10, 2), default=0)        # selling points / BV (1 SP = ₹10)
    stock: Mapped[int] = mapped_column(Integer, default=0)

    image: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_offer: Mapped[bool] = mapped_column(Boolean, default=False)      # "Offer Products"
