from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_member
from app.core.database import get_db
from app.models import Member, CommissionLedger, PayoutRequest
from app.schemas import CommissionOut, PayoutRequestIn, PayoutRequestOut
from app.services import settings_service as cfg

router = APIRouter(prefix="/api/mlm", tags=["mlm"])


@router.get("/commissions", response_model=list[CommissionOut])
def commissions(
    kind: str | None = None,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    stmt = select(CommissionLedger).where(CommissionLedger.member_id == member.id)
    if kind:
        stmt = stmt.where(CommissionLedger.kind == kind)
    return db.execute(stmt.order_by(CommissionLedger.created_at.desc())).scalars().all()


@router.get("/payouts", response_model=list[PayoutRequestOut])
def payouts(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    return (
        db.execute(
            select(PayoutRequest)
            .where(PayoutRequest.member_id == member.id)
            .order_by(PayoutRequest.created_at.desc())
        )
        .scalars()
        .all()
    )


@router.post("/payouts", response_model=PayoutRequestOut)
def request_payout(
    payload: PayoutRequestIn,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    minimum = Decimal(str(cfg.get(db, "payout_min", 500)))
    amount = Decimal(str(payload.amount))
    balance = Decimal(str(member.wallet_balance or 0))

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if amount < minimum:
        raise HTTPException(status_code=400, detail=f"Minimum payout is ₹{minimum}")
    if amount > balance:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    # 5% TDS deducted from the gross; member receives the net.
    tds_pct = Decimal(str(cfg.get(db, "tds_percent", 5)))
    tds = (amount * tds_pct / Decimal("100")).quantize(Decimal("0.01"))
    net = (amount - tds).quantize(Decimal("0.01"))

    member.wallet_balance = balance - amount
    req = PayoutRequest(member_id=member.id, amount=amount, tds=tds, net=net,
                        status="pending", method="bank")
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/idcard")
def id_card(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    return {
        "member_id": member.member_id,
        "name": member.name,
        "phone": member.phone,
        "is_active": member.is_active,
        "joined": member.created_at.date().isoformat() if member.created_at else None,
        "company": cfg.get(db, "company_name", "Arogyam Aradhya"),
    }
