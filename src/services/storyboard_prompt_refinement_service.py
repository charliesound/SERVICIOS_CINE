"""
Storyboard prompt refinement using Gemma4:26b/31b (preferred) or Qwen3:30b (fallback).
Refines base storyboard prompts into detailed visual cinematographic prompts for ComfyUI.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from services.ollama_client_service import ollama_client
from config import get_llm_settings

logger = logging.getLogger(__name__)


VISUAL_REFINEMENT_PROMPT = """Eres director de fotografia, concept artist y prompt engineer experto en ComfyUI, cine hiperrealista y storyboard profesional.

Refina los prompts de storyboard provenientes de un analisis de guion.

Objetivo:
- convertir cada escena en un prompt visual cinematografico
- mantener continuidad de personajes
- mantener continuidad estetica
- describir plano, lente, iluminacion, atmosfera, color, composicion y textura
- evitar estilo generico
- preparar prompts compatibles con SDXL, Flux, Wan, Hunyuan o modelos de imagen/video usados en ComfyUI
- devolver SOLO JSON valido.

Formato por escena:
{
  "scene_number": 1,
  "sequence_id": "SEQ_001",
  "refined_storyboard_prompt": "",
  "comfyui_positive_prompt": "",
  "comfyui_negative_prompt": "",
  "shot_design": {
    "shot_type": "",
    "camera_angle": "",
    "lens": "",
    "camera_movement": "",
    "composition": "",
    "lighting": "",
    "color_palette": "",
    "texture": "",
    "cinematic_reference": ""
  },
  "continuity": {
    "character_continuity_prompt": "",
    "environment_continuity_prompt": "",
    "wardrobe_continuity_prompt": "",
    "seed_strategy": ""
  }
}

Analisis original:
"""


class StoryboardPromptRefinementService:
    """Service for refining storyboard prompts using visual models."""

    async def refine_storyboard_prompts(
        self,
        analysis_payload: Dict[str, Any],
        mode: str = "all",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Refine storyboard prompts using Gemma4 (preferred) or Qwen3 fallback."""
        settings = get_llm_settings()
        
        # Determine visual model
        visual_model = settings.get("visual_model", "gemma4:26b")
        fallback_model = settings.get("fallback_model", "qwen3:30b")
        
        if not await ollama_client.is_model_available(visual_model):
            logger.warning(f"Visual model {visual_model} not available, falling back to {fallback_model}")
            visual_model = fallback_model
        
        scenes = analysis_payload.get("scenes", [])
        
        # Apply filters
        if filters:
            if "scene_numbers" in filters:
                scenes = [s for s in scenes if s.get("scene_number") in filters["scene_numbers"]]
            if "sequence_id" in filters:
                scenes = [s for s in scenes if s.get("sequence_id") == filters["sequence_id"]]
        
        refined_scenes = []
        for scene in scenes:
            prompt = VISUAL_REFINEMENT_PROMPT + json.dumps(scene, ensure_ascii=False) + "\n\"\"\""
            
            try:
                response_text = await ollama_client.generate_json(
                    model=visual_model,
                    prompt=prompt,
                    temperature=settings.get("temperature_visual", 0.55),
                    num_ctx=settings.get("num_ctx", 32768),
                    timeout=settings.get("timeout_seconds", 240),
                )
                
                cleaned = self._clean_json_response(response_text)
                refined = json.loads(cleaned)
                refined["scene_number"] = scene["scene_number"]
                refined["sequence_id"] = scene.get("sequence_id", "")
                refined_scenes.append(refined)
                
            except Exception as exc:
                logger.error(f"Failed to refine scene {scene.get('scene_number')}: {exc}")
                # Keep original if refinement fails
                refined_scenes.append({
                    "scene_number": scene["scene_number"],
                    "sequence_id": scene.get("sequence_id", ""),
                    "refined_storyboard_prompt": scene.get("base_storyboard_prompt", ""),
                    "comfyui_positive_prompt": scene.get("base_storyboard_prompt", ""),
                    "comfyui_negative_prompt": scene.get("negative_prompt", ""),
                    "shot_design": scene.get("comfyui_parameters", {}),
                    "continuity": {"character_continuity_prompt": "", "environment_continuity_prompt": "", "seed_strategy": ""}
                })
        
        return {
            "project_id": analysis_payload.get("project_id", ""),
            "analysis_model": analysis_payload.get("model", "qwen3:30b"),
            "visual_model": visual_model,
            "generation_mode": mode,
            "total_scenes": len(refined_scenes),
            "selected_scenes": [s["scene_number"] for s in refined_scenes],
            "storyboard_prompts": refined_scenes,
        }

    def _clean_json_response(self, text: str) -> str:
        """Clean and extract JSON from Ollama response."""
        import re
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text.strip()


storyboard_prompt_refinement_service = StoryboardPromptRefinementService()
