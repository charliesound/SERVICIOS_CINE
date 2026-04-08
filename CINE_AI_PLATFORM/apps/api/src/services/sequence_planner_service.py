from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from src.schemas.sequence_plan import SequencePlanRequest
from src.services.cinematic_breakdown_service import CinematicBreakdownService
from src.services.cinematic_planning_service import CinematicPlanningService
from src.services.continuity_formal_service import ContinuityFormalService
from src.services.screenplay_parser_service import ScreenplayParserService
from src.services.sequence_semantic_context_service import SequenceSemanticContextService
from src.services.storyboard_grounding_service import StoryboardGroundingService
from src.settings import settings


class SequencePlannerService:
    _DEFAULT_STYLE_PROFILE = "cinematic still"
    _DEFAULT_CONTINUITY_MODE = "balanced"

    _CHARACTER_STOPWORDS = {
        "el",
        "la",
        "los",
        "las",
        "un",
        "una",
        "de",
        "del",
        "al",
        "y",
        "o",
        "interior",
        "exterior",
        "int",
        "ext",
        "dia",
        "noche",
        "tarde",
        "amanecer",
        "atardecer",
        "camara",
        "plano",
        "casa",
        "calle",
        "salon",
        "sala",
        "oficina",
        "parque",
        "bosque",
        "playa",
        "bar",
        "hospital",
        "escuela",
        "estacion",
        "afuera",
        "adentro",
    }

    _LOCATION_ALIASES = {
        "interior": ("interior", "int.", "int "),
        "exterior": ("exterior", "ext.", "ext "),
        "casa": ("casa", "hogar", "apartamento", "departamento"),
        "calle": ("calle", "avenida", "acera"),
        "oficina": ("oficina", "despacho"),
        "parque": ("parque", "plaza", "jardin"),
        "bosque": ("bosque", "selva", "montana", "montana"),
        "playa": ("playa", "costa", "orilla"),
        "hospital": ("hospital", "clinica"),
        "escuela": ("escuela", "colegio", "aula"),
        "bar": ("bar", "cafe", "cafeteria", "restaurante"),
        "estacion": ("estacion", "andenes", "terminal"),
    }

    _ACTION_TERMS = (
        "corre",
        "corren",
        "correr",
        "persigue",
        "perseguir",
        "escapa",
        "escapar",
        "choca",
        "golpea",
        "dispara",
        "salta",
        "abre",
        "cierra",
        "entra",
        "sale",
        "gira",
        "huye",
    )

    _EMOTION_TERMS = (
        "llora",
        "llorar",
        "sonrie",
        "sonreir",
        "teme",
        "miedo",
        "duda",
        "recuerda",
        "susurra",
        "grita",
        "silencio",
        "triste",
        "feliz",
        "ansioso",
    )

    _DIALOGUE_TERMS = (
        "dice",
        "pregunta",
        "responde",
        "contesta",
        "dialoga",
        "habla",
        "murmura",
    )

    def __init__(
        self,
        semantic_context_service: Optional[SequenceSemanticContextService] = None,
        screenplay_parser_service: Optional[ScreenplayParserService] = None,
        cinematic_breakdown_service: Optional[CinematicBreakdownService] = None,
        cinematic_planning_service: Optional[CinematicPlanningService] = None,
        storyboard_grounding_service: Optional[StoryboardGroundingService] = None,
        continuity_formal_service: Optional[ContinuityFormalService] = None,
    ) -> None:
        self.semantic_context_service = semantic_context_service
        self.screenplay_parser_service = screenplay_parser_service or ScreenplayParserService()
        self.cinematic_breakdown_service = cinematic_breakdown_service or CinematicBreakdownService()
        self.cinematic_planning_service = cinematic_planning_service or CinematicPlanningService()
        self.storyboard_grounding_service = storyboard_grounding_service or StoryboardGroundingService()
        self.continuity_formal_service = continuity_formal_service or ContinuityFormalService()

    def plan_sequence(self, payload: SequencePlanRequest) -> Dict[str, Any]:
        script_text = payload.script_text.strip()
        if not script_text:
            raise ValueError("script_text must be a non-empty string")
        style_profile = payload.style_profile or self._DEFAULT_STYLE_PROFILE
        continuity_mode = (payload.continuity_mode or self._DEFAULT_CONTINUITY_MODE).strip().lower()
        semantic_prompt_enrichment_enabled, semantic_prompt_enrichment_max_chars = self._resolve_semantic_prompt_enrichment_config(payload)
        parsed_scenes = self.screenplay_parser_service.parse_script(script_text)
        scene_breakdowns = self.cinematic_breakdown_service.build_scene_breakdowns(parsed_scenes) if parsed_scenes else []

        if parsed_scenes:
            planned_beats = self.cinematic_planning_service.plan_beats(scene_breakdowns)
            fallback_beats = self._build_beats_from_parsed_scenes(parsed_scenes)
            beats = planned_beats if planned_beats else fallback_beats
            characters = self._extract_characters_from_scene_breakdowns(scene_breakdowns) or self._extract_characters_from_parsed_scenes(parsed_scenes)
            locations = self._extract_locations_from_scene_breakdowns(scene_breakdowns) or self._extract_locations_from_parsed_scenes(parsed_scenes)
        else:
            beats = self._segment_into_beats(script_text)
            characters = self._detect_characters(script_text)
            locations = self._detect_locations(script_text)

        if not beats:
            beats = self._segment_into_beats(script_text)
        if not characters:
            characters = self._detect_characters(script_text)
        if not locations:
            locations = self._detect_locations(script_text)

        semantic_context = self._retrieve_semantic_context(payload, script_text)
        shots = self._build_shots(
            beats=beats,
            style_profile=style_profile,
            continuity_mode=continuity_mode,
            characters=characters,
            locations=locations,
            scene_breakdowns=scene_breakdowns,
        )

        continuity_notes = self._build_continuity_notes(
            continuity_mode=continuity_mode,
            characters=characters,
            locations=locations,
            semantic_context=semantic_context,
        )
        render_inputs = self._build_render_inputs(
            payload=payload,
            style_profile=style_profile,
            continuity_mode=continuity_mode,
            shots=shots,
            characters=characters,
            semantic_context=semantic_context,
            semantic_prompt_enrichment_enabled=semantic_prompt_enrichment_enabled,
            semantic_prompt_enrichment_max_chars=semantic_prompt_enrichment_max_chars,
        )

        sequence_label = payload.sequence_id or "sequence_auto"
        sequence_summary = (
            f"{sequence_label}: {len(beats)} beats, {len(shots)} shots, "
            f"{len(characters)} characters, {len(locations)} locations, style={style_profile}"
        )

        return {
            "ok": True,
            "sequence_summary": sequence_summary,
            "parsed_scenes": parsed_scenes,
            "scene_breakdowns": scene_breakdowns,
            "beats": beats,
            "shots": shots,
            "characters_detected": characters,
            "locations_detected": locations,
            "continuity_notes": continuity_notes,
            "semantic_context": semantic_context,
            "semantic_prompt_enrichment": {
                "enabled": semantic_prompt_enrichment_enabled,
                "max_chars": semantic_prompt_enrichment_max_chars,
            },
            "render_inputs": render_inputs,
        }

    def _build_beats_from_parsed_scenes(self, parsed_scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        beats: List[Dict[str, Any]] = []

        for scene in parsed_scenes:
            if not isinstance(scene, dict):
                continue

            scene_id = str(scene.get("scene_id") or "scene").strip() or "scene"
            heading = str(scene.get("heading") or "").strip()
            action_blocks = scene.get("action_blocks") if isinstance(scene.get("action_blocks"), list) else []
            dialogue_blocks = scene.get("dialogue_blocks") if isinstance(scene.get("dialogue_blocks"), list) else []

            for action_text in action_blocks:
                cleaned_action = self._clean_text(str(action_text or ""))
                if not cleaned_action:
                    continue
                beat_index = len(beats) + 1
                beat_text = f"{heading} {cleaned_action}".strip() if heading else cleaned_action
                beats.append(
                    {
                        "beat_id": f"{scene_id}_action_{beat_index:03d}",
                        "index": beat_index,
                        "summary": self._summarize_fragment(cleaned_action),
                        "text": beat_text,
                        "intent": "action",
                    }
                )

            for dialogue_block in dialogue_blocks:
                if not isinstance(dialogue_block, dict):
                    continue
                character = self._clean_text(str(dialogue_block.get("character") or ""))
                dialogue_text = self._clean_text(str(dialogue_block.get("text") or ""))
                if not dialogue_text:
                    continue
                beat_index = len(beats) + 1
                prefix = f"{character}: " if character else ""
                beat_text = f"{heading} {prefix}{dialogue_text}".strip() if heading else f"{prefix}{dialogue_text}".strip()
                beats.append(
                    {
                        "beat_id": f"{scene_id}_dialogue_{beat_index:03d}",
                        "index": beat_index,
                        "summary": self._summarize_fragment(f"{prefix}{dialogue_text}".strip()),
                        "text": beat_text,
                        "intent": "dialogue",
                    }
                )

        return beats

    def _extract_characters_from_parsed_scenes(self, parsed_scenes: List[Dict[str, Any]]) -> List[str]:
        characters: List[str] = []
        seen = set()

        for scene in parsed_scenes:
            if not isinstance(scene, dict):
                continue
            items = scene.get("characters_detected") if isinstance(scene.get("characters_detected"), list) else []
            for item in items:
                normalized = self._normalize_character_name(str(item or ""))
                if not normalized:
                    continue
                lowered = normalized.lower()
                if lowered in seen:
                    continue
                seen.add(lowered)
                characters.append(normalized)

        return characters[:8]

    def _extract_locations_from_parsed_scenes(self, parsed_scenes: List[Dict[str, Any]]) -> List[str]:
        locations: List[str] = []
        seen = set()

        for scene in parsed_scenes:
            if not isinstance(scene, dict):
                continue
            location = self._clean_text(str(scene.get("location") or ""))
            if not location:
                continue
            lowered = location.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            locations.append(location)

        return locations[:8]

    def _extract_characters_from_scene_breakdowns(self, scene_breakdowns: List[Dict[str, Any]]) -> List[str]:
        characters: List[str] = []
        seen = set()

        for scene in scene_breakdowns:
            if not isinstance(scene, dict):
                continue

            for item in scene.get("characters_present", []):
                normalized = self._normalize_character_name(str(item or ""))
                if not normalized:
                    continue
                lowered = normalized.lower()
                if lowered in seen:
                    continue
                seen.add(lowered)
                characters.append(normalized)

        return characters[:8]

    def _extract_locations_from_scene_breakdowns(self, scene_breakdowns: List[Dict[str, Any]]) -> List[str]:
        locations: List[str] = []
        seen = set()

        for scene in scene_breakdowns:
            if not isinstance(scene, dict):
                continue

            location = self._clean_text(str(scene.get("location") or ""))
            if not location:
                continue
            lowered = location.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            locations.append(location)

        return locations[:8]

    def _segment_into_beats(self, script_text: str) -> List[Dict[str, Any]]:
        paragraphs = [
            self._clean_text(fragment)
            for fragment in re.split(r"\n{2,}", script_text)
            if self._clean_text(fragment)
        ]

        if len(paragraphs) >= 2:
            fragments = paragraphs
        else:
            sentences = [
                self._clean_text(fragment)
                for fragment in re.split(r"(?<=[.!?])\s+", script_text)
                if self._clean_text(fragment)
            ]
            if not sentences:
                fragments = [self._clean_text(script_text)]
            elif len(sentences) == 1:
                fragments = sentences
            else:
                fragments = []
                step = 2
                for index in range(0, len(sentences), step):
                    fragments.append(self._clean_text(" ".join(sentences[index : index + step])))

        beats: List[Dict[str, Any]] = []
        for index, fragment in enumerate(fragments, start=1):
            beats.append(
                {
                    "beat_id": f"beat_{index:03d}",
                    "index": index,
                    "summary": self._summarize_fragment(fragment),
                    "text": fragment,
                    "intent": self._detect_intent(fragment, index),
                }
            )

        return beats

    def _detect_characters(self, script_text: str) -> List[str]:
        candidates = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", script_text)
        upper_candidates = [token.title() for token in re.findall(r"\b[A-Z]{2,}\b", script_text)]

        unique: List[str] = []
        seen = set()

        for raw_candidate in candidates + upper_candidates:
            normalized = self._normalize_character_name(raw_candidate)
            if not normalized:
                continue

            key = normalized.lower()
            if key in self._CHARACTER_STOPWORDS:
                continue
            if key in seen:
                continue

            seen.add(key)
            unique.append(normalized)

        return unique[:8]

    def _detect_locations(self, script_text: str) -> List[str]:
        text_lower = script_text.lower()
        locations: List[str] = []

        for label, aliases in self._LOCATION_ALIASES.items():
            if any(alias in text_lower for alias in aliases):
                locations.append(label)

        named_locations = re.findall(
            r"\b(?:en|desde|hacia|sobre)\s+([A-Z][A-Za-z0-9\-]*(?:\s+[A-Z][A-Za-z0-9\-]*){0,2})",
            script_text,
        )
        for item in named_locations:
            cleaned = self._clean_text(item)
            if cleaned and cleaned.lower() not in {location.lower() for location in locations}:
                locations.append(cleaned)

        return locations[:8]

    def _build_shots(
        self,
        beats: List[Dict[str, Any]],
        style_profile: str,
        continuity_mode: str,
        characters: List[str],
        locations: List[str],
        scene_breakdowns: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        total_beats = len(beats)
        shots: List[Dict[str, Any]] = []

        for index, beat in enumerate(beats, start=1):
            fragment_text = beat["text"]
            shot_intent = beat.get("shot_intent")
            beat_type = beat.get("beat_type")
            shot_type = self._resolve_shot_type_from_planning(shot_intent, beat_type, fragment_text, index, total_beats)
            camera = self._camera_for_shot(shot_type)
            motion = self._motion_for_text(fragment_text)

            scene_breakdown = self._find_scene_breakdown_for_beat(beat, scene_breakdowns)
            grounding = self.storyboard_grounding_service.ground_shot(
                shot_intent=shot_intent,
                beat_type=beat_type,
                scene_breakdown=scene_breakdown,
                beat_text=fragment_text,
                characters=characters,
                locations=locations,
            )

            prompt_base_raw = self._build_prompt_base(
                fragment_text=fragment_text,
                shot_type=shot_type,
                style_profile=style_profile,
                characters=characters,
                locations=locations,
            )
            prompt_base = self.storyboard_grounding_service.enrich_prompt_base(prompt_base_raw, grounding)

            continuity_formal = self.continuity_formal_service.assign_continuity(
                shot_intent=shot_intent,
                beat_type=beat_type,
                characters=characters,
                shot_index=index,
                previous_shots=shots,
            )

            shots.append(
                {
                    "shot_id": f"shot_{index:03d}",
                    "beat_id": beat["beat_id"],
                    "index": index,
                    "shot_type": shot_type,
                    "camera": camera,
                    "motion": motion,
                    "prompt": prompt_base,
                    "prompt_base": prompt_base,
                    "negative_prompt": "lowres, blurry, artifacts, deformed hands, watermark, text",
                    "continuity": self._build_shot_continuity(index, continuity_mode, characters, locations),
                    "grounding": grounding,
                    "continuity_formal": continuity_formal,
                }
            )

        return shots

    def _find_scene_breakdown_for_beat(
        self,
        beat: Dict[str, Any],
        scene_breakdowns: Optional[List[Dict[str, Any]]],
    ) -> Optional[Dict[str, Any]]:
        if not scene_breakdowns:
            return None

        beat_id = str(beat.get("beat_id") or "")
        for breakdown in scene_breakdowns:
            if not isinstance(breakdown, dict):
                continue
            scene_id = str(breakdown.get("scene_id") or "")
            if scene_id and beat_id.startswith(scene_id):
                return breakdown

        return scene_breakdowns[0] if scene_breakdowns else None

    def _resolve_shot_type_from_planning(
        self,
        shot_intent: Optional[str],
        beat_type: Optional[str],
        fragment_text: str,
        index: int,
        total_beats: int,
    ) -> str:
        intent_map = {
            "establishing": "establishing_wide",
            "wide": "wide_action",
            "medium": "medium",
            "close_up": "close_up",
            "two_shot": "medium",
            "over_shoulder": "over_shoulder_dialogue",
            "insert": "extreme_close_up",
            "reaction": "close_up_emotion",
            "detail": "extreme_close_up",
        }

        if shot_intent and shot_intent in intent_map:
            return intent_map[shot_intent]

        if beat_type == "dialogue":
            return "over_shoulder_dialogue"

        if beat_type == "action":
            return "wide_action"

        if beat_type == "insert":
            return "extreme_close_up"

        return self._select_shot_type(fragment_text, index, total_beats)

    def _build_continuity_notes(
        self,
        continuity_mode: str,
        characters: List[str],
        locations: List[str],
        semantic_context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        notes = [f"continuity_mode={continuity_mode}"]

        if characters:
            notes.append(f"Keep visual identity stable for: {', '.join(characters)}.")
        else:
            notes.append("Define a primary character profile before final render.")

        if locations:
            notes.append(f"Keep environment continuity for: {', '.join(locations)}.")
        else:
            notes.append("Define a fixed location palette before final render.")

        notes.append("Preserve camera direction and lighting continuity across adjacent beats.")

        if isinstance(semantic_context, dict):
            for hint in semantic_context.get("continuity_hints", []):
                if isinstance(hint, str) and hint.strip():
                    notes.append(hint.strip())
        return notes

    def _build_render_inputs(
        self,
        payload: SequencePlanRequest,
        style_profile: str,
        continuity_mode: str,
        shots: List[Dict[str, Any]],
        characters: List[str],
        semantic_context: Optional[Dict[str, Any]] = None,
        semantic_prompt_enrichment_enabled: bool = True,
        semantic_prompt_enrichment_max_chars: int = 400,
    ) -> Dict[str, Any]:
        render_jobs: List[Dict[str, Any]] = []
        primary_character_id = self._character_id_candidate(characters)
        use_ipadapter = bool(primary_character_id and continuity_mode in {"strict", "character_locked", "locked"})
        semantic_prompt_context = self._build_semantic_prompt_context(
            semantic_context,
            semantic_prompt_enrichment_enabled=semantic_prompt_enrichment_enabled,
            semantic_prompt_enrichment_max_chars=semantic_prompt_enrichment_max_chars,
        )

        for shot in shots:
            seed_value = 12000 + shot["index"]
            prompt_base = str(shot["prompt_base"] or "").strip()
            prompt_enriched = self._merge_prompt_with_semantic_context(prompt_base, semantic_prompt_context)
            semantic_enrichment_applied = bool(semantic_prompt_context and prompt_enriched != prompt_base)
            semantic_summary_used = semantic_prompt_context if semantic_enrichment_applied else None
            metadata = {
                "planner": "sequence_plan_v1",
                "project_id": payload.project_id,
                "sequence_id": payload.sequence_id,
                "style_profile": style_profile,
                "continuity_mode": continuity_mode,
                "shot_id": shot["shot_id"],
                "beat_id": shot["beat_id"],
            }
            metadata = {key: value for key, value in metadata.items() if value is not None}

            request_payload = {
                "prompt": {
                    "3": {
                        "class_type": "KSampler",
                        "inputs": {
                            "model": ["4", 0],
                            "positive": ["6", 0],
                            "negative": ["7", 0],
                            "latent_image": ["5", 0],
                            "seed": seed_value,
                            "steps": 28,
                            "cfg": 6.5,
                            "sampler_name": "euler",
                            "scheduler": "normal",
                            "denoise": 1,
                        },
                    },
                    "4": {
                        "class_type": "CheckpointLoaderSimple",
                        "inputs": {
                            "ckpt_name": "sd_xl_base_1.0.safetensors",
                        },
                    },
                    "5": {
                        "class_type": "EmptyLatentImage",
                        "inputs": {
                            "width": 1024,
                            "height": 576,
                            "batch_size": 1,
                        },
                    },
                    "6": {
                        "class_type": "CLIPTextEncode",
                        "inputs": {
                            "text": prompt_enriched,
                            "clip": ["4", 1],
                        },
                    },
                    "7": {
                        "class_type": "CLIPTextEncode",
                        "inputs": {
                            "text": shot["negative_prompt"],
                            "clip": ["4", 1],
                        },
                    },
                    "8": {
                        "class_type": "VAEDecode",
                        "inputs": {
                            "samples": ["3", 0],
                            "vae": ["4", 2],
                        },
                    },
                    "9": {
                        "class_type": "SaveImage",
                        "inputs": {
                            "images": ["8", 0],
                            "filename_prefix": f"{payload.sequence_id or 'sequence_auto'}_{shot['shot_id']}",
                        },
                    },
                },
                "metadata": metadata,
            }

            render_context: Dict[str, Any] = {}
            if primary_character_id:
                render_context["character_id"] = primary_character_id
                render_context["use_ipadapter"] = use_ipadapter

            if isinstance(semantic_context, dict) and int(semantic_context.get("count") or 0) > 0:
                render_context["semantic_context"] = {
                    "summary_text": str(semantic_context.get("summary_text") or ""),
                    "entity_types": semantic_context.get("entity_types") if isinstance(semantic_context.get("entity_types"), list) else [],
                    "items": semantic_context.get("items") if isinstance(semantic_context.get("items"), list) else [],
                }

            render_jobs.append(
                {
                    "shot_id": shot["shot_id"],
                    "prompt_base": prompt_base,
                    "prompt_enriched": prompt_enriched,
                    "semantic_summary_used": semantic_summary_used,
                    "semantic_enrichment_applied": semantic_enrichment_applied,
                    "request_payload": request_payload,
                    "render_context": render_context,
                }
            )

        return {
            "target_endpoint": "/api/render/jobs",
            "workflow_key": "still_sdxl_base_v1",
            "jobs": render_jobs,
        }

    def _build_semantic_prompt_context(
        self,
        semantic_context: Optional[Dict[str, Any]],
        *,
        semantic_prompt_enrichment_enabled: bool,
        semantic_prompt_enrichment_max_chars: int,
    ) -> str:
        if not semantic_prompt_enrichment_enabled:
            return ""

        if not isinstance(semantic_context, dict):
            return ""

        summary_text = str(semantic_context.get("summary_text") or "").strip()
        if not summary_text:
            return ""

        max_chars = max(0, int(semantic_prompt_enrichment_max_chars))
        if max_chars <= 0:
            return ""

        return summary_text[:max_chars].strip()

    def _resolve_semantic_prompt_enrichment_config(self, payload: SequencePlanRequest) -> tuple[bool, int]:
        enabled_override = payload.semantic_prompt_enrichment_enabled
        max_chars_override = payload.semantic_prompt_enrichment_max_chars

        enrichment_enabled = (
            bool(enabled_override)
            if isinstance(enabled_override, bool)
            else bool(settings.sequence_semantic_prompt_enrichment_enabled)
        )
        max_chars = (
            int(max_chars_override)
            if isinstance(max_chars_override, int)
            else int(settings.sequence_semantic_prompt_enrichment_max_chars)
        )

        return enrichment_enabled, max(0, max_chars)

    def _merge_prompt_with_semantic_context(self, prompt_base: str, semantic_prompt_context: str) -> str:
        base_prompt = str(prompt_base or "").strip()
        semantic_context_text = str(semantic_prompt_context or "").strip()

        if not semantic_context_text:
            return base_prompt

        return f"{base_prompt}. Semantic context: {semantic_context_text}"

    def _retrieve_semantic_context(self, payload: SequencePlanRequest, script_text: str) -> Dict[str, Any]:
        normalized_query_text = (script_text or "").strip()[:1500]

        if self.semantic_context_service is None:
            return {
                "enabled": False,
                "query": {
                    "text": normalized_query_text,
                    "project_id": payload.project_id,
                    "sequence_id": payload.sequence_id,
                    "scene_id": None,
                    "shot_id": None,
                    "limit": 5,
                },
                "count": 0,
                "entity_types": [],
                "summary_text": "",
                "continuity_hints": [],
                "items": [],
                "error": None,
            }

        return self.semantic_context_service.retrieve_relevant_context(
            project_id=payload.project_id,
            sequence_id=payload.sequence_id,
            query_text=normalized_query_text,
        )

    def _select_shot_type(self, fragment_text: str, index: int, total_beats: int) -> str:
        normalized = fragment_text.lower()

        if index == 1:
            return "establishing_wide"
        if any(term in normalized for term in self._ACTION_TERMS):
            return "wide_action"
        if any(term in normalized for term in self._EMOTION_TERMS):
            return "close_up_emotion"
        if any(term in normalized for term in self._DIALOGUE_TERMS) or '"' in fragment_text:
            return "over_shoulder_dialogue"
        if index == total_beats and total_beats > 1:
            return "close_up"
        return "medium"

    def _camera_for_shot(self, shot_type: str) -> str:
        camera_by_type = {
            "establishing_wide": "24mm wide",
            "wide_action": "28mm wide",
            "over_shoulder_dialogue": "50mm over-shoulder",
            "close_up_emotion": "85mm close-up",
            "close_up": "85mm close-up",
            "medium": "50mm medium",
        }
        return camera_by_type.get(shot_type, "50mm medium")

    def _motion_for_text(self, fragment_text: str) -> str:
        normalized = fragment_text.lower()
        if any(term in normalized for term in self._ACTION_TERMS):
            return "tracking"
        if any(term in normalized for term in self._DIALOGUE_TERMS):
            return "slow_push_in"
        return "locked_off"

    def _build_prompt_base(
        self,
        fragment_text: str,
        shot_type: str,
        style_profile: str,
        characters: List[str],
        locations: List[str],
    ) -> str:
        main_characters = ", ".join(characters[:2]) if characters else "undefined characters"
        main_location = locations[0] if locations else "unspecified location"

        return (
            f"{style_profile}, {shot_type.replace('_', ' ')}, "
            f"{fragment_text}, characters: {main_characters}, "
            f"location: {main_location}, cinematic still, detailed lighting"
        )

    def _build_shot_continuity(
        self,
        index: int,
        continuity_mode: str,
        characters: List[str],
        locations: List[str],
    ) -> str:
        if index == 1:
            return "Establish baseline wardrobe, lighting and camera axis for following shots."

        character_text = ", ".join(characters[:2]) if characters else "same main subject"
        location_text = locations[0] if locations else "same environment"

        return (
            f"continuity_mode={continuity_mode}; keep look consistent for {character_text}; "
            f"preserve environment continuity with {location_text}."
        )

    def _detect_intent(self, fragment_text: str, index: int) -> str:
        normalized = fragment_text.lower()
        if any(term in normalized for term in self._ACTION_TERMS):
            return "action"
        if any(term in normalized for term in self._DIALOGUE_TERMS) or '"' in fragment_text:
            return "dialogue"
        if any(term in normalized for term in self._EMOTION_TERMS):
            return "emotion"
        if index == 1:
            return "setup"
        return "progression"

    def _summarize_fragment(self, fragment_text: str) -> str:
        words = fragment_text.split()
        if len(words) <= 18:
            return fragment_text
        return " ".join(words[:18]) + "..."

    def _normalize_character_name(self, value: str) -> Optional[str]:
        cleaned = self._clean_text(value)
        if not cleaned:
            return None

        parts = [part.capitalize() for part in cleaned.split()]
        normalized = " ".join(parts)
        if len(normalized) < 2:
            return None
        return normalized

    def _character_id_candidate(self, characters: List[str]) -> Optional[str]:
        if not characters:
            return None

        slug = re.sub(r"[^a-z0-9]+", "_", characters[0].lower()).strip("_")
        if not slug:
            return None
        return f"char_{slug}"

    def _clean_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
