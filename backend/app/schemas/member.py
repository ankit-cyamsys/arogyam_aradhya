from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: str
    segment: str = "mlm"
    name: str
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    is_active: bool
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    pan: str | None = None
    bank_name: str | None = None
    bank_account: str | None = None
    bank_ifsc: str | None = None
    nominee: str | None = None
    wallet_balance: float = 0
    total_earned: float = 0


class MemberProfileUpdate(BaseModel):
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    pan: str | None = None
    aadhaar: str | None = None
    bank_name: str | None = None
    bank_account: str | None = None
    bank_ifsc: str | None = None
    nominee: str | None = None


class DashboardStats(BaseModel):
    week_payout: float
    total_payout: float
    left_sp: float
    right_sp: float
    matching_sp: float
    left_carry: float
    right_carry: float
    level_bonus: float
    level_bonus_received: float
    self_purchase: float
    capping_limit: float
    total_left_sp: float
    total_right_sp: float
    wallet_balance: float


class TreeNode(BaseModel):
    member_id: str
    name: str
    is_active: bool
    position: str | None = None
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None
