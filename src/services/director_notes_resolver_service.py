from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from schemas.director_notes_schema import (
    CharacterDirectorNotes,
    DirectorNoteOverride,
    DirectorNoteOverrideLevel,
    DirectorNotesBundle,
    DirectorNotesResolveRequest,
    DirectorNotesResolveResult,
    LocationDirectorNotes,
    ProjectDirectorNotes,
    PromptBlocks,
    PropDirectorNotes,
    SequenceDirectorNotes,
    ShotDirectorNotes,
    VoiceDirectorNoteDraft,
)

_PRIORITY_ORDER: dict[DirectorNoteOverrideLevel, int] = {
    DirectorNoteOverrideLevel.OVERRIDE_MANUAL: 0,
    DirectorNoteOverrideLevel.SEQUENCE_SHOT: 1,
    DirectorNoteOverrideLevel.VISUAL_BIBLE: 2,
    DirectorNoteOverrideLevel.SCRIPT_ANALYSIS: 3,
    DirectorNoteOverrideLevel.AUTOMATIC_HEURISTIC: 4,
}


class DirectorNotesResolver:
    def resolve_notes_for_project(
        self,
        project_id: str,
        bundle: DirectorNotesBundle,
    ) -> DirectorNotesResolveResult:
        if bundle.project and bundle.project.project_id != project_id:
            bundle.project = None

        effective_project = bundle.project
        overrides: list[DirectorNoteOverride] = []
        prompt_additions: list[str] = []
        prompt_negatives: list[str] = []

        if effective_project:
            prompt_additions = self._project_prompt_additions(effective_project)
            prompt_negatives = self._project_prompt_negatives(effective_project)
            for override in bundle.overrides:
                overrides.append(override)

        pending_voice = self._pending_voice_drafts(bundle)

        prompt_blocks = PromptBlocks(
            prompt_positive_additions=prompt_additions,
            prompt_negative_constraints=prompt_negatives,
        )

        trace = self.build_trace_metadata(bundle, project_id=project_id)
        refs = bundle.director_note_refs

        return DirectorNotesResolveResult(
            project_id=project_id,
            prompt_blocks=prompt_blocks,
            applied_overrides=overrides,
            trace_metadata=trace,
            voice_drafts_pending_review=pending_voice,
            director_note_refs=refs,
            cinematic_grammar_overrides={},
        )

    def resolve_notes_for_sequence(
        self,
        project_id: str,
        sequence_id: str,
        bundle: DirectorNotesBundle,
    ) -> DirectorNotesResolveResult:
        project_result = self.resolve_notes_for_project(project_id, bundle)
        sequence_notes = [s for s in bundle.sequences if s.sequence_id == sequence_id]

        merged = self.merge_notes_by_priority(
            project_notes=bundle.project,
            sequence_notes=sequence_notes[0] if sequence_notes else None,
        )

        prompt_blocks = self._build_prompt_blocks_from_merged(
            merged, bundle, sequence_id=sequence_id
        )
        pending_voice = self._pending_voice_drafts(bundle)

        cg_overrides: dict[str, Any] = {}
        if sequence_notes:
            sn = sequence_notes[0]
            if sn.tone:
                cg_overrides["tone"] = sn.tone
            if sn.rhythm:
                cg_overrides["rhythm"] = sn.rhythm
            if sn.emotional_goal:
                cg_overrides["emotional_goal"] = sn.emotional_goal

        trace = self.build_trace_metadata(bundle, project_id=project_id, sequence_id=sequence_id)

        return DirectorNotesResolveResult(
            project_id=project_id,
            sequence_id=sequence_id,
            prompt_blocks=prompt_blocks,
            applied_overrides=bundle.overrides,
            trace_metadata=trace,
            voice_drafts_pending_review=pending_voice,
            director_note_refs=bundle.director_note_refs,
            cinematic_grammar_overrides=cg_overrides,
        )

    def resolve_notes_for_shot(
        self,
        project_id: str,
        sequence_id: str | None,
        shot_number: int | None,
        bundle: DirectorNotesBundle,
    ) -> DirectorNotesResolveResult:
        sequence_result = self.resolve_notes_for_sequence(project_id, sequence_id or "", bundle)
        shot_notes = [
            s
            for s in bundle.shots
            if (shot_number is None or s.shot_number == shot_number)
            and (sequence_id is None or s.sequence_id == sequence_id)
        ]

        merged = self.merge_notes_by_priority(
            project_notes=bundle.project,
            sequence_notes=self._find_sequence(bundle, sequence_id),
            shot_notes=shot_notes[0] if shot_notes else None,
        )

        prompt_blocks = self._build_prompt_blocks_from_merged(
            merged, bundle, sequence_id=sequence_id, shot_number=shot_number
        )
        pending_voice = self._pending_voice_drafts(bundle)

        cg_overrides: dict[str, Any] = {}
        if shot_notes:
            sn = shot_notes[0]
            if sn.coverage_pattern_override:
                cg_overrides["coverage_pattern"] = sn.coverage_pattern_override
            if sn.shot_type_override:
                cg_overrides["shot_type"] = sn.shot_type_override
            if sn.priority_override:
                cg_overrides["priority"] = sn.priority_override
            if sn.reference_mode_override:
                cg_overrides["reference_mode"] = sn.reference_mode_override

        visual_raccord = self._build_visual_raccord_block(merged, bundle)
        if visual_raccord:
            prompt_blocks.visual_raccord_block = visual_raccord

        trace = self.build_trace_metadata(
            bundle, project_id=project_id, sequence_id=sequence_id, shot_number=shot_number
        )

        return DirectorNotesResolveResult(
            project_id=project_id,
            sequence_id=sequence_id,
            shot_number=shot_number,
            prompt_blocks=prompt_blocks,
            applied_overrides=bundle.overrides,
            trace_metadata=trace,
            voice_drafts_pending_review=pending_voice,
            director_note_refs=bundle.director_note_refs,
            cinematic_grammar_overrides=cg_overrides,
        )

    def merge_notes_by_priority(
        self,
        project_notes: ProjectDirectorNotes | None = None,
        sequence_notes: SequenceDirectorNotes | None = None,
        shot_notes: ShotDirectorNotes | None = None,
        character_notes: list[CharacterDirectorNotes] | None = None,
        location_notes: list[LocationDirectorNotes] | None = None,
        prop_notes: list[PropDirectorNotes] | None = None,
    ) -> dict[str, Any]:
        candidates: list[tuple[int, str, Any]] = []

        if project_notes:
            priority = _PRIORITY_ORDER.get(project_notes.override_priority, 4)
            candidates.append((priority, "project", project_notes))

        if sequence_notes:
            priority = _PRIORITY_ORDER.get(sequence_notes.override_priority, 4)
            candidates.append((priority, "sequence", sequence_notes))

        if shot_notes:
            priority = _PRIORITY_ORDER.get(shot_notes.override_priority, 4)
            candidates.append((priority, "shot", shot_notes))

        if character_notes:
            for cn in character_notes:
                priority = _PRIORITY_ORDER.get(cn.override_priority, 4)
                candidates.append((priority, f"character:{cn.character_id}", cn))

        if location_notes:
            for ln in location_notes:
                priority = _PRIORITY_ORDER.get(ln.override_priority, 4)
                candidates.append((priority, f"location:{ln.location_id}", ln))

        if prop_notes:
            for pn in prop_notes:
                priority = _PRIORITY_ORDER.get(pn.override_priority, 4)
                candidates.append((priority, f"prop:{pn.prop_id}", pn))

        candidates.sort(key=lambda x: x[0], reverse=True)
        merged: dict[str, Any] = {"sources": [], "tone": None, "emotional_goal": None}
        for priority, source_key, note in candidates:
            merged["sources"].append(source_key)
            self._deep_merge(merged, self._note_to_dict(note))
        return merged

    def build_prompt_blocks(
        self,
        bundle: DirectorNotesBundle,
        sequence_id: str | None = None,
        shot_number: int | None = None,
    ) -> PromptBlocks:
        merged = self.merge_notes_by_priority(
            project_notes=bundle.project,
            sequence_notes=self._find_sequence(bundle, sequence_id),
            shot_notes=self._find_shot(bundle, sequence_id, shot_number),
            character_notes=bundle.characters,
            location_notes=bundle.locations,
            prop_notes=bundle.props,
        )
        return self._build_prompt_blocks_from_merged(
            merged, bundle, sequence_id=sequence_id, shot_number=shot_number
        )

    def build_trace_metadata(
        self,
        bundle: DirectorNotesBundle,
        project_id: str | None = None,
        sequence_id: str | None = None,
        shot_number: int | None = None,
    ) -> dict[str, Any]:
        trace: dict[str, Any] = {
            "project_id": project_id,
            "sequence_id": sequence_id,
            "shot_number": shot_number,
            "applied_sources": [],
            "override_count": len(bundle.overrides),
            "voice_drafts_pending": len(self._pending_voice_drafts(bundle)),
            "character_notes_count": len(bundle.characters),
            "location_notes_count": len(bundle.locations),
            "prop_notes_count": len(bundle.props),
        }

        applied: list[dict[str, Any]] = []
        if bundle.project:
            applied.append({
                "level": "project",
                "source": bundle.project.source.value,
                "priority": bundle.project.override_priority.value,
            })
        for seq in bundle.sequences:
            if sequence_id and seq.sequence_id == sequence_id:
                applied.append({
                    "level": "sequence",
                    "id": seq.sequence_id,
                    "source": seq.source.value,
                    "priority": seq.override_priority.value,
                })
        for shot in bundle.shots:
            if shot_number is not None and shot.shot_number == shot_number:
                applied.append({
                    "level": "shot",
                    "number": shot.shot_number,
                    "source": shot.source.value,
                    "priority": shot.override_priority.value,
                })
        for cn in bundle.characters:
            applied.append({
                "level": "character",
                "id": cn.character_id,
                "source": cn.source.value,
                "priority": cn.override_priority.value,
            })
        for ln in bundle.locations:
            applied.append({
                "level": "location",
                "id": ln.location_id,
                "source": ln.source.value,
                "priority": ln.override_priority.value,
            })
        for pn in bundle.props:
            applied.append({
                "level": "prop",
                "id": pn.prop_id,
                "source": pn.source.value,
                "priority": pn.override_priority.value,
            })

        applied.sort(key=lambda x: _PRIORITY_ORDER.get(
            DirectorNoteOverrideLevel(x["priority"]), 999
        ), reverse=True)
        trace["applied_sources"] = applied
        trace["director_note_refs"] = bundle.director_note_refs
        return trace

    def _build_prompt_blocks_from_merged(
        self,
        merged: dict[str, Any],
        bundle: DirectorNotesBundle,
        sequence_id: str | None = None,
        shot_number: int | None = None,
    ) -> PromptBlocks:
        additions: list[str] = []
        negatives: list[str] = []

        if merged.get("tone"):
            additions.append(f"Tono: {merged['tone']}")
        if merged.get("emotional_goal"):
            additions.append(f"Objetivo emocional: {merged['emotional_goal']}")
        if merged.get("visual_metaphor"):
            additions.append(f"Metáfora visual: {merged['visual_metaphor']}")
        if merged.get("rhythm"):
            additions.append(f"Ritmo: {merged['rhythm']}")
        if merged.get("director_intent"):
            additions.append(f"Intención del director: {merged['director_intent']}")
        if merged.get("montage_intent"):
            additions.append(f"Intención de montaje: {merged['montage_intent']}")
        if merged.get("global_tone"):
            additions.append(f"Tono global: {merged['global_tone']}")
        if merged.get("global_visual_style"):
            additions.append(f"Estilo visual global: {merged['global_visual_style']}")
        if merged.get("global_lighting"):
            additions.append(f"Iluminación global: {merged['global_lighting']}")
        if merged.get("global_atmosphere"):
            additions.append(f"Atmósfera global: {merged['global_atmosphere']}")

        character_lock = self._build_character_lock(bundle.characters)
        location_lock = self._build_location_lock(bundle.locations)
        prop_lock = self._build_prop_lock(bundle.props)
        continuity = self._build_continuity_block(merged, bundle)
        visual_raccord = self._build_visual_raccord_block(merged, bundle)

        for cn in bundle.characters:
            if cn.forbidden_changes:
                for fc in cn.forbidden_changes:
                    negatives.append(f"Personaje {cn.character_name}: evitar {fc}")

        for ln in bundle.locations:
            if ln.forbidden_elements:
                for fe in ln.forbidden_elements:
                    negatives.append(f"Localización: evitar {fe}")

        for pn in bundle.props:
            if pn.forbidden_changes:
                for fc in pn.forbidden_changes:
                    negatives.append(f"Prop {pn.prop_name}: evitar {fc}")

        return PromptBlocks(
            prompt_positive_additions=additions,
            prompt_negative_constraints=negatives,
            continuity_prompt_block=continuity,
            character_lock_block=character_lock,
            location_lock_block=location_lock,
            prop_lock_block=prop_lock,
            visual_raccord_block=visual_raccord,
        )

    def _build_character_lock(
        self, characters: list[CharacterDirectorNotes]
    ) -> str | None:
        if not characters:
            return None
        parts: list[str] = []
        for c in characters:
            details: list[str] = [f"Personaje: {c.character_name}"]
            if c.face_description:
                details.append(f"rostro: {c.face_description}")
            if c.hair:
                details.append(f"cabello: {c.hair}")
            if c.wardrobe:
                details.append(f"vestuario: {c.wardrobe}")
            if c.body_language:
                details.append(f"lenguaje corporal: {c.body_language}")
            if c.emotional_state:
                details.append(f"estado emocional: {c.emotional_state}")
            if c.age_range:
                details.append(f"edad: {c.age_range}")
            if c.visual_references:
                details.append(f"referencias visuales: {'; '.join(c.visual_references)}")
            if c.continuity_constraints:
                details.append(
                    f"restricciones de continuidad: {'; '.join(c.continuity_constraints)}"
                )
            parts.append(" | ".join(details))
        return " || ".join(parts)

    def _build_location_lock(
        self, locations: list[LocationDirectorNotes]
    ) -> str | None:
        if not locations:
            return None
        parts: list[str] = []
        for loc in locations:
            details: list[str] = [f"Localización: {loc.location_name}"]
            if loc.period:
                details.append(f"periodo: {loc.period}")
            if loc.architecture_style:
                details.append(f"arquitectura: {loc.architecture_style}")
            if loc.atmosphere:
                details.append(f"atmósfera: {loc.atmosphere}")
            if loc.lighting:
                details.append(f"iluminación: {loc.lighting}")
            if loc.color_palette:
                details.append(f"paleta de color: {', '.join(loc.color_palette)}")
            if loc.textures:
                details.append(f"texturas: {', '.join(loc.textures)}")
            if loc.spatial_layout:
                details.append(f"disposición espacial: {loc.spatial_layout}")
            if loc.recurring_elements:
                details.append(
                    f"elementos recurrentes: {', '.join(loc.recurring_elements)}"
                )
            if loc.continuity_constraints:
                details.append(
                    f"continuidad: {'; '.join(loc.continuity_constraints)}"
                )
            parts.append(" | ".join(details))
        return " || ".join(parts)

    def _build_prop_lock(
        self, props: list[PropDirectorNotes]
    ) -> str | None:
        if not props:
            return None
        parts: list[str] = []
        for p in props:
            details: list[str] = [f"Prop: {p.prop_name}"]
            if p.description:
                details.append(f"descripción: {p.description}")
            if p.placement:
                details.append(f"ubicación: {p.placement}")
            if p.dramatic_importance:
                details.append(f"importancia dramática: {p.dramatic_importance}")
            if p.continuity_rule:
                details.append(f"regla de continuidad: {p.continuity_rule}")
            if p.must_appear:
                details.append("DEBE APARECER")
            parts.append(" | ".join(details))
        return " || ".join(parts)

    def _build_continuity_block(
        self,
        merged: dict[str, Any],
        bundle: DirectorNotesBundle,
    ) -> str | None:
        parts: list[str] = []
        for cn in bundle.characters:
            if cn.continuity_constraints:
                parts.extend(cn.continuity_constraints)
        for ln in bundle.locations:
            if ln.continuity_constraints:
                parts.extend(ln.continuity_constraints)
        for pn in bundle.props:
            if pn.continuity_rule:
                parts.append(pn.continuity_rule)
        if merged.get("blocking_notes"):
            parts.append(f"Blocking: {merged['blocking_notes']}")
        return " | ".join(parts) if parts else None

    def _build_visual_raccord_block(
        self,
        merged: dict[str, Any],
        bundle: DirectorNotesBundle,
    ) -> str | None:
        parts: list[str] = []
        for cn in bundle.characters:
            if cn.wardrobe:
                parts.append(f"Vestuario consistente: {cn.wardrobe}")
            if cn.continuity_constraints:
                parts.extend(cn.continuity_constraints)
        for ln in bundle.locations:
            if ln.lighting:
                parts.append(f"Iluminación consistente: {ln.lighting}")
            if ln.atmosphere:
                parts.append(f"Atmósfera consistente: {ln.atmosphere}")
            if ln.color_palette:
                parts.append(f"Paleta de color consistente: {', '.join(ln.color_palette)}")
        for pn in bundle.props:
            if pn.must_appear:
                parts.append(f"Prop consistente: {pn.prop_name} — {pn.placement or 'según plano'}")
        return " | ".join(parts) if parts else None

    def _pending_voice_drafts(
        self, bundle: DirectorNotesBundle
    ) -> list[VoiceDirectorNoteDraft]:
        return [d for d in bundle.voice_drafts if not d.reviewed_by_user]

    def _find_sequence(
        self, bundle: DirectorNotesBundle, sequence_id: str | None
    ) -> SequenceDirectorNotes | None:
        if not sequence_id:
            return None
        matches = [s for s in bundle.sequences if s.sequence_id == sequence_id]
        return matches[0] if matches else None

    def _find_shot(
        self,
        bundle: DirectorNotesBundle,
        sequence_id: str | None,
        shot_number: int | None,
    ) -> ShotDirectorNotes | None:
        if shot_number is None:
            return None
        matches = [
            s
            for s in bundle.shots
            if s.shot_number == shot_number
            and (sequence_id is None or s.sequence_id == sequence_id)
        ]
        return matches[0] if matches else None

    def _project_prompt_additions(
        self, project: ProjectDirectorNotes
    ) -> list[str]:
        additions: list[str] = []
        if project.global_tone:
            additions.append(f"Tono global: {project.global_tone}")
        if project.global_visual_style:
            additions.append(f"Estilo visual global: {project.global_visual_style}")
        if project.global_lighting:
            additions.append(f"Iluminación global: {project.global_lighting}")
        if project.global_atmosphere:
            additions.append(f"Atmósfera global: {project.global_atmosphere}")
        if project.notes:
            additions.append(f"Notas: {project.notes}")
        return additions

    def _project_prompt_negatives(
        self, project: ProjectDirectorNotes
    ) -> list[str]:
        return []

    def _note_to_dict(self, note: Any) -> dict[str, Any]:
        if isinstance(note, ProjectDirectorNotes):
            return note.model_dump(exclude_none=True)
        if isinstance(note, SequenceDirectorNotes):
            return note.model_dump(exclude_none=True)
        if isinstance(note, ShotDirectorNotes):
            return note.model_dump(exclude_none=True)
        if isinstance(note, CharacterDirectorNotes):
            return note.model_dump(exclude_none=True)
        if isinstance(note, LocationDirectorNotes):
            return note.model_dump(exclude_none=True)
        if isinstance(note, PropDirectorNotes):
            return note.model_dump(exclude_none=True)
        return {}

    def _deep_merge(self, base: dict[str, Any], overlay: dict[str, Any]) -> None:
        for key, value in overlay.items():
            if key in ("source", "override_priority", "reviewed_by_user", "applied_at"):
                continue
            if key in ("blocking", "dramatic_intent") and isinstance(value, dict):
                if key not in base or base[key] is None:
                    base[key] = {}
                self._deep_merge(base[key], value)
            elif value is not None:
                base[key] = value


director_notes_resolver = DirectorNotesResolver()
