from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from schemas.comfyui_workflow_schema import (
    FALLBACK_CHAIN,
    WorkflowBuildResult,
    WorkflowFallbackReport,
    WorkflowProfile,
)
from services.comfyui_node_capability_service import validate_workflow_nodes

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "data" / "workflows" / "comfyui"

TEMPLATE_FILE_MAP: dict[WorkflowProfile, str] = {
    WorkflowProfile.smoke_light: "smoke_light.json",
    WorkflowProfile.storyboard_safe: "storyboard_safe.json",
}

PROFILE_TO_WORKFLOW_KEY: dict[WorkflowProfile, str] = {
    WorkflowProfile.smoke_light: "smoke_light",
    WorkflowProfile.storyboard_safe: "storyboard_safe",
    WorkflowProfile.storyboard_fast: "storyboard_safe",
    WorkflowProfile.production_quality: "storyboard_safe",
}


def load_template(profile: WorkflowProfile) -> dict[str, Any] | None:
    filename = TEMPLATE_FILE_MAP.get(profile)
    if not filename:
        return None

    path = TEMPLATES_DIR / filename
    if not path.exists():
        logger.warning("Template file not found: %s", path)
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load template %s: %s", path, exc)
        return None


def _copy_json(value: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value))


def _get_input_value(inputs: dict[str, Any], defaults: dict[str, Any], param_name: str) -> Any:
    if param_name in inputs:
        return inputs[param_name]
    if param_name == "positive_prompt":
        return inputs.get("prompt") or inputs.get("text") or defaults.get(param_name, "")
    if param_name == "sampler_name":
        return inputs.get("sampler_name") or inputs.get("sampler") or defaults.get(param_name)
    if param_name == "output_prefix":
        return inputs.get("output_prefix") or inputs.get("filename_prefix") or defaults.get(param_name)
    return defaults.get(param_name)


def build_prompt_from_template(template: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any] | None:
    prompt_template = template.get("prompt_template")
    if not isinstance(prompt_template, dict) or not prompt_template:
        return None

    params = template.get("parameters", {})
    defaults = template.get("defaults", {})
    result = _copy_json(prompt_template)

    for param_name, mapping in params.items():
        if not isinstance(mapping, dict):
            continue
        node_id = mapping.get("node")
        input_key = mapping.get("input")
        if not isinstance(node_id, str) or not isinstance(input_key, str):
            continue
        value = _get_input_value(inputs, defaults, param_name)
        if value is not None and node_id in result:
            result[node_id]["inputs"][input_key] = value

    return result


def _missing_nodes_report(
    *,
    requested_profile: WorkflowProfile,
    attempted_profile: WorkflowProfile,
    missing_nodes: list[str],
) -> WorkflowFallbackReport:
    return WorkflowFallbackReport(
        requested_profile=requested_profile.value,
        executed_profile=attempted_profile.value,
        fallback_applied=True,
        reason="missing_nodes",
        missing_nodes=missing_nodes,
        missing_models=[],
    )


def _non_template_report(
    *,
    requested_profile: WorkflowProfile,
    attempted_profile: WorkflowProfile,
    reason: str,
) -> WorkflowFallbackReport:
    return WorkflowFallbackReport(
        requested_profile=requested_profile.value,
        executed_profile=attempted_profile.value,
        fallback_applied=True,
        reason=reason,
        missing_nodes=[],
        missing_models=[],
    )


def select_workflow(
    workflow_key: str,
    requested_profile: str,
    inputs: dict[str, Any],
    available_nodes: set[str] | None = None,
    *,
    skip_node_validation: bool = False,
) -> tuple[dict[str, Any] | None, str, WorkflowFallbackReport | None, str]:
    try:
        current = WorkflowProfile(requested_profile)
    except ValueError:
        current = WorkflowProfile.storyboard_safe

    original = current
    latest_report: WorkflowFallbackReport | None = None

    while current is not None:
        template = load_template(current)
        if template is None:
            latest_report = _non_template_report(
                requested_profile=original,
                attempted_profile=current,
                reason="profile_not_implemented" if current not in TEMPLATE_FILE_MAP else "template_not_found",
            )
            current = FALLBACK_CHAIN.get(current)
            continue

        prompt = build_prompt_from_template(template, inputs)
        if prompt is None:
            latest_report = _non_template_report(
                requested_profile=original,
                attempted_profile=current,
                reason="template_not_found",
            )
            current = FALLBACK_CHAIN.get(current)
            continue

        if not skip_node_validation:
            if available_nodes is None:
                latest_report = _non_template_report(
                    requested_profile=original,
                    attempted_profile=current,
                    reason="capability_check_unavailable",
                )
                current = FALLBACK_CHAIN.get(current)
                continue

            missing_nodes = validate_workflow_nodes(prompt, available_nodes)
            if missing_nodes:
                latest_report = _missing_nodes_report(
                    requested_profile=original,
                    attempted_profile=current,
                    missing_nodes=missing_nodes,
                )
                current = FALLBACK_CHAIN.get(current)
                continue

        if latest_report is not None and current == original:
            latest_report = None
        elif latest_report is not None:
            latest_report.executed_profile = current.value

        return prompt, PROFILE_TO_WORKFLOW_KEY.get(current, workflow_key), latest_report, current.value

    final_report = latest_report or WorkflowFallbackReport(
        requested_profile=original.value,
        executed_profile="none",
        fallback_applied=True,
        reason="no_viable_profile",
        missing_nodes=[],
        missing_models=[],
    )
    return None, "", final_report, "none"


def select_workflow_build_result(
    workflow_key: str,
    requested_profile: str,
    inputs: dict[str, Any],
    available_nodes: set[str] | None = None,
    *,
    skip_node_validation: bool = False,
) -> WorkflowBuildResult:
    prompt, executed_key, fallback_report, executed_profile = select_workflow(
        workflow_key=workflow_key,
        requested_profile=requested_profile,
        inputs=inputs,
        available_nodes=available_nodes,
        skip_node_validation=skip_node_validation,
    )
    return WorkflowBuildResult(
        prompt_payload=prompt or {},
        workflow_key=executed_key or workflow_key,
        requested_profile=requested_profile,
        executed_profile=executed_profile,
        fallback_report=fallback_report,
        metadata_injected=False,
    )


def build_metadata_workflow_profile(
    requested_profile: str,
    executed_profile: str,
    fallback_report: WorkflowFallbackReport | None,
    *,
    available_node_count: int | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "workflow_profile_requested": requested_profile,
        "workflow_profile_executed": executed_profile,
    }

    if available_node_count is not None:
        metadata["available_node_count"] = available_node_count

    fallback_payload = (
        fallback_report.model_dump()
        if fallback_report is not None
        else {
            "requested_profile": requested_profile,
            "executed_profile": executed_profile,
            "fallback_applied": False,
            "reason": "none",
            "missing_nodes": [],
            "missing_models": [],
        }
    )
    metadata["workflow_fallback_report"] = fallback_payload
    metadata["missing_nodes"] = list(fallback_payload.get("missing_nodes") or [])

    return metadata
