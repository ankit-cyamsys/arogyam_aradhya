from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_member
from app.core.database import get_db
from app.models import Member, CommissionLedger, Order
from app.schemas import DashboardStats, MemberOut, MemberProfileUpdate, TreeNode
from app.services import settings_service as cfg
from app.services import tree
from app.services.mlm_engine import compute_matching

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
    level_recv = _sum(db, member.id, "level")

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
        capping_limit=float(cfg.get(db, "daily_capping", 25000)),
        total_left_sp=float(member.total_left_sp or 0),
        total_right_sp=float(member.total_right_sp or 0),
        wallet_balance=float(member.wallet_balance or 0),
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


@router.post("/matching/run")
def run_matching(member: Member = Depends(get_current_member), db: Session = Depends(get_db)):
    """Trigger a matching calculation for this member (admin runs weekly in prod)."""
    return compute_matching(db, member, commit=True)
