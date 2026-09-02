def test_create_generates_slug_from_title(client, auth_headers):
    resp = client.post("/projects/", json={"title": "My Cool Project!"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["slug"] == "my-cool-project"


def test_duplicate_titles_get_distinct_slugs(client, auth_headers):
    first = client.post("/projects/", json={"title": "Portfolio"}, headers=auth_headers).json()
    second = client.post("/projects/", json={"title": "Portfolio"}, headers=auth_headers).json()
    assert first["slug"] == "portfolio"
    assert second["slug"] == "portfolio-2"
    assert first["id"] != second["id"]


def test_get_project_by_slug(client, auth_headers):
    created = client.post("/projects/", json={"title": "Student Support LLM"}, headers=auth_headers).json()

    resp = client.get(f"/projects/slug/{created['slug']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_project_by_unknown_slug_is_404(client):
    assert client.get("/projects/slug/does-not-exist").status_code == 404


def test_slug_is_stable_across_title_rename(client, auth_headers):
    created = client.post("/projects/", json={"title": "Original Title"}, headers=auth_headers).json()
    original_slug = created["slug"]

    updated = client.put(
        f"/projects/{created['id']}",
        json={"title": "Completely Different Title"},
        headers=auth_headers,
    ).json()

    assert updated["slug"] == original_slug, "renaming a project must not change its public URL"
    assert client.get(f"/projects/slug/{original_slug}").json()["title"] == "Completely Different Title"


def test_featured_and_order_default_safely(client, auth_headers):
    created = client.post("/projects/", json={"title": "Untouched Defaults"}, headers=auth_headers).json()
    assert created["featured"] is False
    assert created["order"] == 0


def test_featured_and_order_are_settable(client, auth_headers):
    created = client.post(
        "/projects/",
        json={"title": "Flagship Project", "featured": True, "order": 1},
        headers=auth_headers,
    ).json()
    assert created["featured"] is True
    assert created["order"] == 1
