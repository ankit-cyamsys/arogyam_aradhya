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
from app.services.mlm_engine import compute_matching
from app.utils.text import slugify

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    members = db.execute(select(func.count(Member.id))).scalar_one()
    active = db.execute(select(func.count(Member.id)).where(Member.is_active.is_(True))).scalar_one()
    orders = db.execute(select(func.count(Order.id))).scalar_one()
    revenue = db.execute(select(func.coalesce(func.sum(Order.total), 0))).scalar_one()
    pending_payouts = db.execute(
        select(func.count(PayoutRequest.id)).where(PayoutRequest.status == "pending")
    ).scalar_one()
    return {
        "members": members,
        "active_members": active,
        "orders": orders,
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
        }
        for m in rows
    ]


@router.post("/members/{member_id}/block")
def toggle_block(member_id: str, db: Session = Depends(get_db)):
    m = db.execute(select(Member).where(Member.member_id == member_id)).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Member not found")
    m.is_blocked = not m.is_blocked
    db.commit()
    return {"member_id": m.member_id, "is_blocked": m.is_blocked}


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
        if member:
            member.total_paid = Decimal(str(member.total_paid or 0)) + Decimal(str(req.amount))
    elif action == "reject":
        req.status = "rejected"
        if member:  # refund to wallet
            member.wallet_balance = Decimal(str(member.wallet_balance or 0)) + Decimal(str(req.amount))
    else:
        raise HTTPException(status_code=400, detail="Unknown action")
    db.commit()
    return {"id": req.id, "status": req.status}


@router.post("/matching/run-all")
def run_all_matching(db: Session = Depends(get_db)):
    members = db.execute(select(Member).where(Member.is_active.is_(True))).scalars().all()
    total = Decimal("0")
    for m in members:
        res = compute_matching(db, m, commit=True)
        total += Decimal(str(res["payout"]))
    return {"processed": len(members), "total_paid": float(total)}


# ---- Settings ----
@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    return cfg.get_all(db)


@router.put("/settings")
def update_setting(payload: SettingUpdate, db: Session = Depends(get_db)):
    cfg.set_value(db, payload.key, payload.value)
    return {"key": payload.key, "value": payload.value}
