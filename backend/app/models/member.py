from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Member(Base, TimestampMixin):
    """A distributor in the binary MLM network.

    Two independent relationships matter:
      * sponsor_id  -> who referred/introduced this member (used for level bonus)
      * parent_id   -> placement position in the binary tree (used for matching)
      * position    -> 'L' or 'R' leg under the parent
    """

    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)

    # Which portal this account belongs to: 'mlm' (binary network) or 'direct' (direct seller)
    segment: Mapped[str] = mapped_column(String(10), default="mlm", index=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Binary tree placement
    sponsor_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), index=True)
    position: Mapped[str | None] = mapped_column(String(1))  # 'L' or 'R'

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)   # "green" ID (>=50 SP self purchase)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    rank_level: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # 0=none .. 12=Global Icon
    rank_bonus_paid_level: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # SP added this payout-week (for the payout register); reset at weekly close
    week_left_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0, server_default="0")
    week_right_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0, server_default="0")

    # Running balances / carry-forward (in SP)
    left_carry: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    right_carry: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_left_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_right_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_matched_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0, server_default="0")  # lifetime matched (drives rank)
    self_purchase_sp: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    capping_limit: Mapped[float] = mapped_column(Numeric(14, 2), default=0, server_default="0")  # weekly matching cap, set at greening

    wallet_balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0)  # payable earnings
    total_earned: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_paid: Mapped[float] = mapped_column(Numeric(14, 2), default=0)

    # KYC / profile
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(80))
    state: Mapped[str | None] = mapped_column(String(80))
    pincode: Mapped[str | None] = mapped_column(String(10))
    pan: Mapped[str | None] = mapped_column(String(20))
    aadhaar: Mapped[str | None] = mapped_column(String(20))
    bank_name: Mapped[str | None] = mapped_column(String(120))
    bank_account: Mapped[str | None] = mapped_column(String(30))
    bank_ifsc: Mapped[str | None] = mapped_column(String(20))
    nominee: Mapped[str | None] = mapped_column(String(120))

    # Self-referential relationships
    sponsor = relationship("Member", remote_side=[id], foreign_keys=[sponsor_id], backref="referrals")
    parent = relationship("Member", remote_side=[id], foreign_keys=[parent_id])

    def public_dict(self) -> dict:
        return {
            "id": self.id,
            "member_id": self.member_id,
            "name": self.name,
            "position": self.position,
            "is_active": self.is_active,
        }
