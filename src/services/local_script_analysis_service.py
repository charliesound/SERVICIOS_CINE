"""
Local script analysis using Qwen3:30b via Ollama.
Generates comprehensive cinematographic script analysis for storyboard preparation.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from services.ollama_client_service import ollama_client
from config import get_llm_settings

logger = logging.getLogger(__name__)


MASTER_ANALYSIS_PROMPT = """Eres un analista profesional de guion cinematografico, script doctor, director de fotografia y supervisor de storyboard.

Analiza el siguiente guion para produccion audiovisual.

Devuelve SOLO JSON valido. No uses markdown. No anadas explicacion externa.

El analisis debe incluir:
- resumen general
- genero
- tono
- tema
- premisa
- conflicto principal
- arco emocional
- personajes
- localizaciones
- secuencias
- escenas
- funcion dramatica de cada escena
- intencion visual
- lenguaje de camara
- notas de sonido
- oportunidades de storyboard
- prompts base para ComfyUI

Cada escena debe incluir un prompt inicial de storyboard que luego sera refinado por otro modelo visual.

Estructura JSON obligatoria:
{
  "project_id": "",
  "model": "",
  "analysis_type": "local_ollama_script_analysis",
  "summary": "",
  "genre": "",
  "tone": "",
  "theme": "",
  "premise": "",
  "main_conflict": "",
  "emotional_arc": "",
  "visual_style": "",
  "characters": [
    {
      "name": "",
      "role": "",
      "description": "",
      "visual_identity": "",
      "emotional_arc": ""
    }
  ],
  "locations": [
    {
      "name": "",
      "description": "",
      "visual_potential": ""
    }
  ],
  "sequences": [
    {
      "sequence_id": "SEQ_001",
      "title": "",
      "summary": "",
      "dramatic_purpose": "",
      "scene_numbers": []
    }
  ],
  "scenes": [
    {
      "scene_number": 1,
      "sequence_id": "SEQ_001",
      "title": "",
      "summary": "",
      "dramatic_function": "",
      "characters": [],
      "location": "",
      "time_of_day": "",
      "mood": "",
      "camera_style": "",
      "sound_notes": "",
      "visual_objective": "",
      "base_storyboard_prompt": "",
      "negative_prompt": "low quality, blurry, distorted faces, bad hands, extra fingers, deformed anatomy, text, subtitles, watermark, logo, oversaturated, plastic skin, inconsistent character design",
      "comfyui_parameters": {
        "aspect_ratio": "16:9",
        "shot_type": "",
        "lens": "",
        "lighting": "",
        "color_palette": "",
        "cinematic_reference": ""
      }
    }
  ]
}

Guion:
"""


class LocalScriptAnalysisService:
    """Service for analyzing scripts using local Ollama Qwen3:30b."""

    async def analyze_script_with_qwen(
        self,
        project_id: str,
        script_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze script using Qwen3:30b via Ollama."""
        settings = get_llm_settings()
        model = settings.get("analysis_model", "qwen3:30b")
        
        if not await ollama_client.is_model_available(model):
            raise RuntimeError(f"Model {model} not available. Run: ollama pull {model}")
        
        prompt = MASTER_ANALYSIS_PROMPT + script_text + "\n\"\"\""
        
        try:
            response_text = await ollama_client.generate_json(
                model=model,
                prompt=prompt,
                temperature=settings.get("temperature_analysis", 0.25),
                num_ctx=settings.get("num_ctx", 32768),
                timeout=settings.get("timeout_seconds", 240),
            )
            
            # Clean and parse JSON
            cleaned = self._clean_json_response(response_text)
            result = json.loads(cleaned)
            
            # Ensure required structure
            result["project_id"] = project_id
            result["model"] = model
            result["analysis_type"] = "local_ollama_script_analysis"
            
            logger.info(f"Script analysis completed for project {project_id} using {model}")
            return result
            
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON from {model}: {exc}")
            raise ValueError(f"Model {model} returned invalid JSON") from exc
        except Exception as exc:
            logger.error(f"Script analysis failed: {exc}")
            raise

    def _clean_json_response(self, text: str) -> str:
        """Clean Ollama response, remove markdown, extract first valid JSON."""
        import re
        # Remove ```json ... ``` blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Try to find first { ... } block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text.strip()


local_script_analysis_service = LocalScriptAnalysisService()
