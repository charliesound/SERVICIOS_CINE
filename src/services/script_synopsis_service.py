from __future__ import annotations

from collections import Counter

from schemas.cid_sequence_first_schema import (
    FullScriptAnalysisResult,
    ScriptSequenceMap,
    ScriptSynopsisResult,
)
from schemas.cid_script_to_prompt_schema import ScriptScene, ScriptSequence
from services.cid_script_scene_parser_service import cid_script_scene_parser_service
from services.script_sequence_mapping_service import (
    script_sequence_mapping_service,
)

GENRE_KEYWORDS: dict[str, list[str]] = {
    "drama": ["decision", "version", "revisa", "discute", "tension"],
    "thriller": ["urgente", "corre", "presion", "espera", "tension"],
    "comedy": ["risa", "broma", "gracioso", "funny", "joke"],
    "action": ["corre", "rapido", "persecucion", "explosion", "arma"],
    "sci_fi": ["futurista", "nave", "robot", "ia", "inteligencia"],
}

TONE_CATEGORIES: dict[str, str] = {
    "tension": "tenso_suspense",
    "urgency": "urgente_acelerado",
    "calm": "calmo_reflexivo",
    "dialogue_tension": "dialogo_tenso",
    "focused_professional": "profesional_concentrado",
}

DRAMATIC_STRUCTURE_ACT_RATIOS = {
    "act_one": 0.25,
    "act_two": 0.50,
    "act_three": 0.25,
}


class ScriptSynopsisService:
    def analyze_script(self, script_text: str) -> FullScriptAnalysisResult:
        sequences, scenes, warnings = cid_script_scene_parser_service.parse_script(
            script_text
        )

        if not scenes:
            return FullScriptAnalysisResult(
                synopsis=ScriptSynopsisResult(),
                sequence_map=ScriptSequenceMap(),
                warnings=[*warnings, "no_scenes_found"],
            )

        sequence_map = script_sequence_mapping_service.build_sequence_map(
            scenes, script_text
        )

        synopsis = self._build_synopsis(scenes, sequences, sequence_map)

        return FullScriptAnalysisResult(
            synopsis=synopsis,
            sequence_map=sequence_map,
            warnings=warnings,
        )

    def _build_synopsis(
        self,
        scenes: list[ScriptScene],
        sequences: list[ScriptSequence],
        sequence_map: ScriptSequenceMap,
    ) -> ScriptSynopsisResult:
        char_freq = self._count_character_frequency(scenes)
        main_characters = [c for c, _ in char_freq[:10]]

        main_locations = list(
            dict.fromkeys(s.location for s in scenes if s.location)
        )

        logline = self._build_logline(scenes, main_characters, main_locations)
        synopsis_short = self._build_synopsis_short(scenes)
        synopsis_extended = self._build_synopsis_extended(scenes)
        premise = self._build_premise(scenes)
        theme = self._build_theme(scenes)
        genre = self._infer_genre(scenes)
        tone = self._infer_tone(scenes)
        dramatic_structure = self._build_dramatic_structure(scenes)
        production_notes = self._collect_production_notes(scenes)
        recommended = self._recommend_storyboard_sequences(sequence_map)
        raw_analysis = self._build_raw_analysis(
            scenes, sequences, char_freq
        )

        return ScriptSynopsisResult(
            logline=logline,
            synopsis_short=synopsis_short,
            synopsis_extended=synopsis_extended,
            premise=premise,
            theme=theme,
            genre=genre,
            tone=tone,
            main_characters=main_characters,
            main_locations=main_locations,
            dramatic_structure=dramatic_structure,
            production_notes=production_notes,
            recommended_storyboard_sequences=recommended,
            raw_analysis=raw_analysis,
        )

    def _count_character_frequency(
        self, scenes: list[ScriptScene]
    ) -> list[tuple[str, int]]:
        counter: Counter[str] = Counter()
        for s in scenes:
            for c in s.characters:
                counter[c] += 1
        return counter.most_common()

    def _build_logline(
        self,
        scenes: list[ScriptScene],
        main_characters: list[str],
        main_locations: list[str],
    ) -> str:
        char_str = ", ".join(main_characters[:3]) if main_characters else "characters"
        loc_str = (
            ", ".join(main_locations[:2]) if main_locations else "various locations"
        )
        first_objectives = [
            s.dramatic_objective
            for s in scenes[:3]
            if s.dramatic_objective
        ]
        objective_str = (
            first_objectives[0].replace("_", " ")
            if first_objectives
            else "navigate their world"
        )
        return (
            f"In {loc_str}, {char_str} must {objective_str} "
            f"across {len(scenes)} scenes of escalating stakes."
        )

    def _build_synopsis_short(self, scenes: list[ScriptScene]) -> str:
        parts: list[str] = []
        for s in scenes[:5]:
            label = s.location or s.heading
            summary = s.action_summary
            if summary:
                parts.append(f"{label}: {summary[:200]}")
            else:
                parts.append(label)
        return " | ".join(parts)[:1000]

    def _build_synopsis_extended(self, scenes: list[ScriptScene]) -> str:
        parts: list[str] = []
        for i, s in enumerate(scenes, start=1):
            line_parts = [f"Scene {i}: {s.heading}"]
            if s.action_summary:
                line_parts.append(s.action_summary)
            if s.dialogue_summary:
                line_parts.append(f"Dialogue: {s.dialogue_summary}")
            if s.emotional_tone:
                line_parts.append(f"[{s.emotional_tone}]")
            parts.append(" -- ".join(line_parts))
        return "\n\n".join(parts)[:5000]

    def _build_premise(self, scenes: list[ScriptScene]) -> str:
        objectives = [
            s.dramatic_objective
            for s in scenes
            if s.dramatic_objective
        ]
        if not objectives:
            return "A story unfolds through a series of scenes."
        unique = list(dict.fromkeys(objectives))
        return (
            "A narrative driven by "
            + ", ".join(u.replace("_", " ") for u in unique[:3])
            + "."
        )

    def _build_theme(self, scenes: list[ScriptScene]) -> str:
        combined = " ".join(
            s.raw_text.lower() for s in scenes if s.raw_text
        )
        if "decision" in combined or "version" in combined:
            return "decision_and_accountability"
        if "discute" in combined or "discuss" in combined:
            return "collaboration_and_conflict"
        if "presenta" in combined or "explica" in combined:
            return "knowledge_and_revelation"
        if "tension" in combined or "tensión" in combined:
            return "pressure_and_resilience"
        return "professional_dynamics"

    def _infer_genre(self, scenes: list[ScriptScene]) -> str:
        combined = " ".join(
            s.raw_text.lower() for s in scenes if s.raw_text
        )
        scores: list[tuple[str, int]] = []
        for genre, keywords in GENRE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > 0:
                scores.append((genre, score))
        if not scores:
            return "drama"
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]

    def _infer_tone(self, scenes: list[ScriptScene]) -> str:
        tones = [s.emotional_tone for s in scenes if s.emotional_tone]
        if not tones:
            return "neutral_professional"
        counter = Counter(tones)
        dominant = counter.most_common(1)[0][0]
        return TONE_CATEGORIES.get(dominant, dominant)

    def _build_dramatic_structure(self, scenes: list[ScriptScene]) -> str:
        total = len(scenes)
        if total <= 1:
            return "single_scene"

        act_one_end = max(1, int(total * DRAMATIC_STRUCTURE_ACT_RATIOS["act_one"]))
        act_two_end = max(
            act_one_end + 1,
            int(total * (DRAMATIC_STRUCTURE_ACT_RATIOS["act_one"] + DRAMATIC_STRUCTURE_ACT_RATIOS["act_two"])),
        )

        act1 = scenes[:act_one_end]
        act2 = scenes[act_one_end:act_two_end]
        act3 = scenes[act_two_end:]

        act1_conflict = sum(1 for s in act1 if s.conflict)
        act2_conflict = sum(1 for s in act2 if s.conflict)
        act3_conflict = sum(1 for s in act3 if s.conflict)

        act1_tone = self._act_dominant_tone(act1)
        act2_tone = self._act_dominant_tone(act2)
        act3_tone = self._act_dominant_tone(act3)

        return (
            f"Three-act structure detected ({total} scenes): "
            f"Act I ({len(act1)} scenes, {act1_conflict} conflicts, tone: {act1_tone}) — "
            f"Act II ({len(act2)} scenes, {act2_conflict} conflicts, tone: {act2_tone}) — "
            f"Act III ({len(act3)} scenes, {act3_conflict} conflicts, tone: {act3_tone})"
        )

    def _act_dominant_tone(self, scenes: list[ScriptScene]) -> str:
        tones = [s.emotional_tone for s in scenes if s.emotional_tone]
        if not tones:
            return "neutral"
        return Counter(tones).most_common(1)[0][0]

    def _collect_production_notes(self, scenes: list[ScriptScene]) -> list[str]:
        notes: list[str] = []
        all_needs: list[str] = []
        for s in scenes:
            all_needs.extend(s.production_needs)
        need_counts = Counter(all_needs)
        for need, count in need_counts.most_common():
            notes.append(f"{need} (x{count})")
        unique_chars = {c for s in scenes for c in s.characters}
        notes.append(f"total_unique_characters:{len(unique_chars)}")
        unique_locs = {s.location for s in scenes if s.location}
        notes.append(f"total_unique_locations:{len(unique_locs)}")
        return notes

    def _recommend_storyboard_sequences(
        self, sequence_map: ScriptSequenceMap
    ) -> list[str]:
        scored: list[tuple[str, float]] = []
        for entry in sequence_map.sequences:
            score = 0.0
            if entry.recommended_for_storyboard:
                score += 5.0
            if entry.visual_opportunity == "high":
                score += 3.0
            elif entry.visual_opportunity == "medium":
                score += 1.0
            if entry.suggested_shot_count > 6:
                score += 2.0
            scored.append((entry.sequence_id, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [sid for sid, _ in scored[:5]]

    def _build_raw_analysis(
        self,
        scenes: list[ScriptScene],
        sequences: list[ScriptSequence],
        char_freq: list[tuple[str, int]],
    ) -> dict[str, object]:
        return {
            "total_scenes": len(scenes),
            "total_sequences": len(sequences),
            "character_frequency": dict(char_freq[:20]),
            "unique_locations": sorted(
                {s.location for s in scenes if s.location}
            ),
            "emotional_tone_distribution": dict(
                Counter(
                    s.emotional_tone for s in scenes if s.emotional_tone
                ).most_common()
            ),
            "conflict_scene_count": sum(
                1 for s in scenes if s.conflict
            ),
            "int_ext_counts": dict(
                Counter(
                    s.int_ext for s in scenes if s.int_ext
                ).most_common()
            ),
        }


script_synopsis_service = ScriptSynopsisService()
