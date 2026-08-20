from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True, nullable=False)

    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_sp: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/paid/shipped/delivered/cancelled
    payment_status: Mapped[str] = mapped_column(String(20), default="unpaid")
    address: Mapped[str | None] = mapped_column(String(400))

    member = relationship("Member")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    sp: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
