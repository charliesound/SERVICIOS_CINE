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


@pytest.fixture(autouse=True)
def _reset_registry():
    from services.comfyui_instance_registry_service import registry

    registry._initialized = False
    registry.__init__()
    registry.load_instances()


def _yaml_path() -> Path:
    return ROOT / "src" / "config" / "comfyui_instances.yml"


class TestRegistryLoading:
    def test_loads_five_instances(self):
        from services.comfyui_instance_registry_service import registry

        instances = registry.get_all_instances()
        assert len(instances) == 5

    def test_expected_keys_present(self):
        from services.comfyui_instance_registry_service import registry

        keys = set(registry.get_all_instances().keys())
        expected = {"image", "video_cine", "dubbing_audio", "restoration", "three_d"}
        assert keys == expected

    def test_each_instance_has_required_fields(self):
        from services.comfyui_instance_registry_service import registry

        for key, rec in registry.get_all_instances().items():
            assert rec.key == key
            assert rec.name
            assert rec.base_url
            assert isinstance(rec.port, int)
            assert isinstance(rec.enabled, bool)
            assert isinstance(rec.task_types, list)
            assert rec.health_endpoint

    def test_image_instance_correct(self):
        from services.comfyui_instance_registry_service import registry

        img = registry.get_instance("image")
        assert img is not None
        assert img.name == "Image"
        assert img.port == 8188
        assert "image" in img.task_types
        assert "storyboard" in img.task_types
        assert "still" in img.task_types

    def test_video_cine_instance_correct(self):
        from services.comfyui_instance_registry_service import registry

        vc = registry.get_instance("video_cine")
        assert vc is not None
        assert vc.name == "Video/Cine"
        assert vc.port == 8189
        assert "video" in vc.task_types
        assert "i2v" in vc.task_types
        assert "t2v" in vc.task_types

    def test_dubbing_audio_instance_correct(self):
        from services.comfyui_instance_registry_service import registry

        da = registry.get_instance("dubbing_audio")
        assert da is not None
        assert da.name == "DubbingAudio"
        assert da.port == 8190
        assert "dubbing" in da.task_types
        assert "lipsync" in da.task_types
        assert "voice" in da.task_types

    def test_restoration_instance_correct(self):
        from services.comfyui_instance_registry_service import registry

        rs = registry.get_instance("restoration")
        assert rs is not None
        assert rs.name == "Restoration"
        assert rs.port == 8191
        assert "restoration" in rs.task_types
        assert "upscale" in rs.task_types

    def test_three_d_instance_correct(self):
        from services.comfyui_instance_registry_service import registry

        td = registry.get_instance("three_d")
        assert td is not None
        assert td.name == "3D"
        assert td.port == 8192
        assert "3d" in td.task_types
        assert "mesh" in td.task_types


class TestTaskResolution:
    def test_storyboard_resolves_to_image(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("storyboard")
        assert inst is not None
        assert inst.key == "image"

    def test_still_resolves_to_image(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("still")
        assert inst is not None
        assert inst.key == "image"

    def test_image_resolves_to_image(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("image")
        assert inst is not None
        assert inst.key == "image"

    def test_i2v_resolves_to_video_cine(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("i2v")
        assert inst is not None
        assert inst.key == "video_cine"

    def test_t2v_resolves_to_video_cine(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("t2v")
        assert inst is not None
        assert inst.key == "video_cine"

    def test_video_resolves_to_video_cine(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("video")
        assert inst is not None
        assert inst.key == "video_cine"

    def test_cine_resolves_to_video_cine(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("cine")
        assert inst is not None
        assert inst.key == "video_cine"

    def test_previz_resolves_to_video_cine(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("previz")
        assert inst is not None
        assert inst.key == "video_cine"

    def test_lipsync_resolves_to_dubbing_audio(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("lipsync")
        assert inst is not None
        assert inst.key == "dubbing_audio"

    def test_dubbing_resolves_to_dubbing_audio(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("dubbing")
        assert inst is not None
        assert inst.key == "dubbing_audio"

    def test_audio_resolves_to_dubbing_audio(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("audio")
        assert inst is not None
        assert inst.key == "dubbing_audio"

    def test_voice_resolves_to_dubbing_audio(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("voice")
        assert inst is not None
        assert inst.key == "dubbing_audio"

    def test_upscale_resolves_to_restoration(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("upscale")
        assert inst is not None
        assert inst.key == "restoration"

    def test_restoration_resolves_to_restoration(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("restoration")
        assert inst is not None
        assert inst.key == "restoration"

    def test_cleanup_resolves_to_restoration(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("cleanup")
        assert inst is not None
        assert inst.key == "restoration"

    def test_repair_resolves_to_restoration(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("repair")
        assert inst is not None
        assert inst.key == "restoration"

    def test_mesh_resolves_to_three_d(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("mesh")
        assert inst is not None
        assert inst.key == "three_d"

    def test_depth_resolves_to_three_d(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("depth")
        assert inst is not None
        assert inst.key == "three_d"

    def test_scene_resolves_to_three_d(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("scene")
        assert inst is not None
        assert inst.key == "three_d"

    def test_3d_resolves_to_three_d(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("3d")
        assert inst is not None
        assert inst.key == "three_d"

    def test_unknown_task_type_returns_none(self):
        from services.comfyui_instance_registry_service import registry

        inst = registry.get_instance_for_task("nonexistent_task_type_xyz")
        assert inst is None


class TestEnvOverride:
    def test_env_override_changes_url(self, monkeypatch):
        monkeypatch.setenv("COMFYUI_IMAGE_URL", "http://192.168.1.100:8188")
        from services.comfyui_instance_registry_service import registry

        registry._initialized = False
        registry.__init__()
        registry.load_instances()
        img = registry.get_instance("image")
        assert img is not None
        assert img.base_url == "http://192.168.1.100:8188"

    def test_env_override_video_cine(self, monkeypatch):
        monkeypatch.setenv("COMFYUI_VIDEO_CINE_URL", "http://10.0.0.1:8189")
        from services.comfyui_instance_registry_service import registry

        registry._initialized = False
        registry.__init__()
        registry.load_instances()
        vc = registry.get_instance("video_cine")
        assert vc is not None
        assert vc.base_url == "http://10.0.0.1:8189"


class TestHealthCheckOffline:
    @pytest.mark.asyncio
    async def test_offline_instance_does_not_crash_registry(self):
        from services.comfyui_instance_registry_service import registry

        result = await registry.check_instance_health("image", timeout=1.0)
        assert result is not None
        assert result["instance_key"] == "image"
        assert "healthy" in result
        assert "status" in result

    @pytest.mark.asyncio
    async def test_all_instances_health_offline_does_not_crash(self):
        from services.comfyui_instance_registry_service import registry

        results = await registry.check_all_instances_health(timeout=1.0)
        assert len(results) == 5
        for r in results:
            assert "instance_key" in r
            assert "healthy" in r
            assert "status" in r


class TestLoadInstancesEdgeCases:
    def test_load_instances_from_yaml_file(self):
        from services.comfyui_instance_registry_service import registry

        path = _yaml_path()
        registry.load_instances(config_path=str(path))
        instances = registry.get_all_instances()
        assert len(instances) == 5

    def test_get_instance_not_found(self):
        from services.comfyui_instance_registry_service import registry

        assert registry.get_instance("nonexistent") is None

    def test_get_instance_for_task_unknown(self):
        from services.comfyui_instance_registry_service import registry

        assert registry.get_instance_for_task("quantum_computing") is None
