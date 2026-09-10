from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models import (
    AdminUser,
    Member,
    Order,
    Product,
    Category,
    PayoutRequest,
)
from app.schemas import ProductIn, ProductOut, SettingUpdate
from app.services import settings_service as cfg
from app.services import ranks as ranks_svc
from app.services.mlm_engine import close_payout_period, pay_due_rank_bonuses, process_order
from app.utils.text import slugify

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    members = db.execute(select(func.count(Member.id))).scalar_one()
    active = db.execute(select(func.count(Member.id)).where(Member.is_active.is_(True))).scalar_one()
    orders = db.execute(select(func.count(Order.id))).scalar_one()
    pending_orders = db.execute(
        select(func.count(Order.id)).where(Order.payment_status == "unpaid", Order.status != "cancelled")
    ).scalar_one()
    revenue = db.execute(
        select(func.coalesce(func.sum(Order.total), 0)).where(Order.payment_status == "paid")
    ).scalar_one()
    pending_payouts = db.execute(
        select(func.count(PayoutRequest.id)).where(PayoutRequest.status == "pending")
    ).scalar_one()
    return {
        "members": members,
        "active_members": active,
        "orders": orders,
        "pending_orders": pending_orders,
        "revenue": float(revenue),
        "pending_payouts": pending_payouts,
    }


# ---- Members ----
@router.get("/members")
def list_members(q: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Member)
    if q:
        stmt = stmt.where(Member.name.ilike(f"%{q}%") | Member.member_id.ilike(f"%{q}%"))
    rows = db.execute(stmt.order_by(Member.created_at.desc()).limit(500)).scalars().all()
    return [
        {
            "member_id": m.member_id,
            "segment": m.segment,
            "name": m.name,
            "phone": m.phone,
            "is_active": m.is_active,
            "is_blocked": m.is_blocked,
            "wallet_balance": float(m.wallet_balance or 0),
            "total_earned": float(m.total_earned or 0),
            "rank_level": m.rank_level or 0,
            "rank_bonus_paid_level": m.rank_bonus_paid_level or 0,
        }
        for m in rows
    ]


@router.get("/members/{member_id}/kyc")
def member_kyc(member_id: str, db: Session = Depends(get_db)):
    from app.services import kyc as kyc_svc
    m = db.execute(select(Member).where(Member.member_id == member_id)).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return {
        "member": {"member_id": m.member_id, "name": m.name, "phone": m.phone,
                   "pan": m.pan, "aadhaar": m.aadhaar, "bank_name": m.bank_name,
                   "bank_account": m.bank_account, "bank_ifsc": m.bank_ifsc,
                   "address": m.address, "is_active": m.is_active},
        "documents": kyc_svc.list_status(db, m.id),
    }


@router.get("/members/{member_id}/kyc/{doc_type}/file")
def member_kyc_file(member_id: str, doc_type: str, db: Session = Depends(get_db)):
    from fastapi.responses import Response
    from app.services import kyc as kyc_svc
    m = db.execute(select(Member).where(Member.member_id == member_id)).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Member not found")
    doc = kyc_svc.get_document(db, m.id, doc_type)
    return Response(content=doc.data, media_type=doc.content_type)


@router.post("/members/{member_id}/block")
def toggle_block(member_id: str, db: Session = Depends(get_db)):
    m = db.execute(select(Member).where(Member.member_id == member_id)).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Member not found")
    m.is_blocked = not m.is_blocked
    db.commit()
    return {"member_id": m.member_id, "is_blocked": m.is_blocked}


@router.post("/members/{member_id}/reset-password")
def reset_member_password(member_id: str, new_password: str, db: Session = Depends(get_db)):
    from app.core.security import hash_password
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    m = db.execute(select(Member).where(Member.member_id == member_id)).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Member not found")
    m.password_hash = hash_password(new_password)
    db.commit()
    return {"ok": True, "member_id": member_id}


# ---- Orders (payment confirmation) ----
@router.get("/orders")
def list_orders(status: str | None = None, db: Session = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    from app.models import Order
    stmt = select(Order).options(selectinload(Order.items))
    if status:
        stmt = stmt.where(Order.status == status)
    rows = db.execute(stmt.order_by(Order.created_at.desc()).limit(500)).scalars().all()
    out = []
    for o in rows:
        m = db.get(Member, o.member_id)
        out.append({
            "id": o.id, "order_no": o.order_no,
            "member_id": m.member_id if m else None, "member_name": m.name if m else None,
            "segment": m.segment if m else None,
            "subtotal": float(o.subtotal), "total": float(o.total), "total_sp": float(o.total_sp),
            "status": o.status, "payment_status": o.payment_status,
            "created_at": o.created_at,
            "items": [{"name": it.name, "qty": it.quantity, "price": float(it.price)} for it in o.items],
        })
    return out


@router.post("/orders/{order_id}/confirm")
def confirm_order(order_id: int, db: Session = Depends(get_db)):
    """Confirm payment received → process SP, commissions and activation (once)."""
    from app.models import Order
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Order already confirmed")
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Order is cancelled")
    order.status = "paid"
    order.payment_status = "paid"
    db.commit()
    process_order(db, order)          # SP propagation, activation, referral / DSA
    return {"id": order.id, "order_no": order.order_no, "status": "paid"}


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    from app.models import Order
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Cannot cancel a confirmed order")
    order.status = "cancelled"
    db.commit()
    return {"id": order.id, "status": "cancelled"}


# ---- Products ----
@router.post("/products", response_model=ProductOut)
def create_product(payload: ProductIn, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump(), slug=slugify(payload.name))
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductIn, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.model_dump().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
    return {"ok": True}


# ---- Payouts ----
@router.get("/payouts")
def all_payouts(status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(PayoutRequest)
    if status:
        stmt = stmt.where(PayoutRequest.status == status)
    rows = db.execute(stmt.order_by(PayoutRequest.created_at.desc())).scalars().all()
    out = []
    for r in rows:
        m = db.get(Member, r.member_id)
        out.append({
            "id": r.id,
            "member_id": m.member_id if m else None,
            "name": m.name if m else None,
            "amount": float(r.amount),
            "tds": float(r.tds or 0),
            "net": float(r.net or 0),
            "status": r.status,
            "created_at": r.created_at,
        })
    return out


@router.post("/payouts/{payout_id}/action")
def act_payout(payout_id: int, action: str, db: Session = Depends(get_db)):
    req = db.get(PayoutRequest, payout_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Payout not found")
    member = db.get(Member, req.member_id)
    if action == "approve":
        req.status = "approved"
    elif action == "pay":
        req.status = "paid"
        if member:  # total_paid = net actually paid to the member (after TDS)
            member.total_paid = Decimal(str(member.total_paid or 0)) + Decimal(str(req.net or req.amount))
    elif action == "reject":
        req.status = "rejected"
        if member:  # refund to wallet
            member.wallet_balance = Decimal(str(member.wallet_balance or 0)) + Decimal(str(req.amount))
    else:
        raise HTTPException(status_code=400, detail="Unknown action")
    db.commit()
    return {"id": req.id, "status": req.status}


@router.post("/payouts/close")
def close_weekly(period: str, label: str | None = None, db: Session = Depends(get_db)):
    """Run the weekly binary-matching close for all MLM members."""
    return close_payout_period(db, period, label)


@router.get("/ranks")
def list_ranks(db: Session = Depends(get_db)):
    return ranks_svc.get_ranks(db)


@router.post("/members/{member_id}/pay-rank-bonus")
def pay_rank_bonus(member_id: str, db: Session = Depends(get_db)):
    """Pay all achieved-but-unpaid one-time rank bonuses to a member."""
    m = db.execute(select(Member).where(Member.member_id == member_id)).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Member not found")
    paid = pay_due_rank_bonuses(db, m)
    return {"member_id": member_id, "rank_level": m.rank_level, "paid": paid}


# ---- Settings ----
@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    return cfg.get_all(db)


@router.put("/settings")
def update_setting(payload: SettingUpdate, db: Session = Depends(get_db)):
    cfg.set_value(db, payload.key, payload.value)
    return {"key": payload.key, "value": payload.value}
