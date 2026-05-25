from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import yaml

from core.config import get_settings
from services.plan_limits_service import plan_limits_service


CID_CORE_HIDDEN_MODULE_KEYS = {
    "sound_post_ai",
}


class ModuleCatalogError(Exception):
    """Base error for module catalog operations."""


class ModuleNotFoundError(ModuleCatalogError):
    """Raised when a module key does not exist in the catalog."""


class ModulePlanError(ModuleCatalogError):
    """Raised when a referenced plan does not exist."""


class ModuleDependencyError(ModuleCatalogError):
    """Raised when module dependencies are invalid or unresolved."""


@dataclass(frozen=True)
class ModuleDefinition:
    key: str
    name: str
    short_description: str
    category: str
    status: str
    commercial_status: str
    requires_gpu: bool
    requires_local_gpu_node: bool
    default_enabled: bool
    visible_in_catalog: bool
    dependencies: list[str]
    recommended_pack: Optional[str]
    route_prefixes: list[str]
    feature_flag_key: Optional[str]


@dataclass(frozen=True)
class ModuleAccessState:
    enabled: bool
    locked_reason: Optional[str] = None


class ModuleCatalogService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._modules: dict[str, ModuleDefinition] = {}
        self._load_catalog()

    def _catalog_path(self, config_path: Optional[str] = None) -> Path:
        if config_path:
            return Path(config_path)
        return Path(__file__).parent.parent / "config" / "modules.yml"

    def _load_catalog(self, config_path: Optional[str] = None) -> None:
        path = self._catalog_path(config_path)
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        raw_modules = data.get("modules") or {}
        if not isinstance(raw_modules, dict):
            raise ModuleCatalogError("modules.yml must define a top-level 'modules' mapping")

        loaded: dict[str, ModuleDefinition] = {}
        seen_keys: set[str] = set()
        for module_key, module_data in raw_modules.items():
            if not isinstance(module_data, dict):
                raise ModuleCatalogError(f"Invalid module definition for '{module_key}'")

            declared_key = str(module_data.get("key") or "").strip()
            if not declared_key:
                raise ModuleCatalogError(f"Module '{module_key}' is missing its internal key")
            if declared_key != module_key:
                raise ModuleCatalogError(
                    f"Module '{module_key}' has mismatched key '{declared_key}'"
                )
            if declared_key in seen_keys:
                raise ModuleCatalogError(f"Duplicate module key '{declared_key}'")
            seen_keys.add(declared_key)

            loaded[module_key] = ModuleDefinition(
                key=declared_key,
                name=str(module_data.get("name") or declared_key),
                short_description=str(module_data.get("short_description") or "").strip(),
                category=str(module_data.get("category") or "general").strip(),
                status=str(module_data.get("status") or "PENDIENTE").strip(),
                commercial_status=str(module_data.get("commercial_status") or "PENDIENTE").strip(),
                requires_gpu=bool(module_data.get("requires_gpu", False)),
                requires_local_gpu_node=bool(module_data.get("requires_local_gpu_node", False)),
                default_enabled=bool(module_data.get("default_enabled", False)),
                visible_in_catalog=bool(module_data.get("visible_in_catalog", True)),
                dependencies=[str(dep).strip() for dep in module_data.get("dependencies", []) if str(dep).strip()],
                recommended_pack=(str(module_data.get("recommended_pack")).strip() if module_data.get("recommended_pack") else None),
                route_prefixes=[str(route).strip() for route in module_data.get("route_prefixes", []) if str(route).strip()],
                feature_flag_key=(str(module_data.get("feature_flag_key")).strip() if module_data.get("feature_flag_key") else None),
            )

        self._modules = loaded
        self._validate_catalog()

    def reload_catalog(self, config_path: Optional[str] = None) -> None:
        self._load_catalog(config_path)

    def _validate_catalog(self) -> None:
        for module in self._modules.values():
            if module.key in module.dependencies:
                raise ModuleDependencyError(
                    f"Module '{module.key}' cannot depend on itself"
                )
            for dependency in module.dependencies:
                if dependency not in self._modules:
                    raise ModuleDependencyError(
                        f"Module '{module.key}' depends on unknown module '{dependency}'"
                    )

        self._validate_cycles()

    def _validate_cycles(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def _dfs(module_key: str) -> None:
            if module_key in visited:
                return
            if module_key in visiting:
                raise ModuleDependencyError(
                    f"Circular dependency detected for module '{module_key}'"
                )

            visiting.add(module_key)
            for dependency in self._modules[module_key].dependencies:
                _dfs(dependency)
            visiting.remove(module_key)
            visited.add(module_key)

        for module_key in self._modules:
            _dfs(module_key)

    def _plan_order(self) -> list[str]:
        return list(plan_limits_service.get_all_plans().keys())

    def _validate_plan(self, plan_name: str):
        normalized_plan = (plan_name or "").strip().lower()
        if not normalized_plan:
            raise ModulePlanError("Plan name is required")
        plan = plan_limits_service.get_plan(normalized_plan)
        if plan is None:
            raise ModulePlanError(f"Plan '{plan_name}' not found")
        return normalized_plan, plan

    def _collect_plan_features(self, plan_name: str, seen: Optional[set[str]] = None) -> set[str]:
        normalized_plan, plan = self._validate_plan(plan_name)
        seen = seen or set()
        if normalized_plan in seen:
            return set()

        seen.add(normalized_plan)
        features = set(plan.features or [])
        if "all_lower_features" in features:
            features.discard("all_lower_features")
            plan_order = self._plan_order()
            idx = plan_order.index(normalized_plan)
            for lower_plan in plan_order[:idx]:
                features.update(self._collect_plan_features(lower_plan, seen))
        return features

    def get_module_catalog(self) -> list[ModuleDefinition]:
        return list(self._modules.values())

    def get_visible_modules(self) -> list[ModuleDefinition]:
        modules = [module for module in self.get_module_catalog() if module.visible_in_catalog]
        if get_settings().feature_cid_core_scope:
            modules = [
                module
                for module in modules
                if module.key not in CID_CORE_HIDDEN_MODULE_KEYS
            ]
        return modules

    def get_module_by_key(self, module_key: str) -> ModuleDefinition:
        module = self._modules.get(module_key)
        if module is None:
            raise ModuleNotFoundError(f"Module '{module_key}' not found")
        return module

    def get_module_access_state(
        self,
        plan_name: str,
        module_key: str,
        visited: Optional[set[str]] = None,
    ) -> ModuleAccessState:
        normalized_plan, _ = self._validate_plan(plan_name)
        module = self.get_module_by_key(module_key)

        visited = visited or set()
        if module.key in visited:
            raise ModuleDependencyError(
                f"Circular dependency detected while resolving '{module.key}'"
            )

        effective_features = self._collect_plan_features(normalized_plan)
        enabled_by_feature = bool(
            module.feature_flag_key and module.feature_flag_key in effective_features
        )
        enabled_by_default = module.default_enabled
        if not enabled_by_feature and not enabled_by_default:
            return ModuleAccessState(enabled=False, locked_reason="plan_feature_missing")

        next_visited = set(visited)
        next_visited.add(module.key)
        for dependency_key in module.dependencies:
            dependency_state = self.get_module_access_state(
                normalized_plan,
                dependency_key,
                next_visited,
            )
            if not dependency_state.enabled:
                return ModuleAccessState(
                    enabled=False,
                    locked_reason=f"dependency_locked:{dependency_key}",
                )

        return ModuleAccessState(enabled=True)

    def is_module_enabled_for_plan(self, plan_name: str, module_key: str) -> bool:
        return self.get_module_access_state(plan_name, module_key).enabled

    def get_modules_for_plan(self, plan_name: str) -> list[ModuleDefinition]:
        normalized_plan, _ = self._validate_plan(plan_name)
        return [
            module
            for module in self.get_visible_modules()
            if self.is_module_enabled_for_plan(normalized_plan, module.key)
        ]

    def get_locked_modules_for_plan(self, plan_name: str) -> list[ModuleDefinition]:
        normalized_plan, _ = self._validate_plan(plan_name)
        return [
            module
            for module in self.get_visible_modules()
            if not self.is_module_enabled_for_plan(normalized_plan, module.key)
        ]

    def ensure_module_access(self, plan_name: str, module_key: str) -> None:
        access_state = self.get_module_access_state(plan_name, module_key)
        if not access_state.enabled:
            normalized_plan, _ = self._validate_plan(plan_name)
            raise ModulePlanError(
                f"Module '{module_key}' is locked for plan '{normalized_plan}'"
            )

    def to_dict(self, module: ModuleDefinition) -> dict:
        return asdict(module)


module_catalog_service = ModuleCatalogService()
