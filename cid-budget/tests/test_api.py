"""Integration tests for CID Budget Estimator API."""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
from app.models import Base
from app import main as main_mod
from fastapi.testclient import TestClient

TEST_DB_URL = "sqlite:///./test_budget.db"


@pytest.fixture(autouse=True)
def setup_db():
    old_db_url = os.environ.get("DATABASE_URL")
    old_jwt = os.environ.get("JWT_SECRET")
    os.environ["DATABASE_URL"] = TEST_DB_URL
    os.environ["JWT_SECRET"] = "test-secret"
    if main_mod.engine:
        Base.metadata.drop_all(bind=main_mod.engine)
    main_mod.engine = None
    main_mod.SessionLocal = None
    main_mod.init_db()
    yield
    if main_mod.engine:
        Base.metadata.drop_all(bind=main_mod.engine)
    if old_db_url:
        os.environ["DATABASE_URL"] = old_db_url
    else:
        os.environ.pop("DATABASE_URL", None)
    if old_jwt:
        os.environ["JWT_SECRET"] = old_jwt
    else:
        os.environ.pop("JWT_SECRET", None)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    import jwt
    token = jwt.encode({"sub": "test-user", "role": "admin"}, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def _create_budget(client, auth_headers, project_id="proj-1", level="medium"):
    resp = client.post(f"/api/budget/projects/{project_id}/generate?level={level}", headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()["budget"]["id"]


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app"] == "CID Budget Estimator"


def test_unauthorized_without_token(client):
    resp = client.get("/api/budget/templates")
    assert resp.status_code == 401


def test_unauthorized_bad_token(client):
    resp = client.get("/api/budget/templates", headers={"Authorization": "Bearer bad-token"})
    assert resp.status_code == 401


def test_list_templates(client, auth_headers):
    resp = client.get("/api/budget/templates", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["templates"]) == 5
    assert data["templates"][0]["id"] == "film_low"


def test_generate_budget(client, auth_headers):
    bid = _create_budget(client, auth_headers)
    resp = client.get(f"/api/budget/{bid}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["budget"]["status"] == "draft"
    assert data["budget"]["total_estimated"] > 0
    assert len(data["lines"]) > 0


def test_list_budgets(client, auth_headers):
    _create_budget(client, auth_headers)
    resp = client.get("/api/budget/projects/proj-1", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["budgets"]) == 1


def test_get_active_budget(client, auth_headers):
    _create_budget(client, auth_headers, "proj-1")
    resp = client.get("/api/budget/projects/proj-1/active", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["budget"] is None


def test_activate_budget(client, auth_headers):
    bid = _create_budget(client, auth_headers, "proj-1")
    resp = client.post(f"/api/budget/{bid}/activate", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["budget"]["status"] == "active"
    resp = client.get("/api/budget/projects/proj-1/active", headers=auth_headers)
    assert resp.json()["budget"] is not None


def test_recalculate_budget(client, auth_headers):
    bid = _create_budget(client, auth_headers, "proj-1", "medium")
    resp = client.post(f"/api/budget/{bid}/recalculate?level=high", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["budget"]["budget_level"] == "high"


def test_archive_budget(client, auth_headers):
    bid = _create_budget(client, auth_headers, "proj-1")
    resp = client.post(f"/api/budget/{bid}/archive", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["budget"]["status"] == "archived"


def test_invalid_level(client, auth_headers):
    resp = client.post("/api/budget/projects/proj-1/generate?level=extreme", headers=auth_headers)
    assert resp.status_code == 400


def test_budget_not_found(client, auth_headers):
    resp = client.get("/api/budget/nonexistent", headers=auth_headers)
    assert resp.status_code == 404


def test_multiple_budgets_per_project(client, auth_headers):
    _create_budget(client, auth_headers, "proj-multi", "low")
    _create_budget(client, auth_headers, "proj-multi", "medium")
    _create_budget(client, auth_headers, "proj-multi", "high")
    resp = client.get("/api/budget/projects/proj-multi", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["budgets"]) == 3
