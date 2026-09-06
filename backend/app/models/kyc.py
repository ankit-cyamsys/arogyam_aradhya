from __future__ import annotations

from sqlalchemy import ForeignKey, LargeBinary, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin

# Allowed document slots
DOC_TYPES = ["profile_photo", "aadhaar_front", "aadhaar_back", "pan_front", "pan_back"]


class KycDocument(Base, TimestampMixin):
    """A member's uploaded KYC file, stored in the database (one per doc type).

    No verification workflow — files are simply stored and viewable by the
    member and the admin.
    """

    __tablename__ = "kyc_documents"
    __table_args__ = (UniqueConstraint("member_id", "doc_type", name="uq_member_doctype"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True, nullable=False)
    doc_type: Mapped[str] = mapped_column(String(30), nullable=False)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
