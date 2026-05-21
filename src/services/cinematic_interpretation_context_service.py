from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CINEMATIC_DIRECTIVES_DIRS = [
    "directivas/prompt_references",
    "directivas/cinematography_prompt_references",
    "directivas",
    "docs",
]

CINEMATIC_KEYWORDS = {
    "guion", "screenplay", "interpretación", "cinematografía",
    "storyboard", "cobertura", "plano", "dirección",
    "sonido", "narrativo", "continuidad", "personaje",
    "tensión", "suspense", "camera", "lens", "lighting",
    "prompt", "beat", "shot",
}

DEFAULT_CINEMATIC_DIRECTIVE = r"""
=== CINEMATIC INTERPRETATION DIRECTIVE ===
Language: bilingual (es/en)

1. CHARACTER ENTRY/EXIT:
   - "entra", "enters", "viene", "llega", "appears" => character_entry beat
   - "sale", "exits", "huye", "escapa", "flee" => character_exit beat
   - Shot: MS for entry, WS or MS for exit

2. IMPORTANT OBJECTS (props with narrative weight):
   - "linterna", "flashlight", "llave", "key", "arma", "weapon"
   - "documento", "document", "nota", "note"
   - => detail_object beat, CU, insert shot

3. NARRATIVE SOUNDS:
   - "cruje", "creak", "crujido", "ruido", "sound"
   - "silencio", "silence" => silence/sound_detail beat
   - "parpadea", "flicker" => sound_detail with visual emphasis
   - "pasos", "footsteps" => sound_detail beat
   - Shot: CU, emphasize diegetic audio

4. DIALOGUE PATTERNS:
   - "dice", "says", "pregunta", "asks", "whispers"
   - "¿...?" or "..." => dialogue beat
   - Shot: OTS or MS, capture reaction

5. EMOTIONAL REACTIONS:
   - "terror", "miedo", "fear", "shock", "sorpresa", "surprise"
   - "quieta", "quieto", "frozen", "paralizado", "paralyzed"
   - => reaction_closeup beat, CU, emotional emphasis

6. THREAT / OFF-SCENE:
   - "sombra", "shadow", "oscuridad", "darkness"
   - "figura", "figure", "silueta", "silhouette"
   - "amenaza", "threat", "tensión", "tension"
   - => shadow_reveal or suspense_build beat, WS or MS

7. SPATIAL CONTINUITY:
   - "contraplano", "reverse", "over shoulder", "desde atrás"
   - => reverse_angle beat, OTS
   - "establecimiento", "establishing", "exterior"
   - => establishing beat, WS

8. MINIMUM COVERAGE PER SEQUENCE (auto_cinematic mode):
   - If dialogue + action + threat => 5 shots
   - If threat + exit/action => 4 shots
   - If action + dialogue => 4 shots
   - Default => 3 shots minimum

9. SUSPENSE SCENE RULES (for scenes like Marta's):
   - floor creaks => sound_detail or object_detail beat
   - "¿Hay alguien ahí?" => dialogue beat + MS/reaction
   - shadow in background => threat/reveal beat
   - contained fear => CU/reaction closeup
   - flashlight flicker => sound_detail + visual emphasis
   - figure at door => figure_reveal or shadow_reveal
   - character fleeing => character_exit + WS
   - reverse angle from door => reverse_angle for drama

10. METADATA REQUIREMENTS:
    - Always include: scene_number, int_ext, location, time_of_day
    - Always compute: cinematic_coverage_score (0-10)
    - Warn when coverage is missing: missing_coverage_warnings
    - List beats found: visual_beats, sound_beats, dialogue_beats,
      reaction_beats, threat_beats, object_beats
    - Suggest coverage: suggested_coverage list with shot reasons
"""


class CinematicInterpretationContextService:

    def load_context(self) -> dict[str, Any]:
        loaded_files: list[str] = []
        combined_text_parts: list[str] = [DEFAULT_CINEMATIC_DIRECTIVE.strip()]

        for dir_rel in CINEMATIC_DIRECTIVES_DIRS:
            dir_path = Path(dir_rel)
            if not dir_path.is_dir():
                continue
            for fpath in sorted(dir_path.iterdir()):
                if fpath.suffix not in (".md", ".txt"):
                    continue
                name_lower = fpath.stem.lower()
                if not any(kw in name_lower for kw in CINEMATIC_KEYWORDS):
                    continue
                try:
                    text = fpath.read_text(encoding="utf-8", errors="replace").strip()
                    if text:
                        combined_text_parts.append(f"--- {fpath} ---\n{text[:3000]}")
                        loaded_files.append(str(fpath))
                except Exception as exc:
                    logger.warning("Failed to read %s: %s", fpath, exc)

        context_text = "\n\n".join(combined_text_parts)

        return {
            "context": context_text,
            "sources": loaded_files,
            "loaded_from_files": bool(loaded_files),
            "beat_detection_rules": [
                {"type": "character_entry", "keywords": ["entra", "enters", "viene", "llega", "appears"]},
                {"type": "character_exit", "keywords": ["sale", "exits", "huye", "escapa", "flee"]},
                {"type": "detail_object", "keywords": ["linterna", "flashlight", "llave", "key", "arma", "weapon"]},
                {"type": "sound_detail", "keywords": ["cruje", "creak", "ruido", "sound", "silencio", "silence", "parpadea", "flicker", "pasos", "footsteps"]},
                {"type": "dialogue", "keywords": ["dice", "says", "pregunta", "asks", "whispers"]},
                {"type": "reaction_closeup", "keywords": ["terror", "miedo", "fear", "shock", "sorpresa", "quieta", "quieto", "frozen", "paralizado"]},
                {"type": "threat_reveal", "keywords": ["sombra", "shadow", "oscuridad", "darkness", "figura", "figure", "silueta", "silhouette", "amenaza", "threat"]},
                {"type": "suspense_build", "keywords": ["tensión", "tension", "suspense", "ominous", "dread"]},
                {"type": "reverse_angle", "keywords": ["contraplano", "reverse", "over shoulder", "desde atrás"]},
                {"type": "establishing", "keywords": ["establecimiento", "establishing", "exterior", "panoramic"]},
            ],
            "coverage_rules": [
                {"condition": "dialogue+action+threat", "shots": 5, "label": "complete coverage"},
                {"condition": "threat+exit_or_action", "shots": 4, "label": "threat resolution"},
                {"condition": "action+dialogue", "shots": 4, "label": "action dialogue"},
                {"condition": "default", "shots": 3, "label": "minimum coverage"},
            ],
        }


cinematic_interpretation_context_service = CinematicInterpretationContextService()
