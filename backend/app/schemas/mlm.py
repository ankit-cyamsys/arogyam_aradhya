from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    amount: float
    sp_matched: float
    note: str | None = None
    created_at: datetime


class PayoutRequestIn(BaseModel):
    amount: float


class PayoutRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    tds: float = 0
    net: float = 0
    status: str
    method: str | None = None
    reference: str | None = None
    created_at: datetime


class SettingOut(BaseModel):
    key: str
    value: object
    label: str | None = None
    group: str | None = None


class SettingUpdate(BaseModel):
    key: str
    value: object
