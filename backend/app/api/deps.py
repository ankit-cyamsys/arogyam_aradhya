from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models import Member, AdminUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

_CREDS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _payload(token: str | None) -> dict:
    if not token:
        raise _CREDS_EXC
    try:
        return decode_token(token)
    except JWTError:
        raise _CREDS_EXC


def get_current_member(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Member:
    payload = _payload(token)
    if payload.get("role") != "member":
        raise _CREDS_EXC
    member = db.execute(
        select(Member).where(Member.member_id == payload.get("sub"))
    ).scalar_one_or_none()
    if member is None:
        raise _CREDS_EXC
    if member.is_blocked:
        raise HTTPException(status_code=403, detail="Account is blocked")
    return member


def get_current_admin(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    payload = _payload(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    admin = db.execute(
        select(AdminUser).where(AdminUser.username == payload.get("sub"))
    ).scalar_one_or_none()
    if admin is None:
        raise _CREDS_EXC
    return admin
