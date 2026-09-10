from decimal import Decimal

from app.core.security import hash_password
from app.models import PayoutRequest
from tests.conftest import make_member


def _login(client, member_id, pw="pass123"):
    r = client.post("/api/auth/login", json={"username": member_id, "password": pw, "segment": "mlm"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_withdrawal_deducts_5pct_tds(client, db):
    m = make_member(db, "Earner", active=True)
    m.password_hash = hash_password("pass123")
    m.wallet_balance = Decimal("10000")
    db.commit()
    H = _login(client, m.member_id)
    r = client.post("/api/mlm/payouts", json={"amount": 2000}, headers=H)
    assert r.status_code == 200
    data = r.json()
    assert data["amount"] == 2000.0
    assert data["tds"] == 100.0      # 5% of 2000
    assert data["net"] == 1900.0     # payable to member
    db.refresh(m)
    assert float(m.wallet_balance) == 8000.0   # gross debited from wallet


def test_withdrawal_below_min_rejected(client, db):
    m = make_member(db, "Earner", active=True)
    m.password_hash = hash_password("pass123")
    m.wallet_balance = Decimal("10000")
    db.commit()
    H = _login(client, m.member_id)
    assert client.post("/api/mlm/payouts", json={"amount": 100}, headers=H).status_code == 400
