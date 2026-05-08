from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from schemas.cid_script_to_prompt_schema import (
    DirectorLensDecision,
    DirectorLensProfile,
    ScriptScene,
)


ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = ROOT / "config" / "cid_director_lens_profiles.yaml"


class DirectorLensService:
    def __init__(self) -> None:
        self._profiles_cache: list[DirectorLensProfile] | None = None

    def list_profiles(self) -> list[DirectorLensProfile]:
        return list(self._load_profiles())

    def get_profile(self, lens_id: str) -> DirectorLensProfile:
        for profile in self._load_profiles():
            if profile.lens_id == lens_id:
                return profile
        raise ValueError(f"Unknown director lens profile: {lens_id}")

    def choose_lens_for_scene(
        self,
        scene: ScriptScene,
        requested_lens_id: str | None = "adaptive_auteur_fusion",
    ) -> DirectorLensDecision:
        requested = requested_lens_id or "adaptive_auteur_fusion"
        warnings: list[str] = []

        if requested != "adaptive_auteur_fusion":
            profile = self.get_profile(requested)
            scene_needs = self._scene_needs(scene)
            return DirectorLensDecision(
                scene_id=scene.scene_id,
                selected_lens_id=profile.lens_id,
                selected_lens_name=profile.name,
                reason="requested_lens_applied_directly",
                scene_needs=scene_needs,
                applied_principles=profile.cinematic_principles[:4],
                warnings=warnings,
            )

        profile = self._choose_adaptive_profile(scene)
        scene_needs = self._scene_needs(scene)
        return DirectorLensDecision(
            scene_id=scene.scene_id,
            selected_lens_id=profile.lens_id,
            selected_lens_name=profile.name,
            reason=self._selection_reason(scene, profile),
            scene_needs=scene_needs,
            applied_principles=profile.cinematic_principles[:5],
            warnings=warnings,
        )

    def _load_profiles(self) -> list[DirectorLensProfile]:
        if self._profiles_cache is None:
            with PROFILES_PATH.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
            profiles_payload = payload.get("profiles", []) if isinstance(payload, dict) else []
            self._profiles_cache = [DirectorLensProfile(**item) for item in profiles_payload]
        return self._profiles_cache

    def _choose_adaptive_profile(self, scene: ScriptScene) -> DirectorLensProfile:
        text = f"{scene.heading} {scene.action_summary} {scene.dialogue_summary or ''} {scene.conflict or ''} {scene.dramatic_objective or ''} {scene.emotional_tone or ''}".lower()
        int_ext = (scene.int_ext or "").upper()
        location = (scene.location or "").lower()

        if int_ext == "INT" and any(word in text for word in ["tension", "duda", "culpa", "espera", "decision", "control"]):
            if any(word in text for word in ["hotel", "habitacion", "habitación", "orden", "simetr"]):
                return self.get_profile("formal_symmetry_control")
            return self.get_profile("suspense_geometric_control")

        if int_ext == "EXT" and any(word in text for word in ["viaje", "camina", "paisaje", "vulnerable", "descubre", "asombro"]):
            return self.get_profile("wonder_humanist_blocking")

        if any(word in text for word in ["deseo", "vergüenza", "verguenza", "intimo", "íntimo", "identidad", "amor", "memoria"]):
            return self.get_profile("melodrama_color_identity")

        if any(word in text for word in ["absurdo", "surreal", "poder", "contradiccion", "contradicción", "ritual", "ridiculo", "ridículo"]):
            return self.get_profile("surreal_social_disruption")

        if any(word in text for word in ["politic", "polític", "violencia", "culpa", "corrup", "poder", "crimen"]):
            if any(word in location for word in ["calle", "ciudad", "oficina", "hotel"]):
                return self.get_profile("urban_moral_energy")
            return self.get_profile("suspense_geometric_control")

        if any(word in text for word in ["duelo", "silencio", "agua", "fuego", "memoria", "contempla", "espera quieta"]):
            return self.get_profile("spiritual_time_pressure")

        if any(word in text for word in ["grupo", "ejercito", "equipo", "paisaje", "honor", "viajeros", "multitud"]):
            return self.get_profile("epic_moral_landscape")

        if any(word in text for word in ["sueño", "sueno", "doble", "identidad", "espejo", "inquietante", "pesadilla"]):
            return self.get_profile("dream_identity_fragment")

        return self.get_profile("adaptive_auteur_fusion")

    def _scene_needs(self, scene: ScriptScene) -> list[str]:
        needs: list[str] = []
        if scene.int_ext:
            needs.append(scene.int_ext.lower())
        if scene.time_of_day:
            needs.append(scene.time_of_day.lower())
        if scene.location:
            needs.append(scene.location.lower())
        if scene.emotional_tone:
            needs.append(scene.emotional_tone)
        if scene.dramatic_objective:
            needs.append(scene.dramatic_objective)
        if scene.conflict:
            needs.append(scene.conflict)
        return needs[:8]

    def _selection_reason(self, scene: ScriptScene, profile: DirectorLensProfile) -> str:
        text = f"{scene.heading} {scene.action_summary} {scene.dialogue_summary or ''}".lower()
        if profile.lens_id == "formal_symmetry_control":
            return "selected_for_interior_psychological_pressure_and_order_revealing_disturbance"
        if profile.lens_id == "suspense_geometric_control":
            return "selected_for_information_control_and_latent_threat_inside_the_frame"
        if profile.lens_id == "wonder_humanist_blocking":
            return "selected_for_human_discovery_vulnerability_or_emotional_clarity"
        if profile.lens_id == "melodrama_color_identity":
            return "selected_for_identity_desire_or_intimate_emotional_conflict"
        if profile.lens_id == "surreal_social_disruption":
            return "selected_for_absurd_social_power_or_symbolic_disruption"
        if profile.lens_id == "urban_moral_energy":
            return "selected_for_urban_pressure_power_and_moral_velocity"
        if profile.lens_id == "spiritual_time_pressure":
            return "selected_for_contemplation_grief_or_temporal_interiority"
        if profile.lens_id == "epic_moral_landscape":
            return "selected_for_group_scale_landscape_or_moral_scope"
        if profile.lens_id == "dream_identity_fragment":
            return "selected_for_identity_instability_and_psychological_uncanniness"
        return f"adaptive_selection_defaulted_after_scene_review:{text[:80]}"


director_lens_service = DirectorLensService()
