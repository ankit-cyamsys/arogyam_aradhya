from __future__ import annotations

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class SPLedger(Base, TimestampMixin):
    """Every SP event flowing up a member's legs (business volume tracking)."""

    __tablename__ = "sp_ledger"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True, nullable=False)
    source_member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    leg: Mapped[str] = mapped_column(String(1))          # 'L', 'R', or 'S' (self)
    sp: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    note: Mapped[str | None] = mapped_column(String(200))


class CommissionLedger(Base, TimestampMixin):
    """Earnings credited to a member (matching / level bonus / etc.)."""

    __tablename__ = "commission_ledger"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(30))        # matching / level / retail / reward
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    sp_matched: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    period: Mapped[str | None] = mapped_column(String(20))  # e.g. weekly period key 2026-W33
    note: Mapped[str | None] = mapped_column(String(200))


class PayoutRequest(Base, TimestampMixin):
    __tablename__ = "payout_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/approved/paid/rejected
    method: Mapped[str | None] = mapped_column(String(30))
    reference: Mapped[str | None] = mapped_column(String(80))
    note: Mapped[str | None] = mapped_column(String(200))

    member = relationship("Member")


class WeeklyPayout(Base, TimestampMixin):
    """One row of a member's weekly payout register (mirrors the reference)."""

    __tablename__ = "weekly_payouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True, nullable=False)
    period: Mapped[str] = mapped_column(String(20), index=True)      # e.g. "2026-W36" or a date
    week_label: Mapped[str | None] = mapped_column(String(40))       # human label e.g. "28 Aug 2026"
    left_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0)     # SP added left this week
    right_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0)    # SP added right this week
    matching_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0) # matchable this close
    closing_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0)  # matched in 50-blocks
    payout: Mapped[float] = mapped_column(Numeric(14, 2), default=0)      # closing_sp * rate
    cf_left: Mapped[float] = mapped_column(Numeric(14, 2), default=0)     # carry forward after
    cf_right: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="paid")


class Setting(Base, TimestampMixin):
    """Key/value store for admin-configurable MLM parameters + site settings."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(60), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    label: Mapped[str | None] = mapped_column(String(160))
    group: Mapped[str | None] = mapped_column(String(40))
