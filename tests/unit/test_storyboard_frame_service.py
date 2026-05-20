from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.storyboard_frame_service import storyboard_frame_service  # noqa: E402


class _ScalarResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class _ExecuteResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return _ScalarResult(self._items)


class _FakeSession:
    def __init__(self, execute_results):
        self._execute_results = list(execute_results)

    async def execute(self, _query):
        return _ExecuteResult(self._execute_results.pop(0))


def _make_asset(tmp_path: Path, *, asset_id: str, job_id: str, created_at: str, meta: dict | None = None):
    image_path = tmp_path / f"{asset_id}.png"
    image_path.write_bytes(b"fake")
    return SimpleNamespace(
        id=asset_id,
        job_id=job_id,
        canonical_path=str(image_path),
        metadata_json=json.dumps(meta or {}),
        created_at=created_at,
        status="indexed",
    )


def _make_shot(asset_id: str, *, sequence_order: int, scene_number: int, shot_type: str = "CU"):
    return SimpleNamespace(
        id=f"shot-{asset_id}",
        asset_id=asset_id,
        sequence_order=sequence_order,
        scene_number=scene_number,
        scene_heading=f"INT. SCENE {scene_number}",
        shot_type=shot_type,
        narrative_text=f"Narrative {sequence_order}",
        metadata_json=json.dumps({"camera_motion": "locked", "notes": f"note-{sequence_order}"}),
    )


@pytest.mark.asyncio
async def test_collect_by_asset_ids_orders_frames(tmp_path: Path) -> None:
    assets = [
        _make_asset(tmp_path, asset_id="a2", job_id="job-1", created_at="2026-01-02T00:00:00", meta={"visual_bible": {"enabled": True}}),
        _make_asset(tmp_path, asset_id="a1", job_id="job-1", created_at="2026-01-01T00:00:00", meta={"workflow_profile": {"requested": "storyboard_safe"}}),
    ]
    shots = [
        _make_shot("a2", sequence_order=2, scene_number=1),
        _make_shot("a1", sequence_order=1, scene_number=1),
    ]
    session = _FakeSession([assets, shots])

    frames = await storyboard_frame_service.collect_by_asset_ids(session, ["a1", "a2"])

    assert [frame.shot_number for frame in frames] == [1, 2]
    assert frames[0].metadata.workflow_profile == {"requested": "storyboard_safe"}
    assert frames[1].metadata.visual_bible == {"enabled": True}
    assert frames[0].metadata.media_asset_id == "a1"
    assert frames[0].metadata.render_job_id == "job-1"
    assert frames[0].info.status == "indexed"


@pytest.mark.asyncio
async def test_collect_by_asset_ids_missing_image_raises_clear_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.png"
    asset = SimpleNamespace(
        id="a1",
        job_id="job-1",
        canonical_path=str(missing_path),
        metadata_json=json.dumps({}),
        created_at="2026-01-01T00:00:00",
    )
    shot = _make_shot("a1", sequence_order=1, scene_number=1)
    session = _FakeSession([[asset], [shot]])

    with pytest.raises(ValueError, match="No storyboard frames with existing image files were found"):
        await storyboard_frame_service.collect_by_asset_ids(session, ["a1"])
