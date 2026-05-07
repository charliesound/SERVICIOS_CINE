from __future__ import annotations

import json
import logging
import os
from typing import Any
from urllib import request as _urlreq

from services.comfyui_pipeline_builder_service import (
    build_optimal_comfyui_pipeline,
    build_storyboard_pipeline_plan,
    validate_selected_scenes,
)
from services.comfyui_workflow_template_service import build_compiled_workflow_preview


logger = logging.getLogger(__name__)
REAL_RENDER_BLOCKED_REASON = (
    "Real ComfyUI render is disabled. Run dry_run=true or enable real render explicitly in a future release."
)


class ComfyUIStoryboardRenderService:
    """Prepare storyboard render contracts without calling real ComfyUI render."""

    def __init__(self) -> None:
        self._base_url: str | None = None
        self._output_dir: str | None = None
        self._workflow: str | None = None
        self._default_width = 1344
        self._default_height = 768
        self._default_steps = 28
        self._default_cfg = 6.5
        self._default_sampler = "dpmpp_2m"
        self._default_scheduler = "karras"

    def _ensure_config(self) -> None:
        if self._base_url is None:
            self._base_url = os.environ.get(
                "COMFYUI_STORYBOARD_BASE_URL",
                "http://127.0.0.1:8188",
            )
            self._output_dir = os.environ.get(
                "COMFYUI_STORYBOARD_OUTPUT_DIR",
                "/opt/SERVICIOS_CINE/media/storyboards",
            )
            self._workflow = os.environ.get(
                "COMFYUI_STORYBOARD_WORKFLOW",
                "cinematic_storyboard_sdxl",
            )
            self._default_width = int(os.environ.get("COMFYUI_STORYBOARD_DEFAULT_WIDTH", "1344"))
            self._default_height = int(os.environ.get("COMFYUI_STORYBOARD_DEFAULT_HEIGHT", "768"))
            self._default_steps = int(os.environ.get("COMFYUI_STORYBOARD_DEFAULT_STEPS", "28"))
            self._default_cfg = float(os.environ.get("COMFYUI_STORYBOARD_DEFAULT_CFG", "6.5"))
            self._default_sampler = os.environ.get(
                "COMFYUI_STORYBOARD_DEFAULT_SAMPLER",
                "dpmpp_2m",
            )
            self._default_scheduler = os.environ.get(
                "COMFYUI_STORYBOARD_DEFAULT_SCHEDULER",
                "karras",
            )

    async def healthcheck(self) -> dict[str, Any]:
        self._ensure_config()
        try:
            request = _urlreq.Request(f"{self._base_url}/system_stats")
            with _urlreq.urlopen(request, timeout=5) as response:
                data = json.loads(response.read())
            device = data.get("system", {}).get("devices", [{}])[0]
            return {
                "available": True,
                "base_url": self._base_url,
                "device": device.get("name", "unknown"),
                "vram": device.get("vram_usage", {}).get("total", 0),
            }
        except Exception as exc:
            logger.warning("ComfyUI health check failed: %s", exc)
            return {
                "available": False,
                "base_url": self._base_url,
                "error": str(exc),
            }

    def _extract_pipeline(self, plan: dict[str, Any]) -> dict[str, Any]:
        pipeline = plan.get("pipeline") if isinstance(plan, dict) else None
        if isinstance(pipeline, dict):
            return pipeline
        if isinstance(plan, dict) and plan.get("workflow_id"):
            return plan
        raise ValueError("A valid pipeline payload is required")

    def validate_render_plan(self, plan: dict[str, Any]) -> None:
        pipeline = self._extract_pipeline(plan)
        selected_scenes = validate_selected_scenes(pipeline.get("selected_scenes"))
        params = pipeline.get("params") or {}

        if not pipeline.get("safe_to_render"):
            raise ValueError("safe_to_render must be true before preparing storyboard render")
        if not pipeline.get("workflow_id"):
            raise ValueError("pipeline.workflow_id is required")
        if not pipeline.get("checkpoint"):
            raise ValueError("pipeline.checkpoint is required")
        if pipeline.get("lora") is not None:
            raise ValueError("pipeline.lora must be null for this validation block")
        if pipeline.get("loras") != []:
            raise ValueError("pipeline.loras must be an empty list for this validation block")

        for key in ("width", "height", "steps", "cfg"):
            if params.get(key) in (None, ""):
                raise ValueError(f"pipeline.params.{key} is required")

        pipeline["selected_scenes"] = selected_scenes

    def build_comfyui_prompt_payload(
        self,
        plan: dict[str, Any],
        prompt: str | None = None,
        negative_prompt: str | None = None,
    ) -> dict[str, Any]:
        return self.build_comfyui_workflow_adapter_payload(
            plan=plan,
            prompt=prompt or "Storyboard prompt preview not provided in dry-run mode.",
            negative_prompt=negative_prompt,
        )

    def build_comfyui_workflow_adapter_payload(
        self,
        plan: dict[str, Any],
        prompt: str,
        negative_prompt: str | None = None,
    ) -> dict[str, Any]:
        self._ensure_config()
        pipeline = self._extract_pipeline(plan)
        params = dict(pipeline.get("params", {}))

        return {
            "workflow_id": pipeline.get("workflow_id"),
            "workflow_status": pipeline.get("workflow_status"),
            "checkpoint_used": pipeline.get("checkpoint"),
            "checkpoint": pipeline.get("checkpoint"),
            "vae_used": pipeline.get("vae"),
            "vae": pipeline.get("vae"),
            "model_family": pipeline.get("model_family"),
            "positive_prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "params": params,
            "selected_scenes": list(pipeline.get("selected_scenes", [])),
            "generation_mode": pipeline.get("generation_mode"),
            "safe_to_render": pipeline.get("safe_to_render"),
            "selection_reason": pipeline.get("reason"),
            "ready_for_comfyui_prompt": False,
            "requires_template_mapping": True,
            "template_mapping_status": "pending",
            "comfyui_request_preview": {
                "base_url": self._base_url,
                "workflow_name": pipeline.get("workflow_id"),
                "checkpoint": pipeline.get("checkpoint"),
                "vae": pipeline.get("vae"),
                "sampler": params.get("sampler", self._default_sampler),
                "scheduler": params.get("scheduler", self._default_scheduler),
                "width": params.get("width", self._default_width),
                "height": params.get("height", self._default_height),
                "steps": params.get("steps", self._default_steps),
                "cfg": params.get("cfg", self._default_cfg),
            },
        }

    def prepare_storyboard_render_request(
        self,
        project_id: str | None,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(payload.get("pipeline"), dict):
            plan = {
                "status": payload.get("status", "ok"),
                "project_id": project_id,
                "pipeline": payload["pipeline"],
            }
        else:
            if project_id is not None:
                plan = build_storyboard_pipeline_plan(project_id=project_id, payload=payload)
            else:
                plan = build_optimal_comfyui_pipeline(payload)

        self.validate_render_plan(plan)
        comfyui_payload_preview = self.build_comfyui_prompt_payload(
            plan,
            prompt=payload.get("prompt"),
            negative_prompt=payload.get("negative_prompt"),
        )

        try:
            compiled_workflow_preview = build_compiled_workflow_preview(
                plan=plan,
                prompt=payload.get("prompt"),
                negative_prompt=payload.get("negative_prompt"),
            )
        except Exception as exc:
            compiled_workflow_preview = {
                "status": "error",
                "workflow_id": self._extract_pipeline(plan).get("workflow_id"),
                "ready_for_comfyui_prompt": False,
                "requires_template_mapping": True,
                "template_mapping_status": "failed",
                "error": str(exc),
            }

        return {
            "status": "planned",
            "dry_run": True,
            "project_id": project_id,
            "pipeline": self._extract_pipeline(plan),
            "comfyui_payload_preview": comfyui_payload_preview,
            "compiled_workflow_preview": compiled_workflow_preview,
        }

    def render_storyboard_with_plan(
        self,
        project_id: str | None,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        prepared = self.prepare_storyboard_render_request(project_id=project_id, payload=payload)
        dry_run = bool(payload.get("dry_run") is True or payload.get("render") is False)

        if dry_run:
            prepared["dry_run"] = True
            prepared["status"] = "planned"
            return prepared

        return {
            "status": "blocked",
            "dry_run": False,
            "reason": REAL_RENDER_BLOCKED_REASON,
            "project_id": project_id,
            "pipeline": prepared["pipeline"],
            "comfyui_payload_preview": prepared["comfyui_payload_preview"],
        }

    async def render_batch(
        self,
        project_id: str,
        storyboard_prompts: list[dict[str, Any]],
        selected_scenes: list[int] | None = None,
    ) -> dict[str, Any]:
        selected = validate_selected_scenes(selected_scenes or [item.get("scene_number") for item in storyboard_prompts if item.get("scene_number")])
        return {
            "status": "blocked",
            "project_id": project_id,
            "total_scenes": len(selected),
            "rendered_scenes": 0,
            "results": [],
            "reason": REAL_RENDER_BLOCKED_REASON,
        }


comfyui_storyboard_render_service = ComfyUIStoryboardRenderService()


def validate_render_plan(plan: dict[str, Any]) -> None:
    comfyui_storyboard_render_service.validate_render_plan(plan)


def build_comfyui_prompt_payload(
    plan: dict[str, Any],
    prompt: str | None = None,
    negative_prompt: str | None = None,
) -> dict[str, Any]:
    return comfyui_storyboard_render_service.build_comfyui_prompt_payload(
        plan=plan,
        prompt=prompt,
        negative_prompt=negative_prompt,
    )


def build_comfyui_workflow_adapter_payload(
    plan: dict[str, Any],
    prompt: str,
    negative_prompt: str | None = None,
) -> dict[str, Any]:
    return comfyui_storyboard_render_service.build_comfyui_workflow_adapter_payload(
        plan=plan,
        prompt=prompt,
        negative_prompt=negative_prompt,
    )


def prepare_storyboard_render_request(
    project_id: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return comfyui_storyboard_render_service.prepare_storyboard_render_request(
        project_id=project_id,
        payload=payload,
    )


def render_storyboard_with_plan(
    project_id: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return comfyui_storyboard_render_service.render_storyboard_with_plan(
        project_id=project_id,
        payload=payload,
    )
