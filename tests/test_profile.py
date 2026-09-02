def test_profile_create_and_read(client, auth_headers):
    client.post("/profile", json={"name": "John", "title": "Dev"}, headers=auth_headers)
    resp = client.get("/profile")
    assert resp.status_code == 200
    assert resp.json() == [{
        "name": "John", "title": "Dev", "description": None,
        "social_links": None, "profile_image_url": None,
    }]


def test_profile_update_stays_a_single_document(client, auth_headers):
    client.post("/profile", json={"name": "John", "title": "Dev"}, headers=auth_headers)
    client.post("/profile", json={"name": "John", "title": "Senior Dev"}, headers=auth_headers)
    client.post("/profile", json={"name": "John", "title": "Staff Dev"}, headers=auth_headers)

    resp = client.get("/profile")
    profiles = resp.json()
    assert len(profiles) == 1, "profile save must upsert, never accumulate documents"
    assert profiles[0]["title"] == "Staff Dev"


def test_profile_create_requires_auth(client):
    resp = client.post("/profile", json={"name": "John", "title": "Dev"})
    assert resp.status_code == 401


def test_profile_requires_name_and_title(client, auth_headers):
    resp = client.post("/profile", json={"name": "John"}, headers=auth_headers)
    assert resp.status_code == 422


def test_profile_empty_before_first_save(client):
    resp = client.get("/profile")
    assert resp.status_code == 200
    assert resp.json() == []
