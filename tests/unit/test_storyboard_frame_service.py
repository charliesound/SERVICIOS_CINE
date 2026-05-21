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


def _make_path_only_asset(
    *,
    canonical_path: str = "",
    content_ref: str | None = None,
    relative_path: str = "",
):
    return SimpleNamespace(
        id="asset-path",
        canonical_path=canonical_path,
        content_ref=content_ref,
        relative_path=relative_path,
    )


@pytest.fixture
def docker_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    docker_data_root = tmp_path / "docker" / "data"
    docker_output_root = docker_data_root / "output"
    host_data_prefix = "/opt/SERVICIOS_CINE/data/"
    host_output_prefix = "/opt/SERVICIOS_CINE/data/output/"

    monkeypatch.setattr(storyboard_frame_service, "_DOCKER_DATA_ROOT", docker_data_root)
    monkeypatch.setattr(storyboard_frame_service, "_DOCKER_OUTPUT_ROOT", docker_output_root)
    monkeypatch.setattr(storyboard_frame_service, "_HOST_DATA_PREFIX", host_data_prefix)
    monkeypatch.setattr(storyboard_frame_service, "_HOST_OUTPUT_PREFIX", host_output_prefix)
    monkeypatch.setattr(
        storyboard_frame_service, "_ALLOWED_DATA_ROOTS", (docker_data_root,)
    )

    return {
        "docker_data_root": docker_data_root,
        "docker_output_root": docker_output_root,
    }


def test_resolve_image_path_uses_valid_canonical_path(tmp_path: Path) -> None:
    image_path = tmp_path / "canonical.png"
    image_path.write_bytes(b"ok")
    asset = _make_path_only_asset(canonical_path=str(image_path))

    resolved_path, attempted = storyboard_frame_service._resolve_image_path(asset, {})

    assert resolved_path == str(image_path)
    assert attempted == [str(image_path)]


def test_resolve_image_path_converts_host_canonical_to_docker(docker_roots: dict[str, Path]) -> None:
    relative_path = "storyboards/scene_01/frame_01.png"
    docker_file = docker_roots["docker_output_root"] / relative_path
    docker_file.parent.mkdir(parents=True, exist_ok=True)
    docker_file.write_bytes(b"ok")

    host_canonical = f"/opt/SERVICIOS_CINE/data/output/{relative_path}"
    asset = _make_path_only_asset(canonical_path=host_canonical)

    resolved_path, attempted = storyboard_frame_service._resolve_image_path(asset, {})

    assert resolved_path == str(docker_file)
    assert attempted[0].replace("\\", "/") == host_canonical


def test_resolve_image_path_converts_metadata_storage_path_to_docker(docker_roots: dict[str, Path]) -> None:
    relative_path = "storyboards/scene_02/frame_03.png"
    docker_file = docker_roots["docker_output_root"] / relative_path
    docker_file.parent.mkdir(parents=True, exist_ok=True)
    docker_file.write_bytes(b"ok")

    metadata = {"storage_path": f"/opt/SERVICIOS_CINE/data/output/{relative_path}"}
    asset = _make_path_only_asset(canonical_path="")

    resolved_path, _attempted = storyboard_frame_service._resolve_image_path(asset, metadata)

    assert resolved_path == str(docker_file)


def test_resolve_image_path_converts_content_ref_file_uri_to_local_path(tmp_path: Path) -> None:
    image_path = tmp_path / "from_content_ref.png"
    image_path.write_bytes(b"ok")
    content_ref = f"file:///{image_path.as_posix()}"
    asset = _make_path_only_asset(canonical_path="", content_ref=content_ref)

    resolved_path, attempted = storyboard_frame_service._resolve_image_path(asset, {})

    assert resolved_path == str(image_path)
    attempted_normalized = [item.replace("\\", "/") for item in attempted]
    assert image_path.as_posix() in attempted_normalized


def test_resolve_image_path_converts_content_ref_host_file_uri_to_docker(docker_roots: dict[str, Path]) -> None:
    relative_path = "storyboards/scene_04/frame_09.png"
    docker_file = docker_roots["docker_output_root"] / relative_path
    docker_file.parent.mkdir(parents=True, exist_ok=True)
    docker_file.write_bytes(b"ok")

    content_ref = f"file:///opt/SERVICIOS_CINE/data/output/{relative_path}"
    asset = _make_path_only_asset(canonical_path="", content_ref=content_ref)

    resolved_path, _attempted = storyboard_frame_service._resolve_image_path(asset, {})

    assert resolved_path == str(docker_file)


def test_resolve_image_path_uses_relative_path_under_docker_output(docker_roots: dict[str, Path]) -> None:
    relative_path = "storyboards/scene_03/frame_07.png"
    docker_file = docker_roots["docker_output_root"] / relative_path
    docker_file.parent.mkdir(parents=True, exist_ok=True)
    docker_file.write_bytes(b"ok")
    asset = _make_path_only_asset(canonical_path="", relative_path=relative_path)

    resolved_path, _attempted = storyboard_frame_service._resolve_image_path(asset, {})

    assert resolved_path == str(docker_file)


def test_resolve_image_path_returns_none_when_no_candidate_exists(docker_roots: dict[str, Path]) -> None:
    asset = _make_path_only_asset(canonical_path="/opt/SERVICIOS_CINE/data/output/storyboards/missing.png")

    resolved_path, attempted = storyboard_frame_service._resolve_image_path(asset, {})

    assert resolved_path is None
    assert attempted


def test_resolve_asset_thumbnail_path_uses_thumbnail_metadata(docker_roots: dict[str, Path]) -> None:
    thumbnail_path = docker_roots["docker_output_root"] / "thumbs" / "frame_01.webp"
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    thumbnail_path.write_bytes(b"ok")
    asset = _make_path_only_asset(canonical_path="")

    resolved_path = storyboard_frame_service.resolve_asset_thumbnail_path(
        asset,
        {
            "thumbnail_path": f"/opt/SERVICIOS_CINE/data/output/thumbs/frame_01.webp",
            "thumbnail_relative_path": "thumbs/frame_01.webp",
        },
    )

    assert resolved_path == str(thumbnail_path)


def test_is_allowed_media_path_rejects_outside_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir(parents=True, exist_ok=True)
    outside_file = tmp_path / "outside.png"
    outside_file.write_bytes(b"ok")
    monkeypatch.setattr(storyboard_frame_service, "_ALLOWED_DATA_ROOTS", (allowed_root,))

    assert storyboard_frame_service.is_allowed_media_path(outside_file) is False


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


def test_limit_frames_without_max_frames_keeps_all() -> None:
    frames = [SimpleNamespace(shot_number=index) for index in range(1, 6)]

    limited = storyboard_frame_service.limit_frames(frames, max_frames=None)

    assert [frame.shot_number for frame in limited] == [1, 2, 3, 4, 5]


def test_limit_frames_respects_max_frames() -> None:
    frames = [SimpleNamespace(shot_number=index) for index in range(1, 7)]

    limited = storyboard_frame_service.limit_frames(frames, max_frames=4)

    assert [frame.shot_number for frame in limited] == [1, 2, 3, 4]


def test_limit_frames_uses_available_frames_when_max_is_higher() -> None:
    frames = [SimpleNamespace(shot_number=index) for index in range(1, 4)]

    limited = storyboard_frame_service.limit_frames(frames, max_frames=8)

    assert [frame.shot_number for frame in limited] == [1, 2, 3]


def test_limit_frames_rejects_unsupported_selection_mode() -> None:
    frames = [SimpleNamespace(shot_number=1)]

    with pytest.raises(ValueError, match="Unsupported frame_selection_mode"):
        storyboard_frame_service.limit_frames(frames, max_frames=1, frame_selection_mode="latest")
