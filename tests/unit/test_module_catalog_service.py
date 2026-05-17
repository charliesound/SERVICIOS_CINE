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
def _reset_module_catalog():
    from services.module_catalog_service import module_catalog_service

    module_catalog_service.reload_catalog()


def test_catalog_loads_expected_modules():
    from services.module_catalog_service import module_catalog_service

    catalog = module_catalog_service.get_module_catalog()
    assert len(catalog) == 14
    assert any(module.key == "core" for module in catalog)
    assert any(module.key == "delivery_distribution" for module in catalog)


def test_all_module_keys_are_unique():
    from services.module_catalog_service import module_catalog_service

    keys = [module.key for module in module_catalog_service.get_module_catalog()]
    assert len(keys) == len(set(keys))


def test_all_dependencies_point_to_existing_modules():
    from services.module_catalog_service import module_catalog_service

    keys = {module.key for module in module_catalog_service.get_module_catalog()}
    for module in module_catalog_service.get_module_catalog():
        for dependency in module.dependencies:
            assert dependency in keys


def test_known_plan_returns_enabled_and_locked_modules():
    from services.module_catalog_service import module_catalog_service

    enabled = {module.key for module in module_catalog_service.get_modules_for_plan("producer")}
    locked = {module.key for module in module_catalog_service.get_locked_modules_for_plan("producer")}

    assert "core" in enabled
    assert "script_analysis" in enabled
    assert "pitch_deck" in enabled
    assert "funding_grants" in enabled
    assert "storyboard_ai" in locked
    assert "pipeline_builder" in locked


def test_module_access_state_reports_missing_feature():
    from services.module_catalog_service import module_catalog_service

    state = module_catalog_service.get_module_access_state("free", "storyboard_ai")
    assert state.enabled is False
    assert state.locked_reason == "plan_feature_missing"


def test_missing_module_returns_controlled_error():
    from services.module_catalog_service import ModuleNotFoundError, module_catalog_service

    with pytest.raises(ModuleNotFoundError):
        module_catalog_service.get_module_by_key("does_not_exist")


def test_missing_plan_returns_controlled_error():
    from services.module_catalog_service import ModulePlanError, module_catalog_service

    with pytest.raises(ModulePlanError):
        module_catalog_service.get_modules_for_plan("unknown_plan")
