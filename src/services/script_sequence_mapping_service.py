from __future__ import annotations

from collections import Counter

from schemas.cid_sequence_first_schema import ScriptSequenceMap, ScriptSequenceMapEntry
from schemas.cid_script_to_prompt_schema import ScriptScene

EMOTIONAL_GOAL_MAP: dict[str, str] = {
    "tension": "build_suspense_and_anticipation",
    "urgency": "create_immediate_pressure",
    "calm": "establish_emotional_grounding",
    "dialogue_tension": "develop_interpersonal_conflict",
    "focused_professional": "maintain_steady_progression",
}

DRAMATIC_FUNCTION_KEY_MOMENTS: set[str] = {
    "exposition",
    "climax",
    "resolution",
    "conflict_escalation",
    "rising_tension",
    "turning_point",
}


class ScriptSequenceMappingService:
    SEQUENCE_CHUNK_SIZE = 3
    MAX_SEQUENCE_SCENES = 5
    STRONG_TRANSITION_MARKERS = (
        "CORTE A",
        "FUNDIDO",
        "MONTAJE",
        "DÍAS DESPUÉS",
        "DIAS DESPUES",
        "SEMANAS DESPUÉS",
        "SEMANAS DESPUES",
        "MESES DESPUÉS",
        "MESES DESPUES",
    )

    def build_sequence_map(
        self,
        scenes: list[ScriptScene],
        script_text: str | None = None,
    ) -> ScriptSequenceMap:
        sequence_groups = self._group_into_sequences(scenes)
        total = len(sequence_groups)

        entries: list[ScriptSequenceMapEntry] = []
        for i, group in enumerate(sequence_groups):
            entry = self._build_entry(group, i + 1, total)
            entries.append(entry)

        scored = [(e, self._score_for_storyboard(e)) for e in entries]
        scored.sort(key=lambda x: x[1], reverse=True)
        priority = [e.sequence_id for e, _ in scored]

        return ScriptSequenceMap(
            sequences=entries,
            total_sequences=total,
            recommended_priority_order=priority,
        )

    def _group_into_sequences(
        self, scenes: list[ScriptScene]
    ) -> list[list[ScriptScene]]:
        if not scenes:
            return []
        groups: list[list[ScriptScene]] = []
        current: list[ScriptScene] = []
        prev: ScriptScene | None = None
        for scene in scenes:
            if not current:
                current = [scene]
                prev = scene
                continue
            if self._starts_new_sequence(prev, scene, current):
                groups.append(current)
                current = [scene]
            else:
                current.append(scene)
            prev = scene
        if current:
            groups.append(current)
        return groups

    def _starts_new_sequence(
        self,
        previous: ScriptScene | None,
        current: ScriptScene,
        current_group: list[ScriptScene],
    ) -> bool:
        if previous is None:
            return False
        if len(current_group) >= self.MAX_SEQUENCE_SCENES:
            return True

        heading = (current.heading or "").upper()
        raw = (current.raw_text or "").upper()
        if any(marker in heading or marker in raw for marker in self.STRONG_TRANSITION_MARKERS):
            return True

        prev_loc = (previous.location or "").strip().lower()
        curr_loc = (current.location or "").strip().lower()
        prev_time = (previous.time_of_day or "").strip().lower()
        curr_time = (current.time_of_day or "").strip().lower()

        location_changed = bool(prev_loc and curr_loc and prev_loc != curr_loc)
        time_jump = bool(prev_time and curr_time and prev_time != curr_time and curr_time not in {"continuous", "continuo"})

        prev_goal = (previous.dramatic_objective or "").strip().lower()
        curr_goal = (current.dramatic_objective or "").strip().lower()
        objective_changed = bool(prev_goal and curr_goal and prev_goal != curr_goal)

        prev_tone = (previous.emotional_tone or "").strip().lower()
        curr_tone = (current.emotional_tone or "").strip().lower()
        tone_changed = bool(prev_tone and curr_tone and prev_tone != curr_tone)

        strong_narrative_break = (location_changed and objective_changed) or (time_jump and objective_changed)
        if strong_narrative_break:
            return True
        if location_changed and tone_changed and len(current_group) >= 2:
            return True
        return False

    def _build_entry(
        self,
        group: list[ScriptScene],
        seq_number: int,
        total_sequences: int,
    ) -> ScriptSequenceMapEntry:
        first = group[0]
        sequence_id = f"seq_{seq_number:03d}"
        scene_numbers = [int(s.scene_number) for s in group]
        source_scene_start = min(scene_numbers) if scene_numbers else 0
        source_scene_end = max(scene_numbers) if scene_numbers else 0
        source_sequence_label = f"Secuencia {seq_number}"
        display_name = f"Secuencia {seq_number} — Escenas {source_scene_start}-{source_scene_end}"
        location_groups = sorted({(s.location or "").strip().lower() for s in group if (s.location or "").strip()})
        continuity_groups = sorted({f"{(s.location or '').strip().lower()}__{(s.time_of_day or '').strip().lower()}" for s in group if (s.location or '').strip()})
        conflict_summary = ", ".join(sorted({(s.conflict or "").strip().lower() for s in group if (s.conflict or "").strip()}))
        causal_links: list[str] = []
        for idx in range(len(group) - 1):
            causal_links.append(f"scene_{group[idx].scene_number}->scene_{group[idx + 1].scene_number}")

        raw_texts = [s.raw_text for s in group if s.raw_text]
        script_excerpt = "\n\n".join(raw_texts)

        summary_parts: list[str] = []
        for s in group:
            label = s.heading
            if s.action_summary:
                label = f"{label}: {s.action_summary[:120]}"
            summary_parts.append(label)
        summary = "; ".join(summary_parts)

        all_chars: list[str] = []
        seen_chars: set[str] = set()
        for s in group:
            for c in s.characters:
                if c not in seen_chars:
                    seen_chars.add(c)
                    all_chars.append(c)

        location = first.location or ""
        time_of_day = first.time_of_day or ""

        titles = [
            s.location or s.heading.split("--")[0].strip()
            for s in group
            if s.location
        ]
        title = titles[0] if titles else (first.location or f"Sequence {seq_number}")

        dramatic_function = self._infer_dramatic_function(
            group, seq_number, total_sequences
        )
        emotional_goal = self._infer_emotional_goal(group)
        visual_opportunity = self._rate_visual_opportunity(group)
        production_complexity = self._rate_production_complexity(group)

        recommended = dramatic_function in DRAMATIC_FUNCTION_KEY_MOMENTS

        suggested_shot_count = self._suggest_shot_count(group)

        technical_notes = self._build_technical_notes(group)

        return ScriptSequenceMapEntry(
            sequence_id=sequence_id,
            sequence_number=seq_number,
            title=title,
            script_excerpt=script_excerpt,
            summary=summary,
            location=location,
            time_of_day=time_of_day,
            characters=all_chars,
            dramatic_function=dramatic_function,
            emotional_goal=emotional_goal,
            visual_opportunity=visual_opportunity,
            production_complexity=production_complexity,
            recommended_for_storyboard=recommended,
            suggested_shot_count=suggested_shot_count,
            technical_notes=technical_notes,
            sequence_title=title,
            dramatic_purpose=dramatic_function,
            continuity_group=self._continuity_group(group),
            source_sequence_label=source_sequence_label,
            source_scene_start=source_scene_start,
            source_scene_end=source_scene_end,
            scene_numbers=scene_numbers,
            scene_count=len(scene_numbers),
            display_name=display_name,
            location_groups=location_groups,
            continuity_groups=continuity_groups,
            conflict_summary=conflict_summary or None,
            causal_links=causal_links,
        )

    def _continuity_group(self, group: list[ScriptScene]) -> str:
        first = group[0]
        loc = (first.location or "unknown").strip().lower().replace(" ", "_")
        tod = (first.time_of_day or "any").strip().lower().replace(" ", "_")
        return f"{loc}__{tod}"

    def _infer_dramatic_function(
        self,
        group: list[ScriptScene],
        seq_number: int,
        total_sequences: int,
    ) -> str:
        if total_sequences <= 1:
            return "single_sequence_full_script"

        has_conflict = any(s.conflict for s in group)
        has_emotional_shift = self._has_emotional_shift(group)
        has_location_shift = self._has_location_shift(group)

        if seq_number == 1:
            if has_conflict:
                return "cold_open_conflict"
            return "exposition"

        if seq_number == total_sequences:
            if has_conflict:
                return "resolution"
            return "climax"

        mid_point = total_sequences // 2
        if seq_number == mid_point:
            return "turning_point"

        if has_conflict and has_emotional_shift:
            return "rising_tension"
        if has_conflict:
            return "conflict_escalation"
        if has_location_shift:
            return "scene_transition"
        return "narrative_development"

    def _has_emotional_shift(self, group: list[ScriptScene]) -> bool:
        tones = [s.emotional_tone for s in group if s.emotional_tone]
        return len(set(tones)) > 1

    def _has_location_shift(self, group: list[ScriptScene]) -> bool:
        locations = [s.location for s in group if s.location]
        return len(set(locations)) > 1

    def _infer_emotional_goal(self, group: list[ScriptScene]) -> str:
        tones = [s.emotional_tone for s in group if s.emotional_tone]
        if not tones:
            return "establish_scene_mood"
        dominant = Counter(tones).most_common(1)[0][0]
        return EMOTIONAL_GOAL_MAP.get(dominant, f"sustain_{dominant}")

    def _rate_visual_opportunity(self, group: list[ScriptScene]) -> str:
        score = 0
        if self._has_location_shift(group):
            score += 2
        if self._has_emotional_shift(group):
            score += 2
        if any(s.time_of_day for s in group):
            score += 1
        all_props: set[str] = set()
        for s in group:
            all_props.update(s.props)
        if any(p not in {"storyboard", "documentos"} for p in all_props):
            score += 1
        if any(s.int_ext and "EXT" in s.int_ext for s in group):
            score += 1
        dialogue_lines = sum(
            1 for s in group if s.dialogue_summary
        )
        if dialogue_lines <= len(group) // 2:
            score += 1

        if score >= 4:
            return "high"
        if score >= 2:
            return "medium"
        return "low"

    def _rate_production_complexity(self, group: list[ScriptScene]) -> str:
        score = 0
        all_chars: set[str] = set()
        all_locs: set[str] = set()
        all_props: set[str] = set()
        for s in group:
            all_chars.update(s.characters)
            if s.location:
                all_locs.add(s.location)
            all_props.update(s.props)

        if len(all_chars) >= 4:
            score += 2
        elif len(all_chars) >= 2:
            score += 1

        if len(all_locs) >= 2:
            score += 2
        elif len(all_locs) == 1:
            score += 1

        if len(all_props) >= 3:
            score += 2
        elif len(all_props) >= 1:
            score += 1

        ext_count = sum(
            1 for s in group if s.int_ext and "EXT" in s.int_ext
        )
        if ext_count > 0:
            score += 1

        if score >= 5:
            return "high"
        if score >= 3:
            return "medium"
        return "low"

    def _suggest_shot_count(self, group: list[ScriptScene]) -> int:
        base = len(group) * 3
        locations: set[str] = {s.location for s in group if s.location}
        base += len(locations) - 1
        all_props: set[str] = set()
        for s in group:
            all_props.update(s.props)
        base += min(len(all_props), 3)
        all_chars: set[str] = set()
        for s in group:
            all_chars.update(s.characters)
        if len(all_chars) >= 3:
            base += 2
        return base

    def _build_technical_notes(self, group: list[ScriptScene]) -> list[str]:
        notes: list[str] = []
        locations: set[str] = {s.location for s in group if s.location}
        if len(locations) > 1:
            notes.append(f"location_changes:{len(locations)}")

        int_count = sum(1 for s in group if s.int_ext and "INT" in s.int_ext)
        ext_count = sum(1 for s in group if s.int_ext and "EXT" in s.int_ext)
        if int_count and ext_count:
            notes.append("int_ext_mixed")

        all_chars: set[str] = set()
        for s in group:
            all_chars.update(s.characters)
        if len(all_chars) >= 3:
            notes.append(f"ensemble_cast:{len(all_chars)}")

        all_props: set[str] = set()
        for s in group:
            all_props.update(s.props)
        if all_props:
            notes.append(f"props_required:{len(all_props)}")

        if self._has_emotional_shift(group):
            notes.append("emotional_shift_within_sequence")

        times = {s.time_of_day for s in group if s.time_of_day}
        if len(times) > 1:
            notes.append("time_transition")

        conflict_count = sum(1 for s in group if s.conflict)
        if conflict_count:
            notes.append(f"conflict_scenes:{conflict_count}")

        return notes

    def _score_for_storyboard(self, entry: ScriptSequenceMapEntry) -> float:
        score = 0.0
        if entry.recommended_for_storyboard:
            score += 5.0
        if entry.visual_opportunity == "high":
            score += 3.0
        elif entry.visual_opportunity == "medium":
            score += 1.0
        if entry.suggested_shot_count > 6:
            score += 2.0
        elif entry.suggested_shot_count > 3:
            score += 1.0
        return score


script_sequence_mapping_service = ScriptSequenceMappingService()
