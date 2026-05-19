from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from routes import storyboard_routes
from services.storyboard_pdf_export_service import storyboard_pdf_export_service


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x03\x00\x01"
    b"+\tM\x84\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.mark.asyncio
async def test_storyboard_zip_includes_manifest_and_pdf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    shot_file = tmp_path / "shot.png"
    shot_file.write_bytes(PNG_1X1)

    shots = [
        SimpleNamespace(
            id="shot-b",
            sequence_order=2,
            scene_number=1,
            sequence_id="seq_01",
            asset_id="asset-b",
            visual_mode="hand_drawn_storyboard",
            narrative_text="second shot",
            metadata_json={"validation_score": 0.8},
        ),
        SimpleNamespace(
            id="shot-a",
            sequence_order=1,
            scene_number=1,
            sequence_id="seq_01",
            asset_id="asset-a",
            visual_mode="hand_drawn_storyboard",
            narrative_text="first shot",
            metadata_json={"validation_score": 0.9},
        ),
    ]

    async def fake_get_sequence_storyboard(*args, **kwargs):
        return {"sequence_id": "seq_01"}, shots

    async def fake_get_project(*args, **kwargs):
        return SimpleNamespace(name="Project Test")

    async def fake_get_asset_preview_payload(*args, **kwargs):
        return {"kind": "file", "path": str(shot_file), "filename": "frame.png"}

    monkeypatch.setattr(storyboard_routes.storyboard_service, "get_sequence_storyboard", fake_get_sequence_storyboard)
    monkeypatch.setattr(storyboard_routes.storyboard_service, "_get_project_for_tenant", fake_get_project)
    from services.presentation_service import presentation_service

    monkeypatch.setattr(presentation_service, "get_asset_preview_payload", fake_get_asset_preview_payload)

    response = await storyboard_routes.export_sequence_storyboard_zip(
        project_id="proj-1",
        sequence_id="seq_01",
        db=SimpleNamespace(),
        tenant=SimpleNamespace(),
    )

    archive = zipfile.ZipFile(io.BytesIO(response.body), "r")
    names = set(archive.namelist())
    assert "storyboard_manifest.json" in names
    assert "storyboard_contact_sheet.pdf" in names

    manifest = json.loads(archive.read("storyboard_manifest.json").decode("utf-8"))
    assert manifest["sequence_id"] == "seq_01"
    assert manifest["total_shots"] == 2
    assert manifest["shots"][0]["sequence_order"] == 1


def test_pdf_generates_when_image_is_missing() -> None:
    pdf = storyboard_pdf_export_service.render_contact_sheet_pdf(
        project_name="Project",
        sequence_id="seq_01",
        exported_at="2026-05-19T00:00:00Z",
        shots=[
            {
                "shot_id": "shot-1",
                "sequence_order": 1,
                "scene_number": 1,
                "sequence_id": "seq_01",
                "render_status": "missing_file",
                "style_preset": "hand_drawn_storyboard",
                "prompt_brief": "test",
                "file_path": "/path/does/not/exist.png",
            }
        ],
    )
    assert isinstance(pdf, bytes)
    assert len(pdf) > 100
