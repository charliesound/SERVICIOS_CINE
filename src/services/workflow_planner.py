from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .workflow_registry import workflow_registry, TaskCategory


@dataclass
class IntentAnalysis:
    task_type: str
    intent: str
    detected_workflow: Optional[str]
    backend: str
    confidence: float
    reasoning: str
    missing_inputs: List[str]
    suggested_params: Dict[str, Any]


class WorkflowPlanner:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def analyze_intent(self, intent: str, context: Dict[str, Any]) -> IntentAnalysis:
        intent_lower = intent.lower()
        
        task_type = self._detect_task_type(intent_lower, context)
        backend = self._map_task_to_backend(task_type)
        workflow_key = self._select_workflow(intent_lower, context, task_type, backend)
        missing_inputs = self._find_missing_inputs(workflow_key, context)
        suggested_params = self._extract_suggested_params(intent_lower, context)

        confidence = self._calculate_confidence(workflow_key, missing_inputs)

        reasoning = self._build_reasoning(task_type, workflow_key, context)

        return IntentAnalysis(
            task_type=task_type,
            intent=intent,
            detected_workflow=workflow_key,
            backend=backend,
            confidence=confidence,
            reasoning=reasoning,
            missing_inputs=missing_inputs,
            suggested_params=suggested_params
        )

    def _detect_task_type(self, intent: str, context: Dict[str, Any]) -> str:
        source_image = context.get("source_image")
        mask = context.get("mask")
        
        if intent.startswith("generate") or intent.startswith("create image"):
            if mask:
                return "inpaint"
            return "still"
        
        if any(word in intent for word in ["storyboard", "plano", "frame", "shot"]):
            return "still"
        
        if any(word in intent for word in ["character", "consistencia", "personaje"]) and source_image:
            return "still"
        
        if intent.startswith("video") or "video" in intent:
            return "video"
        
        if any(word in intent for word in ["dubbing", "voz", "tts", "audio", "traducir"]):
            return "dubbing"
        
        if any(word in intent for word in ["test", "probe", "experimental", "lab"]):
            return "experimental"
        
        return context.get("task_type", "still")

    def _map_task_to_backend(self, task_type: str) -> str:
        mapping = {
            "still": "still",
            "image": "still",
            "img2img": "still",
            "inpaint": "still",
            "upscale": "still",
            "video": "video",
            "text_to_video": "video",
            "image_to_video": "video",
            "dubbing": "dubbing",
            "tts": "dubbing",
            "voice_clone": "dubbing",
            "experimental": "lab",
            "test": "lab"
        }
        return mapping.get(task_type, "still")

    def _select_workflow(self, intent: str, context: Dict[str, Any], task_type: str, backend: str) -> Optional[str]:
        source_image = context.get("source_image")
        mask = context.get("mask")
        reference_audio = context.get("reference_audio")

        if task_type == "still":
            if any(word in intent for word in ["storyboard", "plano", "frame"]):
                return "still_storyboard_frame"
            if context.get("reference_image") and any(word in intent for word in ["character", "consistencia"]):
                return "still_character_consistency"
            if mask:
                return "still_inpaint_production"
            if source_image and not mask:
                return "still_img2img_cinematic"
            if any(word in intent for word in ["upscale", "mejorar", "enhance"]):
                return "still_upscale_master"
            return "still_text_to_image_pro"

        if task_type == "video":
            if context.get("first_frame") and context.get("last_frame"):
                return "video_first_last_frame"
            if source_image:
                return "video_image_to_video_base"
            return "video_text_to_video_base"

        if task_type == "dubbing":
            if reference_audio and context.get("text"):
                return "dubbing_voice_clone_single"
            if context.get("script") and any(word in intent for word in ["dialog", "dialogo", "multi"]):
                return "dubbing_multi_character_dialog"
            if context.get("source_audio") and any(word in intent for word in ["translate", "traducir"]):
                return "dubbing_translate_stt_tts"
            if context.get("text"):
                return "dubbing_tts_es_es"
            return "dubbing_tts_es_es"

        if task_type == "experimental":
            if any(word in intent for word in ["probe", "test"]):
                return "lab_probe_nodes"
            return "lab_auto_assemble_test"

        workflows = workflow_registry.get_workflows_by_backend(backend)
        return workflows[0].key if workflows else None

    def _find_missing_inputs(self, workflow_key: str, context: Dict[str, Any]) -> List[str]:
        if not workflow_key:
            return []
        
        workflow = workflow_registry.get_workflow(workflow_key)
        if not workflow:
            return []
        
        missing = []
        for required in workflow.required_inputs:
            if required not in context or context[required] is None:
                missing.append(required)
        
        return missing

    def _extract_suggested_params(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        params = {}
        
        if "cinematic" in intent or "cinematográfico" in intent:
            params["aspect_ratio"] = "16:9"
            params["lighting"] = "dramatic"
        
        if "portrait" in intent or "retrato" in intent:
            params["aspect_ratio"] = "3:4"
        
        if "fast" in intent or "rápido" in intent:
            params["steps"] = 20
        
        if "high quality" in intent or "alta calidad" in intent:
            params["steps"] = 50
            params["cfg"] = 7.5
        
        if context.get("duration"):
            params["duration"] = context["duration"]
        
        if context.get("seed"):
            params["seed"] = context["seed"]
        
        return params

    def _calculate_confidence(self, workflow_key: Optional[str], missing_inputs: List[str]) -> float:
        if not workflow_key:
            return 0.0
        
        base = 0.7
        
        if not missing_inputs:
            base += 0.2
        else:
            base -= len(missing_inputs) * 0.1
        
        return min(1.0, max(0.0, base))

    def _build_reasoning(self, task_type: str, workflow_key: Optional[str], context: Dict[str, Any]) -> str:
        parts = []
        
        parts.append(f"Tarea clasificada como: {task_type}")
        
        if workflow_key:
            workflow = workflow_registry.get_workflow(workflow_key)
            if workflow:
                parts.append(f"Workflow seleccionado: {workflow.name}")
        
        if context.get("source_image"):
            parts.append("Se detectó imagen source - img2img")
        if context.get("mask"):
            parts.append("Se detectó máscara - inpaint")
        if context.get("reference_audio"):
            parts.append("Se detectó audio de referencia - voice clone")
        
        return ". ".join(parts)


planner = WorkflowPlanner()
