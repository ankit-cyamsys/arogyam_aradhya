from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_member
from app.core.database import get_db
from app.models import Member, Order, OrderItem, Product
from app.schemas import OrderIn, OrderOut
from app.services import settings_service as cfg
from app.services.ids import generate_order_no
from app.services.mlm_engine import process_order

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def my_orders(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    return (
        db.execute(
            select(Order)
            .where(Order.member_id == member.id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
        .scalars()
        .all()
    )


@router.post("", response_model=OrderOut)
def place_order(
    payload: OrderIn,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = Order(
        order_no=generate_order_no(db),
        member_id=member.id,
        address=payload.address or member.address,
    )
    subtotal = Decimal("0")
    total_sp = Decimal("0")

    for line in payload.items:
        product = db.get(Product, line.product_id)
        if product is None or not product.is_active:
            raise HTTPException(status_code=404, detail=f"Product {line.product_id} unavailable")
        qty = max(1, line.quantity)
        price = Decimal(str(product.price))
        sp = Decimal(str(product.sp))
        subtotal += price * qty
        total_sp += sp * qty
        order.items.append(
            OrderItem(product_id=product.id, name=product.name, price=price, sp=sp, quantity=qty)
        )

    # GST: subtotal is the taxable value (DP). Add GST on top when prices are
    # GST-exclusive; when inclusive, the tax is already inside the price.
    gst_rate = Decimal(str(cfg.get(db, "gst_rate", 18)))
    inclusive = bool(cfg.get(db, "price_gst_inclusive", False))
    order.subtotal = subtotal
    if inclusive:
        order.total = subtotal
    else:
        order.total = (subtotal * (Decimal("1") + gst_rate / Decimal("100"))).quantize(Decimal("0.01"))
    order.total_sp = total_sp
    # Demo flow: mark paid immediately so commissions flow. Wire a real gateway later.
    order.status = "paid"
    order.payment_status = "paid"

    db.add(order)
    db.commit()
    db.refresh(order)

    process_order(db, order)
    db.refresh(order)
    return order


@router.get("/{order_id}/invoice")
def order_invoice(
    order_id: int,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    order = (
        db.execute(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        ).scalar_one_or_none()
    )
    if order is None or order.member_id != member.id:
        raise HTTPException(status_code=404, detail="Order not found")
    from app.services.invoice import build_invoice
    return build_invoice(db, order)
