import io

import pytest
from fastapi import HTTPException
from starlette.datastructures import Headers, UploadFile

from app.services import kyc as kyc_svc
from tests.conftest import make_member


def _upload(data=b"fakeimage", name="a.png", ct="image/png"):
    return UploadFile(file=io.BytesIO(data), filename=name, headers=Headers({"content-type": ct}))


def test_upload_and_fetch(db):
    m = make_member(db, "M")
    kyc_svc.save_document(db, m.id, "aadhaar_front", _upload())
    doc = kyc_svc.get_document(db, m.id, "aadhaar_front")
    assert doc.content_type == "image/png"
    assert doc.data == b"fakeimage"
    status = kyc_svc.list_status(db, m.id)
    assert status["aadhaar_front"]["uploaded"] is True
    assert status["pan_front"]["uploaded"] is False


def test_replace_document(db):
    m = make_member(db, "M")
    kyc_svc.save_document(db, m.id, "pan_front", _upload(b"v1"))
    kyc_svc.save_document(db, m.id, "pan_front", _upload(b"v2"))
    assert kyc_svc.get_document(db, m.id, "pan_front").data == b"v2"
    # still exactly one row for this member/type
    from app.models import KycDocument
    n = db.query(KycDocument).filter_by(member_id=m.id, doc_type="pan_front").count()
    assert n == 1


def test_invalid_doc_type(db):
    m = make_member(db, "M")
    with pytest.raises(HTTPException) as e:
        kyc_svc.save_document(db, m.id, "passport", _upload())
    assert e.value.status_code == 400


def test_invalid_content_type(db):
    m = make_member(db, "M")
    with pytest.raises(HTTPException) as e:
        kyc_svc.save_document(db, m.id, "pan_back", _upload(ct="application/zip"))
    assert e.value.status_code == 400


def test_get_missing_document(db):
    m = make_member(db, "M")
    with pytest.raises(HTTPException) as e:
        kyc_svc.get_document(db, m.id, "profile_photo")
    assert e.value.status_code == 404
