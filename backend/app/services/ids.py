from __future__ import annotations

import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Member, Order


def generate_member_id(db: Session) -> str:
    prefix = settings.MEMBER_ID_PREFIX
    for _ in range(50):
        candidate = f"{prefix}{random.randint(10_000_000, 99_999_999)}"
        exists = db.execute(
            select(Member.id).where(Member.member_id == candidate)
        ).scalar_one_or_none()
        if not exists:
            return candidate
    raise RuntimeError("Could not allocate a unique member id")


def generate_order_no(db: Session) -> str:
    for _ in range(50):
        candidate = f"ORD{random.randint(100_000, 999_999)}"
        exists = db.execute(
            select(Order.id).where(Order.order_no == candidate)
        ).scalar_one_or_none()
        if not exists:
            return candidate
    raise RuntimeError("Could not allocate a unique order no")
