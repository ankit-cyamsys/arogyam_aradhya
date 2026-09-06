from tests.conftest import make_member


def _root(db):
    return make_member(db, "Sponsor Root", segment="mlm", active=True)


# ---------------- Signup ----------------
def test_signup_success(client, db):
    root = _root(db)
    r = client.post("/api/auth/signup", json={
        "name": "New Member", "phone": "9876543210", "password": "secret1",
        "sponsor_id": root.member_id, "position": "L",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["role"] == "member" and data["segment"] == "mlm"
    assert data["member_id"].startswith("AA")


def test_signup_weak_password_rejected(client, db):
    root = _root(db)
    r = client.post("/api/auth/signup", json={
        "name": "Xavier", "phone": "9876500000", "password": "123",
        "sponsor_id": root.member_id,
    })
    assert r.status_code == 422  # pydantic min_length


def test_signup_bad_sponsor(client, db):
    r = client.post("/api/auth/signup", json={
        "name": "Xavier", "phone": "9876500001", "password": "secret1", "sponsor_id": "AA00000000",
    })
    assert r.status_code == 404


def test_signup_duplicate_phone(client, db):
    root = _root(db)
    body = {"name": "Aay", "phone": "9811111111", "password": "secret1", "sponsor_id": root.member_id}
    assert client.post("/api/auth/signup", json=body).status_code == 200
    body2 = {**body, "name": "Bee", "sponsor_id": root.member_id}
    r = client.post("/api/auth/signup", json=body2)
    assert r.status_code == 409


def test_phone_normalization_and_login(client, db):
    root = _root(db)
    # +91 prefix + spaces should normalise to 10 digits
    r = client.post("/api/auth/signup", json={
        "name": "Norm", "phone": "+91 98765 12345", "password": "secret1", "sponsor_id": root.member_id,
    })
    assert r.status_code == 200
    # login by the normalised phone
    r2 = client.post("/api/auth/login", json={"username": "9876512345", "password": "secret1", "segment": "mlm"})
    assert r2.status_code == 200


# ---------------- Login ----------------
def test_login_wrong_password(client, db):
    m = make_member(db, "M", active=True)
    # set a known password
    from app.core.security import hash_password
    m.password_hash = hash_password("rightpass")
    db.commit()
    r = client.post("/api/auth/login", json={"username": m.member_id, "password": "wrongpass"})
    assert r.status_code == 401


def test_login_blocked(client, db):
    from app.core.security import hash_password
    m = make_member(db, "M", active=True)
    m.password_hash = hash_password("pass123")
    m.is_blocked = True
    db.commit()
    r = client.post("/api/auth/login", json={"username": m.member_id, "password": "pass123"})
    assert r.status_code == 403


def test_portal_guard(client, db):
    from app.core.security import hash_password
    seller = make_member(db, "Seller", segment="direct")
    seller.password_hash = hash_password("pass123")
    db.commit()
    # trying to log a direct account into the MLM portal is rejected
    r = client.post("/api/auth/login", json={"username": seller.member_id, "password": "pass123", "segment": "mlm"})
    assert r.status_code == 403


# ---------------- Change password ----------------
def test_change_password(client, db):
    from app.core.security import hash_password
    m = make_member(db, "M", active=True)
    m.password_hash = hash_password("oldpass")
    db.commit()
    tok = client.post("/api/auth/login", json={"username": m.member_id, "password": "oldpass"}).json()["access_token"]
    H = {"Authorization": f"Bearer {tok}"}
    # wrong current
    assert client.post("/api/member/change-password", json={"current_password": "nope", "new_password": "newpass1"}, headers=H).status_code == 400
    # correct
    assert client.post("/api/member/change-password", json={"current_password": "oldpass", "new_password": "newpass1"}, headers=H).status_code == 200
    # old no longer works, new does
    assert client.post("/api/auth/login", json={"username": m.member_id, "password": "oldpass"}).status_code == 401
    assert client.post("/api/auth/login", json={"username": m.member_id, "password": "newpass1"}).status_code == 200


# ---------------- Admin ----------------
def test_admin_login(client, db, admin_user):
    assert client.post("/api/auth/admin/login", json={"username": "admin", "password": "Admin@2026"}).status_code == 200
    assert client.post("/api/auth/admin/login", json={"username": "admin", "password": "wrong"}).status_code == 401


# ---------------- Rate limiting ----------------
def test_login_rate_limited(client, db):
    # login limit is 15 / 5min per IP
    codes = [client.post("/api/auth/login", json={"username": "AA00000000", "password": "x"}).status_code for _ in range(20)]
    assert 429 in codes, "expected rate limiting to kick in"
