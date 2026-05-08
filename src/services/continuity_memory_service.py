from __future__ import annotations

from schemas.cid_script_to_prompt_schema import ScriptScene


class ContinuityMemoryService:
    """Build continuity anchors in memory.

    Future versions should persist these memories per tenant and project, but this
    initial service stays DB-free and deterministic.
    """

    def build_scene_memory(self, scene: ScriptScene) -> dict[str, list[str] | str]:
        return {
            "scene_id": scene.scene_id,
            "character_anchors": [f"character:{character.lower()}" for character in scene.characters],
            "location_anchors": [f"location:{scene.location.lower()}"] if scene.location else [],
            "tone_anchors": [f"tone:{scene.emotional_tone}"] if scene.emotional_tone else [],
            "palette_anchors": self._infer_palette(scene),
        }

    def build_project_visual_bible(self, scenes: list[ScriptScene]) -> dict[str, list[str]]:
        character_anchors = sorted({f"character:{character.lower()}" for scene in scenes for character in scene.characters})
        location_anchors = sorted({f"location:{scene.location.lower()}" for scene in scenes if scene.location})
        tone_anchors = sorted({f"tone:{scene.emotional_tone}" for scene in scenes if scene.emotional_tone})
        palette_anchors = sorted({anchor for scene in scenes for anchor in self._infer_palette(scene)})
        return {
            "character_visual_memory": character_anchors,
            "location_visual_memory": location_anchors,
            "sequence_style_memory": tone_anchors,
            "project_visual_bible": palette_anchors,
        }

    def build_continuity_anchors(self, scene: ScriptScene, project_memory: dict[str, list[str]] | None = None) -> list[str]:
        memory = self.build_scene_memory(scene)
        anchors = []
        for key in ("character_anchors", "location_anchors", "tone_anchors", "palette_anchors"):
            anchors.extend(memory.get(key, []))
        anchors.extend(scene.visual_anchors)
        if project_memory:
            anchors.extend(project_memory.get("project_visual_bible", [])[:2])
        cleaned: list[str] = []
        seen: set[str] = set()
        for anchor in anchors:
            normalized = str(anchor).strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            cleaned.append(normalized)
        return cleaned

    def _infer_palette(self, scene: ScriptScene) -> list[str]:
        time_of_day = (scene.time_of_day or "").lower()
        if time_of_day in {"night", "noche"}:
            return ["palette:charcoal_amber", "palette:controlled_cyan"]
        if time_of_day in {"day", "dia", "día"}:
            return ["palette:natural_daylight", "palette:soft_neutral"]
        return ["palette:premium_cinematic_saas"]


continuity_memory_service = ContinuityMemoryService()
