from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scripts.ingest_screenwriting_theory import run_ingest  # noqa: E402


@pytest.mark.asyncio
async def test_ingestion_builds_points_and_upserts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    theory_dir = tmp_path / "data" / "theory" / "screenwriting"
    theory_dir.mkdir(parents=True)
    (theory_dir / "author-title.txt").write_text("INT. CASA - DÍA\nAcción dramática", encoding="utf-8")

    async def fake_embed_texts(texts):
        return [[0.1, 0.2, 0.3] for _ in texts], "ollama"

    async def fake_create_collection(*, name, vector_size, distance="Cosine"):
        return True

    async def fake_upsert_points(*, collection, points):
        return len(points) > 0

    monkeypatch.setattr("scripts.ingest_screenwriting_theory.project_document_rag_service._embed_texts", fake_embed_texts)
    monkeypatch.setattr("scripts.ingest_screenwriting_theory.qdrant_service.create_collection", fake_create_collection)
    monkeypatch.setattr("scripts.ingest_screenwriting_theory.qdrant_service.upsert_points", fake_upsert_points)

    result = await run_ingest(theory_dir)
    assert result["status"] == "ok"
    assert result["points"] > 0
