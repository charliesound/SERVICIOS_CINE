"""
Local script analysis using Qwen3:30b via Ollama.
Generates comprehensive cinematographic script analysis for storyboard preparation.
"""
import json
import logging
from typing import Any

from services.cinematic_interpretation_context_service import (
    cinematic_interpretation_context_service,
)
from services.ollama_client_service import OllamaClientService, ollama_client
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

INSTRUCCIONES ADICIONALES DE INTERPRETACION CINEMATOGRAFICA:
{cinematic_context}

Cada escena debe incluir un prompt inicial de storyboard que luego sera refinado por otro modelo visual.

Estructura JSON obligatoria:
{{
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
    {{
      "name": "",
      "role": "",
      "description": "",
      "visual_identity": "",
      "emotional_arc": ""
    }}
  ],
  "locations": [
    {{
      "name": "",
      "description": "",
      "visual_potential": ""
    }}
  ],
  "sequences": [
    {{
      "sequence_id": "SEQ_001",
      "title": "",
      "summary": "",
      "dramatic_purpose": "",
      "scene_numbers": []
    }}
  ],
  "scenes": [
    {{
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
      "comfyui_parameters": {{
        "aspect_ratio": "16:9",
        "shot_type": "",
        "lens": "",
        "lighting": "",
        "color_palette": "",
        "cinematic_reference": ""
      }},
      "visual_beats": [],
      "sound_beats": [],
      "dialogue_beats": [],
      "reaction_beats": [],
      "threat_beats": [],
      "object_beats": [],
      "suggested_coverage": [],
      "cinematic_coverage_score": null,
      "missing_coverage_warnings": []
    }}
  ]
}}

Guion:
"""


class LocalScriptAnalysisService:

    async def analyze_script_with_qwen(
        self,
        project_id: str,
        script_text: str,
    ) -> dict[str, Any]:
        settings = get_llm_settings()
        model = OllamaClientService.get_model_for_task("script_analysis", settings)

        if not await ollama_client.is_model_available(model):
            raise RuntimeError(f"Model {model} not available. Run: ollama pull {model}")

        cinematic_context = cinematic_interpretation_context_service.load_context()
        context_snippet = cinematic_context["context"][:4000]

        prompt = MASTER_ANALYSIS_PROMPT.format(cinematic_context=context_snippet) + script_text + "\n\"\"\""

        used_fallback = False
        try:
            response_text = await ollama_client.generate_json(
                model=model,
                prompt=prompt,
                temperature=settings.get("temperature_analysis", 0.25),
                num_ctx=settings.get("num_ctx", 32768),
                timeout=settings.get("timeout_seconds", 240),
            )

            cleaned = self._clean_json_response(response_text)
            result = json.loads(cleaned)

            result["project_id"] = project_id
            result["model"] = model
            result["analysis_type"] = "local_ollama_script_analysis"

            logger.info(f"Script analysis completed for project {project_id} using {model}")
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON from {model}: {exc}")
            used_fallback = True
            result = self._fallback_analysis(project_id, script_text, model)
        except Exception as exc:
            logger.error(f"Script analysis failed: {exc}")
            used_fallback = True
            result = self._fallback_analysis(project_id, script_text, model)

        result.setdefault("analysis_provider", "ollama" if not used_fallback else "fallback")
        result.setdefault("interpretation_provider", "local_cinematic_context")
        result.setdefault("rag_context_used", False)
        result.setdefault("cinematic_context_used", True)
        result.setdefault("cinematic_context_sources", cinematic_context["sources"])
        result.setdefault("fallback_applied", used_fallback)
        result.setdefault("ollama_model_used", model)
        result.setdefault("source", "cinematic_script_analysis" if not used_fallback else "fallback_script_breakdown")
        if used_fallback:
            result.setdefault("missing_coverage_warnings", ["Ollama analysis failed; using fallback breakdown"])

        return result

    def _fallback_analysis(
        self,
        project_id: str,
        script_text: str,
        model: str,
    ) -> dict[str, Any]:
        from services.script_synopsis_service import script_synopsis_service
        analysis = script_synopsis_service.analyze_script(script_text)
        raw = analysis.synopsis.raw_analysis if analysis.synopsis else {}
        scenes_raw = []
        for entry in analysis.sequence_map.sequences:
            scene_dict = {
                "scene_number": entry.scene_numbers[0] if entry.scene_numbers else 0,
                "sequence_id": entry.sequence_id,
                "title": entry.title,
                "dramatic_function": entry.dramatic_function or "",
                "characters": entry.characters,
                "location": entry.location or "",
                "time_of_day": entry.time_of_day or "",
                "visual_beats": [],
                "sound_beats": [],
                "dialogue_beats": [],
                "reaction_beats": [],
                "threat_beats": [],
                "object_beats": [],
                "suggested_coverage": [],
                "cinematic_coverage_score": None,
                "missing_coverage_warnings": [],
            }
            scenes_raw.append(scene_dict)
        return {
            "project_id": project_id,
            "model": model,
            "analysis_type": "fallback_script_analysis",
            "summary": raw.get("summary", ""),
            "synopsis": analysis.synopsis.model_dump() if analysis.synopsis else {},
            "scenes": scenes_raw,
            "sequences": [s.model_dump() for s in analysis.sequence_map.sequences],
        }

    def _clean_json_response(self, text: str) -> str:
        import re
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text.strip()


local_script_analysis_service = LocalScriptAnalysisService()
