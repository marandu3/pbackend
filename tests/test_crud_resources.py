import pytest

# Each resource exposes an identical CRUD shape (POST/GET /x/, PUT/DELETE /x/{id}).
# Rather than duplicating the same four tests four times, drive them from one
# table of (url prefix, natural "rename" field, minimal valid payload).
RESOURCES = [
    pytest.param(
        "education",
        {"level": "Bachelor", "institution": "MIT", "field_of_study": "CS", "location": "USA", "start_year": 2018},
        "location", "Boston",
        id="education",
    ),
    pytest.param(
        "skills",
        {"name": "Python", "category": "Programming"},
        "category", "Backend",
        id="skills",
    ),
    pytest.param(
        "projects",
        {"title": "Portfolio", "technologies": ["Angular", "FastAPI"]},
        "title", "Portfolio v2",
        id="projects",
    ),
    pytest.param(
        "timeline",
        {"title": "Started Job", "start_date": "2023-01-01"},
        "location", "Remote",
        id="timeline",
    ),
]


@pytest.mark.parametrize("resource,payload,changed_field,changed_value", RESOURCES)
def test_create_then_list(client, auth_headers, resource, payload, changed_field, changed_value):
    resp = client.post(f"/{resource}/", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    created = resp.json()
    assert created["id"]

    listed = client.get(f"/{resource}/").json()
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]


@pytest.mark.parametrize("resource,payload,changed_field,changed_value", RESOURCES)
def test_update_by_id_survives_field_change(client, auth_headers, resource, payload, changed_field, changed_value):
    """The exact bug the old natural-key routes had: editing the field used as
    the lookup key (title/name/level) must not orphan the record."""
    created = client.post(f"/{resource}/", json=payload, headers=auth_headers).json()
    updated_payload = {**payload, changed_field: changed_value}

    resp = client.put(f"/{resource}/{created['id']}", json=updated_payload, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()[changed_field] == changed_value
    assert resp.json()["id"] == created["id"]

    listed = client.get(f"/{resource}/").json()
    assert len(listed) == 1
    assert listed[0][changed_field] == changed_value


@pytest.mark.parametrize("resource,payload,changed_field,changed_value", RESOURCES)
def test_update_invalid_id_format_is_400_not_500(client, auth_headers, resource, payload, changed_field, changed_value):
    resp = client.put(f"/{resource}/not-a-real-object-id", json=payload, headers=auth_headers)
    assert resp.status_code == 400


@pytest.mark.parametrize("resource,payload,changed_field,changed_value", RESOURCES)
def test_update_missing_id_is_404(client, auth_headers, resource, payload, changed_field, changed_value):
    resp = client.put(f"/{resource}/64b64b64b64b64b64b64b64b", json=payload, headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.parametrize("resource,payload,changed_field,changed_value", RESOURCES)
def test_delete_by_id(client, auth_headers, resource, payload, changed_field, changed_value):
    created = client.post(f"/{resource}/", json=payload, headers=auth_headers).json()

    resp = client.delete(f"/{resource}/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert client.get(f"/{resource}/").json() == []

    # deleting again is a 404, not a crash
    assert client.delete(f"/{resource}/{created['id']}", headers=auth_headers).status_code == 404


@pytest.mark.parametrize("resource,payload,changed_field,changed_value", RESOURCES)
def test_mutations_require_auth(client, resource, payload, changed_field, changed_value):
    assert client.post(f"/{resource}/", json=payload).status_code == 401
    assert client.put(f"/{resource}/64b64b64b64b64b64b64b64b", json=payload).status_code == 401
    assert client.delete(f"/{resource}/64b64b64b64b64b64b64b64b").status_code == 401


@pytest.mark.parametrize("resource,payload,changed_field,changed_value", RESOURCES)
def test_public_read_needs_no_auth(client, resource, payload, changed_field, changed_value):
    assert client.get(f"/{resource}/").status_code == 200
