from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.qdrant_service import qdrant_service  # noqa: E402


@pytest.mark.asyncio
async def test_qdrant_semantic_search_returns_result_list(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_post(*args, **kwargs):
        class Response:
            status_code = 200

            @staticmethod
            def json():
                return {"result": [{"id": "1", "score": 0.8, "payload": {"chunk_text": "hello"}}]}

            text = "ok"

        return Response()

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        post = staticmethod(fake_post)

    monkeypatch.setattr("services.qdrant_service.httpx.AsyncClient", lambda timeout: FakeClient())
    results = await qdrant_service.semantic_search(collection="x", query_vector=[0.1, 0.2], limit=2)
    assert isinstance(results, list)
    assert results
