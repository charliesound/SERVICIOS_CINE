from typing import Dict, List, Optional, Any
from copy import deepcopy
import hashlib
import random
import logging

from .workflow_registry import workflow_registry, WorkflowTemplate, TaskCategory
from schemas.comfyui_workflow_schema import WorkflowFallbackReport
from services.comfyui_workflow_selector_service import select_workflow as _selector_select_workflow
from services.storyboard_style_preset_service import storyboard_style_preset_service


logger = logging.getLogger(__name__)


STORYBOARD_RUNTIME_PRESETS = {
    "storyboard_sketch": {
        "checkpoint": "AAM_XL_Anime_Mix.safetensors",
        "settings": {
            "width": 1024,
            "height": 576,
            "steps": 24,
            "cfg": 6.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
        },
    },
    "storyboard_realistic": {
        "checkpoint": "Realistic_Vision_V2.0.safetensors",
        "settings": {
            "width": 1024,
            "height": 576,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
        },
    },
    "production_storyboard_cinematic": {
        "checkpoint": "FLUX/flux1-schnell-fp8.safetensors",
        "settings": {
            "width": 1344,
            "height": 768,
            "steps": 8,
            "cfg": 2.5,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
        },
    }
}
DEFAULT_STORYBOARD_NEGATIVE = (
    "blurry, low quality, bad anatomy, deformed hands, extra fingers, duplicate, "
    "cropped, watermark, text, logo, oversaturated, cartoon, anime, plastic skin"
)
PRODUCTION_STORYBOARD_NEGATIVE = (
    "low quality, blurry, noisy image, bad anatomy, deformed hands, extra fingers, duplicate limbs, "
    "inconsistent character face, broken perspective, muddy composition, unreadable action, flat lighting, "
    "oversaturated color, cheap CGI look, random props, text, subtitle, logo, watermark, interface overlay"
)


class WorkflowBuilder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def build_workflow(self, workflow_key: str, inputs: Dict[str, Any], 
                       overrides: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        template = workflow_registry.get_workflow(workflow_key)
        if not template:
            return None

        workflow = {
            "nodes": [],
            "links": [],
            "version": "1.0",
            "workflow_key": workflow_key,
            "category": template.category.value,
            "backend": template.backend
        }

        nodes_map = {}

        for node in template.nodes:
            node_dict = self._build_node(node, inputs, nodes_map)
            if node_dict:
                workflow["nodes"].append(node_dict)
                nodes_map[node.node_id] = node_dict

        self._finalize_links(workflow, nodes_map)

        if overrides:
            self._apply_overrides(workflow, overrides)

        return workflow

    def _build_node(self, node, inputs: Dict[str, Any], nodes_map: Dict) -> Optional[Dict[str, Any]]:
        node_dict = {
            "id": node.node_id,
            "type": node.class_type,
            "pos": [0, 0],
            "size": [320, 240],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": {},
            "outputs": {},
            "properties": {},
            "widgets_values": []
        }

        for input_name in node.required_inputs:
            value = inputs.get(input_name)
            if value is not None:
                node_dict["inputs"][input_name] = self._resolve_input(value, input_name, nodes_map)
            elif input_name in ["prompt", "text"]:
                node_dict["inputs"][input_name] = inputs.get("prompt", "") or inputs.get("text", "")

        for input_name in node.optional_inputs:
            value = inputs.get(input_name)
            if value is not None:
                node_dict["inputs"][input_name] = self._resolve_input(value, input_name, nodes_map)

        return node_dict

    def _resolve_input(self, value: Any, input_name: str, nodes_map: Dict) -> Any:
        if input_name == "clip" and isinstance(value, list):
            node_id, output_idx = value
            if node_id in nodes_map:
                return {"name": "clip", "slot_index": output_idx, "link": None}
        
        if input_name == "model" and isinstance(value, list):
            node_id, output_idx = value
            if node_id in nodes_map:
                return {"name": "model", "slot_index": output_idx, "link": None}
        
        if input_name == "vae" and isinstance(value, list):
            node_id, output_idx = value
            if node_id in nodes_map:
                return {"name": "vae", "slot_index": output_idx, "link": None}
        
        return value

    def _finalize_links(self, workflow: Dict, nodes_map: Dict):
        links = []
        link_id = 1

        for node in workflow["nodes"]:
            for input_name, input_val in node.get("inputs", {}).items():
                if isinstance(input_val, dict) and "link" in input_val:
                    for target_node in workflow["nodes"]:
                        if target_node["id"] == node["id"]:
                            continue
                        for out_name in ["model", "clip", "vae", "samples", "images", "audio", "text"]:
                            if out_name in target_node.get("outputs", {}):
                                pass

        workflow["links"] = links

    def _apply_overrides(self, workflow: Dict, overrides: Dict[str, Any]):
        for node in workflow["nodes"]:
            for key, value in overrides.items():
                if key in node.get("inputs", {}):
                    node["inputs"][key] = value
                if key in node.get("widgets_values", []):
                    idx = node["widgets_values"].index(key)
                    if idx + 1 < len(node["widgets_values"]):
                        node["widgets_values"][idx + 1] = value

    def build_from_intent(self, intent: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from .workflow_planner import planner
        
        analysis = planner.analyze_intent(intent, context)
        
        if not analysis.detected_workflow:
            return None
        
        if analysis.missing_inputs:
            return {
                "error": "missing_inputs",
                "missing": analysis.missing_inputs,
                "analysis": {
                    "task_type": analysis.task_type,
                    "backend": analysis.backend,
                    "confidence": analysis.confidence,
                    "reasoning": analysis.reasoning
                }
            }
        
        merged_inputs = {**context, **analysis.suggested_params}
        
        return self.build_workflow(analysis.detected_workflow, merged_inputs)

    def clone_workflow(self, workflow_key: str, new_name: str) -> Optional[Dict[str, Any]]:
        template = workflow_registry.get_workflow(workflow_key)
        if not template:
            return None
        
        return {
            "nodes": deepcopy(template.nodes),
            "version": "1.0",
            "workflow_key": f"{workflow_key}_custom",
            "name": new_name,
            "category": template.category.value,
            "backend": template.backend,
            "custom": True
        }

    def get_workflow_preview(self, workflow_key: str) -> Optional[Dict[str, Any]]:
        template = workflow_registry.get_workflow(workflow_key)
        if not template:
            return None
        
        return {
            "key": template.key,
            "name": template.name,
            "description": template.description,
            "required_inputs": template.required_inputs,
            "optional_inputs": template.optional_inputs,
            "nodes_count": len(template.nodes),
            "node_types": [n.class_type for n in template.nodes],
            "tags": template.tags
        }

    def build_runtime_prompt(self, workflow_key: str, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self._looks_like_comfyui_prompt(inputs):
            return inputs

        requested_profile = inputs.get("workflow_profile_requested") or inputs.get("workflow_profile")
        if isinstance(requested_profile, str) and requested_profile.strip():
            prompt, _exec_key, _fallback_report, _exec_profile = self.build_runtime_prompt_with_profile(
                workflow_key,
                inputs,
                requested_profile=requested_profile,
                available_nodes=None,
                skip_node_validation=True,
            )
            if prompt:
                return prompt

        if workflow_key == "still_storyboard_frame":
            return self._build_still_storyboard_prompt(inputs)
        if workflow_key == "still_text_to_image_pro":
            return self._build_basic_text_to_image_prompt(
                inputs,
                checkpoint=str(inputs.get("checkpoint") or "Realistic_Vision_V2.0.safetensors"),
                filename_prefix=str(inputs.get("filename_prefix") or "text_to_image"),
            )
        return None

    def _looks_like_comfyui_prompt(self, payload: Dict[str, Any]) -> bool:
        if not isinstance(payload, dict) or not payload:
            return False
        return all(
            isinstance(node, dict) and "class_type" in node and "inputs" in node
            for node in payload.values()
        )

    def _build_still_storyboard_prompt(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        storyboard_inputs = dict(inputs)
        storyboard_inputs.setdefault("seed", self._resolve_storyboard_seed(storyboard_inputs))
        preset_key = str(storyboard_inputs.get("preset_key") or "storyboard_realistic")
        preset = STORYBOARD_RUNTIME_PRESETS.get(preset_key)
        if preset is None:
            logger.warning(
                "Unknown storyboard preset_key '%s', falling back to storyboard_sketch",
                preset_key,
            )
            preset_key = "storyboard_sketch"
            preset = STORYBOARD_RUNTIME_PRESETS["storyboard_sketch"]
        settings = preset.get("settings", {})
        style_preset = str(storyboard_inputs.get("style_preset") or "").strip().lower()
        if style_preset:
            base_prompt = str(storyboard_inputs.get("prompt") or storyboard_inputs.get("text") or "").strip()
            storyboard_inputs["prompt"] = storyboard_style_preset_service.enrich_prompt_with_storyboard_style(
                base_prompt,
                style_preset,
            )
            style_negative = storyboard_style_preset_service.get_negative_prompt_for_storyboard_style(style_preset)
            if style_negative:
                base_negative = str(storyboard_inputs.get("negative_prompt") or DEFAULT_STORYBOARD_NEGATIVE).strip()
                storyboard_inputs["negative_prompt"] = ", ".join(
                    part for part in [base_negative, style_negative] if part
                )
        return self._build_basic_text_to_image_prompt(
            storyboard_inputs,
            checkpoint=str(storyboard_inputs.get("checkpoint") or preset.get("checkpoint") or "Realistic_Vision_V2.0.safetensors"),
            filename_prefix=str(storyboard_inputs.get("filename_prefix") or "storyboard"),
            width=int(storyboard_inputs.get("width") or settings.get("width") or 1024),
            height=int(storyboard_inputs.get("height") or settings.get("height") or 576),
            steps=int(storyboard_inputs.get("steps") or settings.get("steps") or 20),
            cfg=float(storyboard_inputs.get("cfg") or settings.get("cfg") or 7.0),
            sampler_name=str(storyboard_inputs.get("sampler_name") or settings.get("sampler_name") or "euler"),
            scheduler=str(storyboard_inputs.get("scheduler") or settings.get("scheduler") or "normal"),
            denoise=float(storyboard_inputs.get("denoise") or settings.get("denoise") or 1.0),
            negative_prompt=str(storyboard_inputs.get("negative_prompt") or DEFAULT_STORYBOARD_NEGATIVE),
        )

    def _stable_hash_to_seed(self, value: str) -> int:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        seed = int(digest[:8], 16)
        return max(1, seed)

    def _resolve_storyboard_seed(self, inputs: Dict[str, Any]) -> int:
        explicit_seed = inputs.get("seed")
        try:
            if explicit_seed is not None:
                return max(1, int(explicit_seed))
        except (TypeError, ValueError):
            pass

        continuity_seed = str(inputs.get("continuity_seed") or "").strip()
        if continuity_seed:
            return self._stable_hash_to_seed(continuity_seed)

        parts = [
            str(inputs.get("scene_heading") or ""),
            str(inputs.get("source_scene_heading") or ""),
            str(inputs.get("source_action_summary") or ""),
            str(inputs.get("shot_objective") or ""),
            str(inputs.get("location") or ""),
            str(inputs.get("time_of_day") or ""),
            str(inputs.get("style_preset") or ""),
            str(inputs.get("workflow_profile_requested") or inputs.get("workflow_profile") or "storyboard_safe"),
        ]
        source = "|".join(parts)
        return self._stable_hash_to_seed(source or str(random.randint(1, 2**31 - 1)))

    def _build_production_storyboard_prompt_text(self, inputs: Dict[str, Any]) -> str:
        base_prompt = str(inputs.get("prompt") or inputs.get("text") or "").strip()
        scene_heading = str(inputs.get("source_scene_heading") or inputs.get("scene_heading") or "").strip()
        action = str(inputs.get("source_action_summary") or "").strip()
        objective = str(inputs.get("shot_objective") or "").strip()
        atmosphere = str(inputs.get("atmosphere") or "").strip()
        location = str(inputs.get("location") or "").strip()
        time_of_day = str(inputs.get("time_of_day") or "").strip()
        continuity_seed = str(inputs.get("continuity_seed") or "").strip()

        parts = [
            "cinematic storyboard frame for premium client review",
            base_prompt,
            f"scene heading: {scene_heading}" if scene_heading else "",
            f"action: {action}" if action else "",
            f"objective: {objective}" if objective else "",
            f"atmosphere: {atmosphere}" if atmosphere else "",
            f"location: {location}" if location else "",
            f"time of day: {time_of_day}" if time_of_day else "",
            "consistent character identity, clear blocking, production-ready composition, readable silhouette, grounded lighting",
            f"continuity anchor: {continuity_seed}" if continuity_seed else "",
        ]
        return ", ".join(part for part in parts if part)

    def _build_production_storyboard_negative_prompt(self, inputs: Dict[str, Any]) -> str:
        base_negative = str(inputs.get("negative_prompt") or "").strip()
        return ", ".join(part for part in [base_negative, PRODUCTION_STORYBOARD_NEGATIVE] if part)

    def _prepare_storyboard_profile_inputs(self, inputs: Dict[str, Any], requested_profile: str) -> Dict[str, Any]:
        prepared = dict(inputs)
        prepared.setdefault("workflow_profile_requested", requested_profile)
        prepared["seed"] = self._resolve_storyboard_seed(prepared)
        if requested_profile in {"production_storyboard_cinematic", "production_quality"}:
            prepared["checkpoint"] = STORYBOARD_RUNTIME_PRESETS["production_storyboard_cinematic"]["checkpoint"]
            prepared["width"] = STORYBOARD_RUNTIME_PRESETS["production_storyboard_cinematic"]["settings"]["width"]
            prepared["height"] = STORYBOARD_RUNTIME_PRESETS["production_storyboard_cinematic"]["settings"]["height"]
            prepared["steps"] = STORYBOARD_RUNTIME_PRESETS["production_storyboard_cinematic"]["settings"]["steps"]
            prepared["cfg"] = STORYBOARD_RUNTIME_PRESETS["production_storyboard_cinematic"]["settings"]["cfg"]
            prepared["sampler_name"] = STORYBOARD_RUNTIME_PRESETS["production_storyboard_cinematic"]["settings"]["sampler_name"]
            prepared["scheduler"] = STORYBOARD_RUNTIME_PRESETS["production_storyboard_cinematic"]["settings"]["scheduler"]
            prepared["model_family"] = "flux"
            prepared["prompt"] = self._build_production_storyboard_prompt_text(prepared)
            prepared["negative_prompt"] = self._build_production_storyboard_negative_prompt(prepared)
        if requested_profile == "production_storyboard_cinematic_controlnet":
            strength_value = inputs.get("controlnet_strength")
            try:
                controlnet_strength = float(strength_value) if strength_value is not None else 1.0
            except (TypeError, ValueError):
                controlnet_strength = 1.0
            prepared["checkpoint"] = "FLUX/flux1-dev-fp8.safetensors"
            prepared["width"] = 1344
            prepared["height"] = 768
            prepared["steps"] = 20
            prepared["cfg"] = 3.5
            prepared["sampler_name"] = "euler"
            prepared["scheduler"] = "normal"
            prepared["controlnet_strength"] = controlnet_strength
            prepared["controlnet_preprocessor"] = str(inputs.get("controlnet_preprocessor") or "DWPreprocessor")
            prepared["controlnet_model"] = str(inputs.get("controlnet_model") or "flux_dev_openpose_controlnetl.safetensors")
            prepared["reference_mode"] = "controlnet"
        return prepared

    def _has_usable_controlnet_reference(self, inputs: Dict[str, Any]) -> bool:
        pose_reference_image = inputs.get("pose_reference_image")
        if isinstance(pose_reference_image, str) and pose_reference_image.strip():
            return True
        hints = inputs.get("controlnet_hints")
        if isinstance(hints, dict):
            return any(value not in (None, "", [], {}) for value in hints.values())
        if isinstance(hints, list):
            return len(hints) > 0
        return False

    def extract_runtime_prompt_metadata(self, runtime_prompt: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(runtime_prompt, dict):
            return {}

        def _first_node_inputs(class_type: str) -> Dict[str, Any]:
            for node in runtime_prompt.values():
                if isinstance(node, dict) and node.get("class_type") == class_type:
                    inputs_payload = node.get("inputs")
                    if isinstance(inputs_payload, dict):
                        return inputs_payload
            return {}

        checkpoint_inputs = _first_node_inputs("CheckpointLoaderSimple")
        text_nodes = [
            node.get("inputs")
            for node in runtime_prompt.values()
            if isinstance(node, dict) and node.get("class_type") == "CLIPTextEncode" and isinstance(node.get("inputs"), dict)
        ]
        latent_inputs = _first_node_inputs("EmptyLatentImage")
        sampler_inputs = _first_node_inputs("KSampler")

        checkpoint = checkpoint_inputs.get("ckpt_name")
        positive_prompt = text_nodes[0].get("text") if len(text_nodes) > 0 else None
        negative_prompt = text_nodes[1].get("text") if len(text_nodes) > 1 else None
        width = latent_inputs.get("width")
        height = latent_inputs.get("height")
        model_family: Optional[str] = None
        if isinstance(checkpoint, str):
            ckpt_lower = checkpoint.lower()
            if "flux" in ckpt_lower:
                model_family = "flux"
            elif "sdxl" in ckpt_lower or "sd_xl" in ckpt_lower:
                model_family = "sdxl"
            elif "wan" in ckpt_lower:
                model_family = "wan22"
        return {
            "checkpoint": checkpoint,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": sampler_inputs.get("steps"),
            "cfg": sampler_inputs.get("cfg"),
            "sampler_name": sampler_inputs.get("sampler_name"),
            "scheduler": sampler_inputs.get("scheduler"),
            "seed": sampler_inputs.get("seed"),
            "model_family": model_family,
        }

    def _build_basic_text_to_image_prompt(
        self,
        inputs: Dict[str, Any],
        *,
        checkpoint: str,
        filename_prefix: str,
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg: float = 7.0,
        sampler_name: str = "euler",
        scheduler: str = "normal",
        denoise: float = 1.0,
        negative_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        prompt_text = str(inputs.get("prompt") or inputs.get("text") or "").strip()
        negative_text = str(
            negative_prompt
            or inputs.get("negative_prompt")
            or "blurry, low quality, distorted"
        ).strip()
        seed_value = inputs.get("seed")
        try:
            seed = int(seed_value) if seed_value is not None else random.randint(1, 2**31 - 1)
        except (TypeError, ValueError):
            seed = random.randint(1, 2**31 - 1)

        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt_text, "clip": ["1", 1]},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": negative_text, "clip": ["1", 1]},
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler_name,
                    "scheduler": scheduler,
                    "denoise": denoise,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                },
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": filename_prefix, "images": ["6", 0]},
            },
        }


    def build_runtime_prompt_with_profile(
        self,
        workflow_key: str,
        inputs: Dict[str, Any],
        requested_profile: str = "storyboard_safe",
        available_nodes: Optional[set[str]] = None,
        *,
        skip_node_validation: bool = False,
    ) -> tuple[Optional[Dict[str, Any]], str, Optional[WorkflowFallbackReport], str]:
        if self._looks_like_comfyui_prompt(inputs):
            return inputs, workflow_key, None, requested_profile

        if workflow_key == "still_storyboard_frame":
            storyboard_inputs = self._prepare_storyboard_profile_inputs(inputs, requested_profile)
            selector_profiles = {
                "smoke_light",
                "storyboard_safe",
                "storyboard_fast",
                "production_quality",
                "production_storyboard_cinematic",
                "production_storyboard_cinematic_controlnet",
            }
            fallback_report: Optional[WorkflowFallbackReport] = None
            executed_profile = requested_profile
            selector_requested_profile = requested_profile
            if requested_profile == "production_storyboard_cinematic_controlnet" and not self._has_usable_controlnet_reference(storyboard_inputs):
                selector_requested_profile = "production_storyboard_cinematic"
                fallback_report = WorkflowFallbackReport(
                    requested_profile="production_storyboard_cinematic_controlnet",
                    executed_profile="production_storyboard_cinematic",
                    fallback_applied=True,
                    reason="missing_controlnet_reference",
                    missing_nodes=[],
                    missing_models=[],
                )
            if requested_profile in selector_profiles:
                prompt, _exec_key, selector_fallback_report, executed_profile = _selector_select_workflow(
                    workflow_key=workflow_key,
                    requested_profile=selector_requested_profile,
                    inputs=storyboard_inputs,
                    available_nodes=available_nodes,
                    skip_node_validation=skip_node_validation,
                )
                if selector_fallback_report is not None:
                    fallback_report = selector_fallback_report
                if prompt is not None:
                    return prompt, workflow_key, fallback_report, executed_profile
            prompt = self._build_still_storyboard_prompt(storyboard_inputs)
            return prompt, workflow_key, fallback_report, "hardcoded_safety_net"

        prompt, exec_key, fallback_report, exec_profile = _selector_select_workflow(
            workflow_key=workflow_key,
            requested_profile=requested_profile,
            inputs=inputs,
            available_nodes=available_nodes,
            skip_node_validation=skip_node_validation,
        )
        if prompt is not None:
            return prompt, exec_key, fallback_report, exec_profile

        if workflow_key in {"still_text_to_image_pro", "storyboard_safe", "smoke_light"}:
            fallback_prompt = self._build_basic_text_to_image_prompt(
                inputs,
                checkpoint=str(inputs.get("checkpoint") or "Realistic_Vision_V2.0.safetensors"),
                filename_prefix=str(
                    inputs.get("output_prefix")
                    or inputs.get("filename_prefix")
                    or workflow_key
                ),
                width=int(inputs.get("width") or 1024),
                height=int(inputs.get("height") or 1024),
                steps=int(inputs.get("steps") or 20),
                cfg=float(inputs.get("cfg") or 7.0),
                sampler_name=str(inputs.get("sampler_name") or inputs.get("sampler") or "euler"),
                scheduler=str(inputs.get("scheduler") or "normal"),
                denoise=float(inputs.get("denoise") or 1.0),
                negative_prompt=str(inputs.get("negative_prompt") or "blurry, low quality, distorted"),
            )
            return fallback_prompt, workflow_key, fallback_report, "hardcoded_safety_net"

        return None, "", fallback_report, "none"


builder = WorkflowBuilder()
