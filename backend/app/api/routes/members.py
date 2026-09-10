from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.services import kyc as kyc_svc

from fastapi import HTTPException

from app.api.deps import get_current_member
from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.models import Member, CommissionLedger, Order, WeeklyPayout
from app.schemas import ChangePasswordRequest, DashboardStats, MemberOut, MemberProfileUpdate, TreeNode
from app.services import settings_service as cfg
from app.services import ranks as ranks_svc
from app.services import tree

router = APIRouter(prefix="/api/member", tags=["member"])


@router.get("/me", response_model=MemberOut)
def me(member: Member = Depends(get_current_member)):
    return member


@router.put("/me", response_model=MemberOut)
def update_me(
    payload: MemberProfileUpdate,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member


def _sum(db: Session, member_id: int, kind: str) -> float:
    total = db.execute(
        select(func.coalesce(func.sum(CommissionLedger.amount), 0)).where(
            CommissionLedger.member_id == member_id, CommissionLedger.kind == kind
        )
    ).scalar_one()
    return float(total)


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    left = Decimal(str(member.left_carry or 0))
    right = Decimal(str(member.right_carry or 0))
    matching_sp = float(min(left, right))
    level_recv = _sum(db, member.id, "rank")
    rank = ranks_svc.rank_by_level(ranks_svc.get_ranks(db), member.rank_level or 0)

    return DashboardStats(
        week_payout=0.0,
        total_payout=float(member.total_paid or 0),
        left_sp=float(member.left_carry or 0),
        right_sp=float(member.right_carry or 0),
        matching_sp=matching_sp,
        left_carry=float(member.left_carry or 0),
        right_carry=float(member.right_carry or 0),
        level_bonus=level_recv,
        level_bonus_received=level_recv,
        self_purchase=float(member.self_purchase_sp or 0),
        capping_limit=float(member.capping_limit or 0),
        total_left_sp=float(member.total_left_sp or 0),
        total_right_sp=float(member.total_right_sp or 0),
        wallet_balance=float(member.wallet_balance or 0),
        rank_level=member.rank_level or 0,
        rank_name=(rank["name"] if rank else ""),
        rank_tier=(rank["tier"] if rank else ""),
    )


@router.get("/direct/dashboard")
def direct_dashboard(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    """Summary for a Direct-Selling agent."""
    total_sales = db.execute(
        select(func.coalesce(func.sum(Order.total), 0)).where(Order.member_id == member.id)
    ).scalar_one()
    order_count = db.execute(
        select(func.count(Order.id)).where(Order.member_id == member.id)
    ).scalar_one()
    total_sp = db.execute(
        select(func.coalesce(func.sum(Order.total_sp), 0)).where(Order.member_id == member.id)
    ).scalar_one()
    dsa_earned = _sum(db, member.id, "dsa")
    return {
        "total_sales": float(total_sales),
        "order_count": int(order_count),
        "total_sp": float(total_sp),
        "total_earned": float(member.total_earned or 0),
        "dsa_earned": dsa_earned,
        "wallet_balance": float(member.wallet_balance or 0),
        "total_paid": float(member.total_paid or 0),
        "dsa_percent": float(cfg.get(db, "dsa_percent", 40)),
    }


@router.get("/tree", response_model=TreeNode)
def genealogy(
    depth: int = 3,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    depth = max(1, min(depth, 6))
    return tree.build_tree(db, member, depth)


@router.get("/team")
def team_summary(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    counts = tree.subtree_counts(db, member)
    parent = db.get(Member, member.parent_id) if member.parent_id else None
    return {
        "counts": counts,
        "parent": {"member_id": parent.member_id, "name": parent.name} if parent else None,
        "tree": tree.build_tree(db, member, 3),
    }


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, member.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    member.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"ok": True}


@router.get("/kyc")
def kyc_status(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    return kyc_svc.list_status(db, member.id)


@router.post("/kyc/{doc_type}")
def kyc_upload(
    doc_type: str,
    file: UploadFile = File(...),
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    doc = kyc_svc.save_document(db, member.id, doc_type, file)
    return {"doc_type": doc.doc_type, "filename": doc.filename, "uploaded": True}


@router.get("/kyc/{doc_type}/file")
def kyc_file(
    doc_type: str,
    member: Member = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    doc = kyc_svc.get_document(db, member.id, doc_type)
    return Response(content=doc.data, media_type=doc.content_type)


@router.get("/level-bonus")
def level_bonus(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    ranks = ranks_svc.get_ranks(db)
    rank = ranks_svc.rank_by_level(ranks, member.rank_level or 0)
    payments = db.execute(
        select(CommissionLedger)
        .where(CommissionLedger.member_id == member.id, CommissionLedger.kind == "rank")
        .order_by(CommissionLedger.created_at.desc())
    ).scalars().all()
    return {
        "stored_level": member.rank_level or 0,
        "level_name": rank["name"] if rank else "—",
        "tier": rank["tier"] if rank else "",
        "cumulative_left_sp": float(member.total_left_sp or 0),
        "cumulative_right_sp": float(member.total_right_sp or 0),
        "matching_sp": float(min(Decimal(str(member.total_left_sp or 0)), Decimal(str(member.total_right_sp or 0)))),
        "bonus_payments": [
            {"amount": float(p.amount), "date": p.created_at, "status": "paid", "remarks": p.note}
            for p in payments
        ],
        "ranks": ranks,
    }


@router.get("/bonus")
def bonus_payments(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    rows = db.execute(
        select(CommissionLedger)
        .where(CommissionLedger.member_id == member.id, CommissionLedger.kind.in_(["rank", "referral"]))
        .order_by(CommissionLedger.created_at.desc())
    ).scalars().all()
    return [
        {"date": r.created_at, "amount": float(r.amount), "kind": r.kind, "status": "paid", "note": r.note}
        for r in rows
    ]


@router.get("/payout-register")
def payout_register(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    rows = db.execute(
        select(WeeklyPayout)
        .where(WeeklyPayout.member_id == member.id)
        .order_by(WeeklyPayout.created_at.desc())
    ).scalars().all()
    total = db.execute(
        select(func.coalesce(func.sum(WeeklyPayout.payout), 0)).where(WeeklyPayout.member_id == member.id)
    ).scalar_one()
    return {
        "total_earned": float(total),
        "rows": [
            {
                "week_label": r.week_label, "left_sp": float(r.left_sp), "right_sp": float(r.right_sp),
                "matching_sp": float(r.matching_sp), "closing_sp": float(r.closing_sp),
                "payout": float(r.payout), "cf_left": float(r.cf_left), "cf_right": float(r.cf_right),
                "status": r.status,
            } for r in rows
        ],
    }
