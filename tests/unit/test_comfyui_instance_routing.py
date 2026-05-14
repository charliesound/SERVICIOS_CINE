from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(autouse=True)
def _reset_registry():
    from services.instance_registry import registry

    registry._initialized = False
    registry.__init__()
    registry.load_config()


def _resolve(task_type: str):
    from services.instance_registry import registry

    backend = registry.resolve_backend_for_task(task_type)
    assert backend is not None
    return backend


def test_resolves_still_to_8188():
    assert _resolve("still").base_url.endswith(":8188")


def test_resolves_video_to_8189():
    assert _resolve("video").base_url.endswith(":8189")


def test_resolves_dubbing_to_8190():
    assert _resolve("dubbing").base_url.endswith(":8190")


def test_resolves_restoration_to_8191():
    assert _resolve("restoration").base_url.endswith(":8191")


def test_resolves_3d_to_8192():
    assert _resolve("3d").base_url.endswith(":8192")


def test_storyboard_realistic_resolves_to_still():
    assert _resolve("storyboard_realistic").type.value == "still"


def test_storyboard_sketch_resolves_to_lab():
    assert _resolve("storyboard_sketch").type.value == "lab"


def test_unknown_falls_back_to_still():
    assert _resolve("unknown_task").type.value == "still"


def test_env_override_for_video_base_url(monkeypatch):
    monkeypatch.setenv("COMFYUI_VIDEO_BASE_URL", "http://override-video:9999")
    from services.instance_registry import registry

    registry._initialized = False
    registry.__init__()
    registry.load_config()
    assert _resolve("video").base_url == "http://override-video:9999"


def test_env_override_for_3d_base_url(monkeypatch):
    monkeypatch.setenv("COMFYUI_3D_BASE_URL", "http://override-3d:9998")
    from services.instance_registry import registry

    registry._initialized = False
    registry.__init__()
    registry.load_config()
    assert _resolve("3d").base_url == "http://override-3d:9998"


def test_comfyui_api_client_no_longer_uses_hardcoded_default_when_env_missing(tmp_path, monkeypatch):
    from services.instance_registry import registry
    from services.comfyui_api_client_service import get_comfyui_base_url

    monkeypatch.delenv("COMFYUI_STORYBOARD_BASE_URL", raising=False)
    monkeypatch.delenv("COMFYUI_STILL_BASE_URL", raising=False)
    monkeypatch.delenv("COMFYUI_BASE_URL", raising=False)

    source_cfg = ROOT / "src" / "config" / "instances.yml"
    data = yaml.safe_load(source_cfg.read_text(encoding="utf-8"))
    data["backends"]["still"]["base_url"] = "http://registry-routed:8188"

    temp_cfg = tmp_path / "instances.yml"
    temp_cfg.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    registry._initialized = False
    registry.__init__()
    registry.load_config(config_path=str(temp_cfg))

    assert get_comfyui_base_url() == "http://registry-routed:8188"


def test_has_task_mapping_for_storyboard_true():
    from services.instance_registry import registry

    assert registry.has_task_mapping("storyboard") is True


def test_has_task_mapping_for_unknown_false():
    from services.instance_registry import registry

    assert registry.has_task_mapping("nonexistent_task_type_xyz") is False


def test_backend_key_for_task_expected_mappings():
    from services.instance_registry import registry

    assert registry.backend_key_for_task("storyboard") == "still"
    assert registry.backend_key_for_task("video") == "video"
    assert registry.backend_key_for_task("cine") == "video"
    assert registry.backend_key_for_task("dubbing") == "dubbing"
    assert registry.backend_key_for_task("audio") == "dubbing"
    assert registry.backend_key_for_task("restoration") == "restoration"
    assert registry.backend_key_for_task("cleanup") == "restoration"
    assert registry.backend_key_for_task("3d") == "3d"
    assert registry.backend_key_for_task("scene_3d") == "3d"


def test_tasks_for_backend_video_contains_expected_tasks():
    from services.instance_registry import registry

    tasks = set(registry.tasks_for_backend("video"))
    assert {"video", "cine", "text_to_video"}.issubset(tasks)


def test_tasks_for_backend_3d_contains_expected_tasks():
    from services.instance_registry import registry

    tasks = set(registry.tasks_for_backend("3d"))
    assert {"3d", "scene_3d", "depth"}.issubset(tasks)
