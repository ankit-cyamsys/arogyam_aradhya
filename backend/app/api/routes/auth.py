from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Member, AdminUser
from app.schemas import (
    LoginRequest,
    SignupRequest,
    DirectSignupRequest,
    TokenResponse,
    AdminLoginRequest,
)
from app.services import tree
from app.services.ids import generate_member_id

router = APIRouter(prefix="/api/auth", tags=["auth"])

SEGMENT_LABEL = {"mlm": "MLM Network", "direct": "Direct Selling"}


def _token(member: Member) -> TokenResponse:
    token = create_access_token(subject=member.member_id, role="member", segment=member.segment)
    return TokenResponse(
        access_token=token, role="member", segment=member.segment,
        member_id=member.member_id, name=member.name,
    )


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """MLM (binary network) signup — requires a sponsor and placement leg."""
    sponsor = db.execute(
        select(Member).where(Member.member_id == payload.sponsor_id.strip().upper())
    ).scalar_one_or_none()
    if sponsor is None:
        raise HTTPException(status_code=404, detail="Sponsor ID not found")
    if sponsor.segment != "mlm":
        raise HTTPException(status_code=400, detail="Sponsor must be an MLM member")

    if payload.email:
        dup = db.execute(select(Member).where(Member.email == payload.email)).scalar_one_or_none()
        if dup:
            raise HTTPException(status_code=409, detail="Email already registered")

    parent, leg = tree.find_placement(db, sponsor, payload.position)
    member = Member(
        member_id=generate_member_id(db),
        segment="mlm",
        name=payload.name.strip(),
        email=payload.email,
        phone=payload.phone.strip(),
        password_hash=hash_password(payload.password),
        sponsor_id=sponsor.id,
        parent_id=parent.id,
        position=leg,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return _token(member)


@router.post("/direct/signup", response_model=TokenResponse)
def direct_signup(payload: DirectSignupRequest, db: Session = Depends(get_db)):
    """Direct-selling signup — standalone agent, no sponsor or binary tree."""
    if payload.email:
        dup = db.execute(select(Member).where(Member.email == payload.email)).scalar_one_or_none()
        if dup:
            raise HTTPException(status_code=409, detail="Email already registered")

    referrer = None
    if payload.referral_code:
        referrer = db.execute(
            select(Member).where(Member.member_id == payload.referral_code.strip().upper())
        ).scalar_one_or_none()

    member = Member(
        member_id=generate_member_id(db),
        segment="direct",
        name=payload.name.strip(),
        email=payload.email,
        phone=payload.phone.strip(),
        password_hash=hash_password(payload.password),
        sponsor_id=referrer.id if referrer else None,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return _token(member)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    ident = payload.username.strip()
    member = db.execute(
        select(Member).where(
            or_(Member.member_id == ident.upper(), Member.phone == ident, Member.email == ident)
        )
    ).scalar_one_or_none()
    if member is None or not verify_password(payload.password, member.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if member.is_blocked:
        raise HTTPException(status_code=403, detail="Account is blocked")
    # Portal guard: don't let a direct seller log into the MLM portal or vice-versa.
    if payload.segment and member.segment != payload.segment:
        want = SEGMENT_LABEL.get(member.segment, member.segment)
        raise HTTPException(status_code=403, detail=f"This account belongs to the {want} portal.")
    return _token(member)


@router.post("/token", response_model=TokenResponse)
def token_login(payload: LoginRequest, db: Session = Depends(get_db)):
    return login(payload, db)


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.execute(
        select(AdminUser).where(AdminUser.username == payload.username.strip())
    ).scalar_one_or_none()
    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    token = create_access_token(subject=admin.username, role="admin")
    return TokenResponse(access_token=token, role="admin", name=admin.name or admin.username)
