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


@pytest.fixture(autouse=True)
def _reset_registry():
    from services.comfyui_instance_registry_service import registry
    from services.instance_registry import registry as unified_registry

    registry._initialized = False
    registry.__init__()
    unified_registry._initialized = False
    unified_registry.__init__()
    registry.load_instances()


def test_load_instances_uses_unified_registry():
    from services.comfyui_instance_registry_service import registry
    from services.instance_registry import registry as unified_registry

    registry.load_instances(config_path="/tmp/ignored_legacy_path.yml")
    assert len(unified_registry.get_all_backends()) == 6
    assert len(registry.get_all_instances()) == 6


def test_get_all_instances_returns_legacy_keys():
    from services.comfyui_instance_registry_service import registry

    keys = set(registry.get_all_instances().keys())
    assert keys == {
        "image",
        "video_cine",
        "dubbing_audio",
        "restoration",
        "three_d",
        "lab",
    }


def test_get_instance_legacy_key_image_maps_to_still():
    from services.comfyui_instance_registry_service import registry

    rec = registry.get_instance("image")
    assert rec is not None
    assert rec.key == "image"
    assert rec.port == 8188


def test_get_instance_legacy_key_three_d_maps_to_3d():
    from services.comfyui_instance_registry_service import registry

    rec = registry.get_instance("three_d")
    assert rec is not None
    assert rec.key == "three_d"
    assert rec.port == 8192


def test_get_instance_unified_key_3d_also_works():
    from services.comfyui_instance_registry_service import registry

    rec = registry.get_instance("3d")
    assert rec is not None
    assert rec.key == "three_d"
    assert rec.port == 8192


def test_get_instance_for_task_i2v_maps_to_video():
    from services.comfyui_instance_registry_service import registry

    rec = registry.get_instance_for_task("i2v")
    assert rec is not None
    assert rec.key == "video_cine"
    assert rec.port == 8189


def test_get_instance_for_task_lipsync_maps_to_dubbing():
    from services.comfyui_instance_registry_service import registry

    rec = registry.get_instance_for_task("lipsync")
    assert rec is not None
    assert rec.key == "dubbing_audio"
    assert rec.port == 8190


def test_get_instance_for_task_upscale_maps_to_restoration():
    from services.comfyui_instance_registry_service import registry

    rec = registry.get_instance_for_task("upscale")
    assert rec is not None
    assert rec.key == "restoration"
    assert rec.port == 8191


def test_get_instance_for_task_mesh_maps_to_three_d():
    from services.comfyui_instance_registry_service import registry

    rec = registry.get_instance_for_task("mesh")
    assert rec is not None
    assert rec.key == "three_d"
    assert rec.port == 8192


def test_get_instance_for_unknown_task_returns_none():
    from services.comfyui_instance_registry_service import registry

    assert registry.get_instance_for_task("nonexistent_task_type_xyz") is None


@pytest.mark.asyncio
async def test_health_result_shape_is_legacy_compatible(monkeypatch):
    from services.comfyui_instance_registry_service import registry
    from services.instance_registry import registry as unified_registry

    async def _fake_check_health(_backend_key: str) -> bool:
        return True

    monkeypatch.setattr(unified_registry, "check_health", _fake_check_health)
    result = await registry.check_instance_health("image", timeout=1.5)

    assert result["instance_key"] == "image"
    assert result["status"] == "online"
    assert result["healthy"] is True
    assert "instance_name" in result
    assert "base_url" in result
    assert result["detail"] == {"timeout_seconds": 1.5}


@pytest.mark.asyncio
async def test_all_health_result_shape_is_legacy_compatible(monkeypatch):
    from services.comfyui_instance_registry_service import registry
    from services.instance_registry import registry as unified_registry

    async def _fake_check_all_health() -> dict[str, bool]:
        return {
            "still": True,
            "video": False,
            "dubbing": True,
            "restoration": False,
            "3d": True,
            "lab": True,
        }

    monkeypatch.setattr(unified_registry, "check_all_health", _fake_check_all_health)
    results = await registry.check_all_instances_health(timeout=2.0)

    assert len(results) == 6
    keys = {item["instance_key"] for item in results}
    assert keys == {
        "image",
        "video_cine",
        "dubbing_audio",
        "restoration",
        "three_d",
        "lab",
    }
    for item in results:
        assert "instance_name" in item
        assert "base_url" in item
        assert item["status"] in {"online", "offline"}
        assert isinstance(item["healthy"], bool)
        assert item["detail"] == {"timeout_seconds": 2.0}
