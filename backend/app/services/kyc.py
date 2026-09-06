from __future__ import annotations

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KycDocument
from app.models.kyc import DOC_TYPES

ALLOWED_CT = {"image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf"}
MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def save_document(db: Session, member_id: int, doc_type: str, upload: UploadFile) -> KycDocument:
    if doc_type not in DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid document type. Allowed: {', '.join(DOC_TYPES)}")
    ct = (upload.content_type or "").lower()
    if ct not in ALLOWED_CT:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, WEBP or PDF files are allowed")
    data = upload.file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 5 MB)")

    doc = db.execute(
        select(KycDocument).where(
            KycDocument.member_id == member_id, KycDocument.doc_type == doc_type
        )
    ).scalar_one_or_none()
    if doc is None:
        doc = KycDocument(member_id=member_id, doc_type=doc_type)
        db.add(doc)
    doc.filename = upload.filename or f"{doc_type}"
    doc.content_type = ct
    doc.data = data
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, member_id: int, doc_type: str) -> KycDocument:
    doc = db.execute(
        select(KycDocument).where(
            KycDocument.member_id == member_id, KycDocument.doc_type == doc_type
        )
    ).scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not uploaded")
    return doc


def list_status(db: Session, member_id: int) -> dict:
    docs = db.execute(
        select(KycDocument).where(KycDocument.member_id == member_id)
    ).scalars().all()
    have = {d.doc_type: {"uploaded": True, "filename": d.filename, "content_type": d.content_type} for d in docs}
    return {dt: have.get(dt, {"uploaded": False}) for dt in DOC_TYPES}
