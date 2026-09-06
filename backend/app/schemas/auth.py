from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


def _clean_phone(v: str) -> str:
    """Keep digits only; accept an optional leading country code, store 10 digits."""
    digits = "".join(ch for ch in (v or "") if ch.isdigit())
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError("Enter a valid 10-digit mobile number")
    return digits


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str
    email: EmailStr | None = None
    password: str = Field(min_length=6, max_length=128)
    sponsor_id: str = Field(min_length=3, description="Sponsor's member ID, e.g. AA47818100")
    position: str = Field(default="L", pattern="^[LR]$")

    @field_validator("phone")
    @classmethod
    def _v_phone(cls, v: str) -> str:
        return _clean_phone(v)


class DirectSignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str
    email: EmailStr | None = None
    password: str = Field(min_length=6, max_length=128)
    referral_code: str | None = None  # optional, for tracking only (no downline)

    @field_validator("phone")
    @classmethod
    def _v_phone(cls, v: str) -> str:
        return _clean_phone(v)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=120)  # member_id or phone
    password: str = Field(min_length=1, max_length=128)
    segment: str | None = None  # portal guard: 'mlm' or 'direct'


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=1, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    segment: str | None = None
    member_id: str | None = None
    name: str | None = None
