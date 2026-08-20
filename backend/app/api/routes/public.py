from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import settings_service as cfg

router = APIRouter(prefix="/api/site", tags=["site"])

_PUBLIC_KEYS = {"company_name", "support_phone", "support_email", "address"}


@router.get("/settings")
def site_settings(db: Session = Depends(get_db)):
    allv = cfg.get_all(db)
    return {k: v for k, v in allv.items() if k in _PUBLIC_KEYS}
