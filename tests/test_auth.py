def test_bootstrap_registration_creates_admin(client):
    resp = client.post("/register", json={"username": "admin", "password": "supersecret1"})
    assert resp.status_code == 200
    assert resp.json() == {"username": "admin", "role": "admin"}


def test_registration_closed_after_first_admin_exists(client):
    client.post("/register", json={"username": "admin", "password": "supersecret1"})
    resp = client.post("/register", json={"username": "attacker", "password": "whatever12"})
    assert resp.status_code == 403


def test_registration_rejects_short_password(client):
    resp = client.post("/register", json={"username": "admin", "password": "short"})
    assert resp.status_code == 422


def test_login_success_returns_bearer_token(client):
    client.post("/register", json={"username": "admin", "password": "supersecret1"})
    resp = client.post("/login", data={"username": "admin", "password": "supersecret1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_login_wrong_password_rejected(client):
    client.post("/register", json={"username": "admin", "password": "supersecret1"})
    resp = client.post("/login", data={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_user_rejected(client):
    resp = client.post("/login", data={"username": "ghost", "password": "whatever12"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    assert client.get("/me").status_code == 401


def test_me_rejects_garbage_token(client):
    resp = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    resp = client.get("/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == {"username": "admin", "role": "admin"}


def test_login_rate_limited_after_repeated_failures(client):
    client.post("/register", json={"username": "admin", "password": "supersecret1"})
    statuses = [
        client.post("/login", data={"username": "admin", "password": "wrong"}).status_code
        for _ in range(15)
    ]
    assert 429 in statuses, "expected the login rate limiter to eventually kick in"
