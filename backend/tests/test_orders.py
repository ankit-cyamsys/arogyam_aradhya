from decimal import Decimal

from app.core.security import hash_password
from app.models import CommissionLedger, Order
from tests.conftest import make_member


def _login(client, member_id, pw="pass123", segment="mlm"):
    r = client.post("/api/auth/login", json={"username": member_id, "password": pw, "segment": segment})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_order_pending_then_admin_confirm(client, db, product, admin_user):
    sponsor = make_member(db, "Sponsor", segment="mlm", active=True)
    buyer = make_member(db, "Buyer", segment="mlm", sponsor=sponsor, position="L")
    buyer.password_hash = hash_password("pass123")
    db.commit()

    H = _login(client, buyer.member_id)
    # place order (product is ₹100, 1 SP each) x60 => activates + gives sponsor left SP
    r = client.post("/api/orders", json={"items": [{"product_id": product.id, "quantity": 60}]}, headers=H)
    assert r.status_code == 200
    o = r.json()
    assert o["status"] == "pending" and o["payment_status"] == "unpaid"

    # No commissions/activation yet
    db.refresh(buyer)
    assert buyer.is_active is False
    assert db.query(CommissionLedger).count() == 0

    # Admin confirms payment
    admin_h = {"Authorization": f"Bearer {client.post('/api/auth/admin/login', json={'username':'admin','password':'Admin@2026'}).json()['access_token']}"}
    rc = client.post(f"/api/admin/orders/{o['id']}/confirm", headers=admin_h)
    assert rc.status_code == 200

    # Now processed: buyer active, sponsor got referral + left SP
    db.refresh(buyer); db.refresh(sponsor)
    assert buyer.is_active is True
    assert float(sponsor.total_left_sp) == 60.0
    assert db.query(CommissionLedger).filter_by(kind="referral").count() == 1

    # Double confirm rejected
    assert client.post(f"/api/admin/orders/{o['id']}/confirm", headers=admin_h).status_code == 400


def test_cancel_pending_order(client, db, product, admin_user):
    buyer = make_member(db, "Buyer", segment="direct")
    buyer.password_hash = hash_password("pass123")
    db.commit()
    H = _login(client, buyer.member_id, segment="direct")
    o = client.post("/api/orders", json={"items": [{"product_id": product.id, "quantity": 5}]}, headers=H).json()

    admin_h = {"Authorization": f"Bearer {client.post('/api/auth/admin/login', json={'username':'admin','password':'Admin@2026'}).json()['access_token']}"}
    assert client.post(f"/api/admin/orders/{o['id']}/cancel", headers=admin_h).status_code == 200
    # cannot confirm a cancelled order
    assert client.post(f"/api/admin/orders/{o['id']}/confirm", headers=admin_h).status_code == 400
    db.refresh(buyer)
    assert buyer.is_active is False
