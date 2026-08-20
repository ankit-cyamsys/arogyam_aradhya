from __future__ import annotations

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=20)
    email: str | None = None
    password: str = Field(min_length=3, max_length=128)
    sponsor_id: str = Field(description="Sponsor's member ID, e.g. AA47818100")
    position: str = Field(default="L", pattern="^[LR]$")


class DirectSignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=20)
    email: str | None = None
    password: str = Field(min_length=3, max_length=128)
    referral_code: str | None = None  # optional, for tracking only (no downline)


class LoginRequest(BaseModel):
    username: str  # member_id or phone
    password: str
    segment: str | None = None  # portal guard: 'mlm' or 'direct'


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    segment: str | None = None
    member_id: str | None = None
    name: str | None = None
