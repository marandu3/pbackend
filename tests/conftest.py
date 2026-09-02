import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ["DATABASE_URL"] = "mongodb://localhost:27017"
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:4200")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mongomock
import pytest
from fastapi.testclient import TestClient

with patch("pymongo.mongo_client.MongoClient", mongomock.MongoClient):
    import main  # noqa: E402  (must import after the MongoClient patch)


@pytest.fixture(autouse=True)
def clean_database():
    """Every test starts from an empty database with the app's real indexes in
    place, and a freshly reset rate limiter (its counters are process-global
    and would otherwise leak between tests since they all share one client)."""
    main.client.drop_database(main.settings.database_name)
    main.user_collection.create_index("username", unique=True)
    main.project_collection.create_index("slug", unique=True)
    main.limiter.reset()
    yield


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture
def admin_token(client):
    client.post("/register", json={"username": "admin", "password": "supersecret1"})
    resp = client.post("/login", data={"username": "admin", "password": "supersecret1"})
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
