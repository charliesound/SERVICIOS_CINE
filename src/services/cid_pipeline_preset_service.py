from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional


class CIDPipelinePresetService:
    def __init__(self) -> None:
        self._presets = [
            {
                "key": "storyboard_from_script",
                "name": "Storyboard desde guion",
                "description": "Convierte un guion en un pipeline simulado de storyboard visual.",
                "task_type": "storyboard",
                "requires_legal_gate": False,
                "default_workflow_key": "still_storyboard_frame",
                "default_backend": "still",
                "stages": [
                    {
                        "id": "script_ingest",
                        "name": "Script Ingest",
                        "type": "ingest",
                        "inputs": ["script_text"],
                        "outputs": ["normalized_script"],
                        "config": {"source": "script"},
                    },
                    {
                        "id": "scene_extraction",
                        "name": "Scene Extraction",
                        "type": "analysis",
                        "inputs": ["normalized_script"],
                        "outputs": ["scene_beats", "shot_candidates"],
                        "config": {"granularity": "scene"},
                    },
                    {
                        "id": "frame_generation",
                        "name": "Storyboard Frame Generation",
                        "type": "generation",
                        "inputs": ["shot_candidates", "visual_style"],
                        "outputs": ["storyboard_frames"],
                        "config": {"aspect_ratio": "16:9"},
                    },
                    {
                        "id": "review_export",
                        "name": "Review Export",
                        "type": "delivery",
                        "inputs": ["storyboard_frames"],
                        "outputs": ["review_package"],
                        "config": {"format": "pdf_bundle"},
                    },
                ],
            },
            {
                "key": "teaser_from_script",
                "name": "Teaser desde guion",
                "description": "Genera un pipeline simulado de teaser a partir de un guion o sinopsis.",
                "task_type": "teaser",
                "requires_legal_gate": False,
                "default_workflow_key": "video_text_to_video_base",
                "default_backend": "video",
                "stages": [
                    {
                        "id": "story_ingest",
                        "name": "Story Ingest",
                        "type": "ingest",
                        "inputs": ["script_text", "tone"],
                        "outputs": ["teaser_brief"],
                        "config": {"source": "script_or_synopsis"},
                    },
                    {
                        "id": "beat_selection",
                        "name": "Beat Selection",
                        "type": "analysis",
                        "inputs": ["teaser_brief"],
                        "outputs": ["selected_beats", "narrative_arc"],
                        "config": {"target_duration_seconds": 45},
                    },
                    {
                        "id": "shot_generation",
                        "name": "Shot Generation",
                        "type": "generation",
                        "inputs": ["selected_beats", "visual_style"],
                        "outputs": ["teaser_shots"],
                        "config": {"format": "animatic"},
                    },
                    {
                        "id": "assembly_preview",
                        "name": "Assembly Preview",
                        "type": "assembly",
                        "inputs": ["teaser_shots", "narrative_arc"],
                        "outputs": ["teaser_preview"],
                        "config": {"audio_bed": "temp_music"},
                    },
                ],
            },
            {
                "key": "ai_dubbing_with_legal_gate",
                "name": "Doblaje IA con Legal Gate",
                "description": "Pipeline simulado de doblaje con control legal para consentimiento y derechos.",
                "task_type": "dubbing",
                "requires_legal_gate": True,
                "default_workflow_key": "dubbing_voice_clone_single",
                "default_backend": "dubbing",
                "stages": [
                    {
                        "id": "dialogue_ingest",
                        "name": "Dialogue Ingest",
                        "type": "ingest",
                        "inputs": ["dialogue_script", "reference_audio"],
                        "outputs": ["dialogue_segments"],
                        "config": {"language": "source"},
                    },
                    {
                        "id": "legal_gate",
                        "name": "Legal Gate",
                        "type": "compliance",
                        "inputs": ["consent", "rights_declared", "voice_cloning"],
                        "outputs": ["legal_decision"],
                        "config": {"blocking": True},
                    },
                    {
                        "id": "voice_preparation",
                        "name": "Voice Preparation",
                        "type": "preprocess",
                        "inputs": ["dialogue_segments", "legal_decision"],
                        "outputs": ["clean_reference_voice"],
                        "config": {"normalize": True},
                    },
                    {
                        "id": "dub_generation",
                        "name": "Dub Generation",
                        "type": "generation",
                        "inputs": ["clean_reference_voice", "translated_lines"],
                        "outputs": ["dubbed_audio"],
                        "config": {"mode": "simulated"},
                    },
                    {
                        "id": "dub_qc",
                        "name": "Dub QC",
                        "type": "quality_control",
                        "inputs": ["dubbed_audio"],
                        "outputs": ["delivery_audio", "qc_report"],
                        "config": {"lipsync_check": "manual_review"},
                    },
                ],
            },
            {
                "key": "sound_cleanup",
                "name": "Limpieza de sonido",
                "description": "Pipeline simulado para limpieza, reduccion de ruido y entrega de audio.",
                "task_type": "sound_cleanup",
                "requires_legal_gate": False,
                "default_workflow_key": None,
                "default_backend": "lab",
                "stages": [
                    {
                        "id": "audio_ingest",
                        "name": "Audio Ingest",
                        "type": "ingest",
                        "inputs": ["source_audio"],
                        "outputs": ["indexed_audio"],
                        "config": {"detect_channels": True},
                    },
                    {
                        "id": "noise_profile",
                        "name": "Noise Profile",
                        "type": "analysis",
                        "inputs": ["indexed_audio"],
                        "outputs": ["noise_profile", "issue_report"],
                        "config": {"strategy": "spectral"},
                    },
                    {
                        "id": "cleanup_pass",
                        "name": "Cleanup Pass",
                        "type": "processing",
                        "inputs": ["indexed_audio", "noise_profile"],
                        "outputs": ["clean_audio"],
                        "config": {"repair_level": "balanced"},
                    },
                    {
                        "id": "loudness_qc",
                        "name": "Loudness QC",
                        "type": "quality_control",
                        "inputs": ["clean_audio"],
                        "outputs": ["delivery_audio", "loudness_report"],
                        "config": {"target_lufs": -16},
                    },
                ],
            },
            {
                "key": "audiovisual_pitch_deck",
                "name": "Pitch deck audiovisual",
                "description": "Pipeline simulado para convertir materiales de proyecto en un pitch deck audiovisual.",
                "task_type": "pitch_deck",
                "requires_legal_gate": False,
                "default_workflow_key": "still_text_to_image_pro",
                "default_backend": "still",
                "stages": [
                    {
                        "id": "materials_ingest",
                        "name": "Materials Ingest",
                        "type": "ingest",
                        "inputs": ["project_brief", "script_text", "references"],
                        "outputs": ["normalized_materials"],
                        "config": {"sources": ["brief", "script", "references"]},
                    },
                    {
                        "id": "hook_extraction",
                        "name": "Hook Extraction",
                        "type": "analysis",
                        "inputs": ["normalized_materials"],
                        "outputs": ["logline", "audience_hooks", "slide_outline"],
                        "config": {"focus": "commercial_positioning"},
                    },
                    {
                        "id": "visual_concepts",
                        "name": "Visual Concepts",
                        "type": "generation",
                        "inputs": ["slide_outline", "visual_style"],
                        "outputs": ["concept_boards"],
                        "config": {"format": "key_visuals"},
                    },
                    {
                        "id": "deck_assembly",
                        "name": "Deck Assembly",
                        "type": "assembly",
                        "inputs": ["logline", "audience_hooks", "concept_boards"],
                        "outputs": ["pitch_deck_package"],
                        "config": {"format": "presentation_bundle"},
                    },
                ],
            },
        ]

    def list_presets(self) -> list[dict[str, Any]]:
        return [self._to_response_payload(preset) for preset in self._presets]

    def get_preset(self, preset_key: str) -> Optional[dict[str, Any]]:
        normalized_key = (preset_key or "").strip().lower()
        for preset in self._presets:
            if preset["key"] == normalized_key:
                return deepcopy(preset)
        return None

    def resolve_preset(self, preset_key: Optional[str], intent: Optional[str]) -> dict[str, Any]:
        if preset_key:
            preset = self.get_preset(preset_key)
            if preset is None:
                raise ValueError("Unknown CID pipeline preset")
            return preset

        detected_key = self._detect_preset_from_intent(intent or "")
        return deepcopy(self.get_preset(detected_key) or self._presets[0])

    def _detect_preset_from_intent(self, intent: str) -> str:
        normalized_intent = intent.strip().lower()
        if any(keyword in normalized_intent for keyword in {"doblaje", "dubbing", "voice clone", "voz"}):
            return "ai_dubbing_with_legal_gate"
        if any(keyword in normalized_intent for keyword in {"teaser", "trailer", "promo"}):
            return "teaser_from_script"
        if any(keyword in normalized_intent for keyword in {"sonido", "audio cleanup", "noise", "limpieza"}):
            return "sound_cleanup"
        if any(keyword in normalized_intent for keyword in {"pitch", "deck", "investor", "sales"}):
            return "audiovisual_pitch_deck"
        return "storyboard_from_script"

    def _to_response_payload(self, preset: dict[str, Any]) -> dict[str, Any]:
        return {
            "key": preset["key"],
            "name": preset["name"],
            "description": preset["description"],
            "task_type": preset["task_type"],
            "mode": "simulated",
            "requires_legal_gate": bool(preset.get("requires_legal_gate", False)),
            "default_workflow_key": preset.get("default_workflow_key"),
            "default_backend": preset.get("default_backend"),
            "stage_count": len(preset.get("stages", [])),
        }


cid_pipeline_preset_service = CIDPipelinePresetService()
