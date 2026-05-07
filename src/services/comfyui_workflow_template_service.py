from __future__ import annotations

import json
from pathlib import Path
from typing import Any


WORKFLOWS_DIR = Path(__file__).resolve().parents[1] / "comfyui_workflows"
DEFAULT_POSITIVE_PROMPT = (
    "cinematic storyboard frame, professional film previsualization, realistic lighting, clear composition"
)
DEFAULT_NEGATIVE_PROMPT = "low quality, blurry, distorted, watermark, text, logo, bad anatomy"
DEFAULT_SEED = 0

NUMERIC_PLACEHOLDERS = {
    "{{WIDTH}}": int,
    "{{HEIGHT}}": int,
    "{{STEPS}}": int,
    "{{SEED}}": int,
    "{{CFG}}": float,
}

STRING_PLACEHOLDERS = {
    "{{CHECKPOINT_NAME}}",
    "{{POSITIVE_PROMPT}}",
    "{{NEGATIVE_PROMPT}}",
    "{{SAMPLER}}",
    "{{SCHEDULER}}",
}


def _extract_pipeline(plan: dict[str, Any]) -> dict[str, Any]:
    if isinstance(plan.get("pipeline"), dict):
        return plan["pipeline"]
    if plan.get("workflow_id"):
        return plan
    raise ValueError("A pipeline payload is required to compile a workflow template")


def get_workflow_template_path(workflow_id: str) -> Path:
    if not workflow_id:
        raise ValueError("workflow_id is required")

    template_path = WORKFLOWS_DIR / f"{workflow_id}.template.json"
    if not template_path.exists():
        raise FileNotFoundError(f"Workflow template not found for '{workflow_id}': {template_path}")
    return template_path


def load_workflow_template(workflow_id: str) -> dict[str, Any]:
    template_path = get_workflow_template_path(workflow_id)
    try:
        return json.loads(template_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Workflow template is not valid JSON: {template_path}") from exc


def _replace_placeholders(value: Any, replacements: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {key: _replace_placeholders(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_placeholders(item, replacements) for item in value]
    if isinstance(value, str):
        if value in replacements:
            return replacements[value]
        updated = value
        for placeholder, replacement in replacements.items():
            if isinstance(replacement, (str, int, float)):
                updated = updated.replace(placeholder, str(replacement))
        return updated
    return value


def _missing_placeholders(value: Any) -> list[str]:
    missing: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for item in node.values():
                visit(item)
        elif isinstance(node, list):
            for item in node:
                visit(item)
        elif isinstance(node, str) and "{{" in node and "}}" in node:
            missing.append(node)

    visit(value)
    return sorted(set(missing))


def compile_workflow_template(
    plan: dict[str, Any],
    prompt: str,
    negative_prompt: str | None = None,
) -> dict[str, Any]:
    pipeline = _extract_pipeline(plan)
    workflow_id = pipeline.get("workflow_id")
    if not workflow_id:
        raise ValueError("pipeline.workflow_id is required")
    if not pipeline.get("checkpoint"):
        raise ValueError("pipeline.checkpoint is required")
    if pipeline.get("lora") is not None:
        raise ValueError("pipeline.lora must be null for template compilation")
    if pipeline.get("loras") != []:
        raise ValueError("pipeline.loras must be an empty list for template compilation")

    params = pipeline.get("params") or {}
    for key in ("width", "height", "steps", "cfg"):
        if params.get(key) in (None, ""):
            raise ValueError(f"pipeline.params.{key} is required")

    template = load_workflow_template(workflow_id)
    replacements: dict[str, Any] = {
        "{{CHECKPOINT_NAME}}": pipeline["checkpoint"],
        "{{POSITIVE_PROMPT}}": prompt or DEFAULT_POSITIVE_PROMPT,
        "{{NEGATIVE_PROMPT}}": negative_prompt or DEFAULT_NEGATIVE_PROMPT,
        "{{WIDTH}}": int(params["width"]),
        "{{HEIGHT}}": int(params["height"]),
        "{{STEPS}}": int(params["steps"]),
        "{{CFG}}": float(params["cfg"]),
        "{{SAMPLER}}": str(params.get("sampler") or "dpmpp_2m"),
        "{{SCHEDULER}}": str(params.get("scheduler") or "karras"),
        "{{SEED}}": int(params.get("seed", DEFAULT_SEED)),
    }

    compiled = _replace_placeholders(template, replacements)
    missing = _missing_placeholders(compiled)
    if missing:
        raise ValueError(f"Unresolved placeholders remain in compiled workflow: {missing}")

    return compiled


def validate_compiled_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(workflow, dict) or not workflow:
        raise ValueError("Compiled workflow must be a non-empty dictionary")

    missing_placeholders = _missing_placeholders(workflow)
    required_nodes = {"CheckpointLoaderSimple", "CLIPTextEncode", "EmptyLatentImage", "KSampler", "VAEDecode", "SaveImage"}
    present_nodes = {
        node.get("class_type")
        for node in workflow.values()
        if isinstance(node, dict)
    }
    missing_nodes = sorted(required_nodes - present_nodes)
    if missing_nodes:
        raise ValueError(f"Compiled workflow is missing required nodes: {missing_nodes}")

    return {
        "valid": not missing_placeholders and not missing_nodes,
        "missing_placeholders": missing_placeholders,
        "node_count": len(workflow),
    }


def build_compiled_workflow_preview(
    plan: dict[str, Any],
    prompt: str | None = None,
    negative_prompt: str | None = None,
) -> dict[str, Any]:
    pipeline = _extract_pipeline(plan)
    workflow_id = pipeline.get("workflow_id")
    template_path = get_workflow_template_path(workflow_id)
    compiled_workflow = compile_workflow_template(
        plan=plan,
        prompt=prompt or DEFAULT_POSITIVE_PROMPT,
        negative_prompt=negative_prompt or DEFAULT_NEGATIVE_PROMPT,
    )
    validation = validate_compiled_workflow(compiled_workflow)

    return {
        "status": "ok",
        "workflow_id": workflow_id,
        "template_path": str(template_path),
        "ready_for_comfyui_prompt": True,
        "requires_template_mapping": False,
        "template_mapping_status": "compiled",
        "compiled_workflow": compiled_workflow,
        "validation": validation,
        "seed_note": "Seed is a placeholder value for dry-run compilation.",
    }
