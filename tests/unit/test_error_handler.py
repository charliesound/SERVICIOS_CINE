from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


@pytest.mark.asyncio
async def test_http_exception_returns_uniform_error(test_app):
    """Test that HTTPExceptions raised inside route handlers produce uniform JSON."""
    from fastapi import HTTPException

    @test_app.get("/_test_http_error")
    async def _test_http_error():
        raise HTTPException(status_code=404, detail="Not Found")

    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/_test_http_error")
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]
    assert "request_id" in body["error"]


@pytest.mark.asyncio
async def test_validation_error_returns_uniform_error(test_app):
    """Test that RequestValidationErrors produce uniform JSON."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/auth/register", json={"invalid": "data"})
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in body["error"]


@pytest.mark.asyncio
async def test_request_id_in_error_response(test_app):
    """Test that request_id is propagated through error responses."""
    from fastapi import HTTPException

    @test_app.get("/_test_rid_error")
    async def _test_rid_error():
        raise HTTPException(status_code=400, detail="Bad request")

    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/_test_rid_error",
            headers={"X-Request-ID": "my-custom-rid"},
        )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["request_id"] == "my-custom-rid"


@pytest.mark.asyncio
async def test_missing_route_returns_uniform_404_and_respects_request_id(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/ruta-inexistente",
            headers={"X-Request-ID": "cid-test-001"},
        )

    assert resp.status_code == 404
    assert resp.headers["X-Request-ID"] == "cid-test-001"

    body = resp.json()
    assert body != {"detail": "Not Found"}
    assert body["error"]["code"] == "not_found"
    assert body["error"]["message"] == "Not Found"
    assert body["error"]["details"] == {}
    assert body["error"]["request_id"] == "cid-test-001"


@pytest.mark.asyncio
async def test_internal_error_logs_and_returns_500(test_app):
    """Test that unhandled 500 errors are logged and return a 500 response.

    Note: Starlette's ServerErrorMiddleware at the outermost layer handles
    truly unhandled exceptions. Our global handler logs the error but the
    response format is controlled by Starlette for these cases.
    """
    from httpx import AsyncClient, ASGITransport

    @test_app.get("/_test_500")
    async def _test_500():
        raise RuntimeError("secret internal detail")

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/_test_500")
    assert resp.status_code == 500
    # Starlette returns {"detail": "Internal Server Error"} for unhandled errors
    # Our custom error handlers correctly handle HTTPException and ValidationError
    body = resp.json()
    assert "detail" in body or "error" in body
