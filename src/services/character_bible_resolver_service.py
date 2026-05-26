from __future__ import annotations

from typing import Any

from schemas.character_bible_schema import (
    ApprovedReferenceAsset,
    CharacterBibleEntry,
    CharacterBibleResolveRequest,
    CharacterBibleResolveResult,
    CharacterLookVariant,
)
from schemas.director_notes_schema import DirectorNotesResolveResult


class CharacterBibleResolver:
    def resolve_character_references_for_shot(
        self,
        bible_entries: list[CharacterBibleEntry],
        shot_number: int,
        sequence_id: str | None = None,
        character_ids_in_shot: list[str] | None = None,
        director_notes_result: DirectorNotesResolveResult | None = None,
    ) -> list[CharacterBibleResolveResult]:
        ids = character_ids_in_shot or [e.character_id for e in bible_entries]

        if not ids:
            return []

        results: list[CharacterBibleResolveResult] = []

        for character_id in ids:
            entry = self._find_entry(bible_entries, character_id)
            if entry is None:
                results.append(self._unresolved_result(character_id))
                continue

            request = CharacterBibleResolveRequest(
                project_id=entry.project_id,
                character_id=character_id,
                scene_id=sequence_id,
            )
            result = self._resolve_single(entry, request, director_notes_result)
            results.append(result)

        return results

    def resolve_character_references_for_sequence(
        self,
        bible_entries: list[CharacterBibleEntry],
        sequence_id: str,
        character_ids_in_sequence: list[str] | None = None,
    ) -> list[CharacterBibleResolveResult]:
        ids = character_ids_in_sequence or [e.character_id for e in bible_entries]

        if not ids:
            return []

        results: list[CharacterBibleResolveResult] = []

        for character_id in ids:
            entry = self._find_entry(bible_entries, character_id)
            if entry is None:
                results.append(self._unresolved_result(character_id))
                continue

            request = CharacterBibleResolveRequest(
                project_id=entry.project_id,
                character_id=character_id,
                scene_id=sequence_id,
            )
            result = self._resolve_single(entry, request)
            results.append(result)

        return results

    def select_look_variant(
        self,
        entry: CharacterBibleEntry,
        request: CharacterBibleResolveRequest,
    ) -> CharacterLookVariant | None:
        if not entry.look_variants:
            return None

        if request.look_id:
            for v in entry.look_variants:
                if v.look_id == request.look_id:
                    return v

        if request.narrative_phase:
            for v in entry.look_variants:
                if v.narrative_phase == request.narrative_phase:
                    return v

        if request.scene_id:
            for v in entry.look_variants:
                if request.scene_id in v.scene_ids:
                    return v

        if entry.default_look_id:
            for v in entry.look_variants:
                if v.look_id == entry.default_look_id:
                    return v

        if entry.look_variants:
            return entry.look_variants[0]

        return None

    def select_approved_reference(
        self,
        entry: CharacterBibleEntry,
        look: CharacterLookVariant | None,
    ) -> tuple[ApprovedReferenceAsset | None, list[ApprovedReferenceAsset]]:
        candidates: list[ApprovedReferenceAsset] = []

        if look and look.approved_references:
            candidates = list(look.approved_references)
        elif entry.approved_references:
            candidates = list(entry.approved_references)

        if not candidates and entry.approved_reference_asset_id:
            candidates = [
                a for a in entry.approved_references
                if a.asset_id == entry.approved_reference_asset_id
            ]

        primary: ApprovedReferenceAsset | None = None
        secondary: list[ApprovedReferenceAsset] = []

        for ref in candidates:
            if ref.is_primary and primary is None:
                primary = ref
            else:
                secondary.append(ref)

        if primary is None and candidates:
            candidates_sorted = sorted(candidates, key=lambda x: x.sort_order)
            primary = candidates_sorted[0]
            secondary = candidates_sorted[1:]

        return primary, secondary

    def build_character_lock_block(
        self,
        entry: CharacterBibleEntry,
        look: CharacterLookVariant | None,
        primary: ApprovedReferenceAsset | None,
        secondary: list[ApprovedReferenceAsset],
    ) -> str | None:
        parts: list[str] = [f"Personaje: {entry.character_name}"]

        if primary:
            if primary.asset_api_url:
                parts.append(f"referencia_principal: {primary.asset_api_url}")
            if primary.reference_id:
                parts.append(f"ref_id: {primary.reference_id}")
            if primary.description:
                parts.append(f"descripción: {primary.description}")

        if look:
            if look.wardrobe_notes:
                parts.append(f"vestuario: {look.wardrobe_notes}")
            if look.hair_makeup_notes:
                parts.append(f"pelo_maquillaje: {look.hair_makeup_notes}")
        else:
            if entry.wardrobe_notes:
                parts.append(f"vestuario: {entry.wardrobe_notes}")
            if entry.hair_makeup_notes:
                parts.append(f"pelo_maquillaje: {entry.hair_makeup_notes}")

        if look and look.key_props:
            parts.append(f"props_clave: {'; '.join(look.key_props)}")
        elif entry.key_props:
            parts.append(f"props_clave: {'; '.join(entry.key_props)}")

        if secondary:
            sec_ids = [s.reference_id or s.asset_id for s in secondary if s.reference_id or s.asset_id]
            if sec_ids:
                parts.append(f"referencias_secundarias: {'; '.join(sec_ids)}")

        if primary and primary.asset_type:
            parts.append(f"tipo_referencia: {primary.asset_type.value}")

        return " | ".join(parts) if parts else None

    def build_negative_constraints(
        self,
        entry: CharacterBibleEntry,
        look: CharacterLookVariant | None,
    ) -> str | None:
        constraints: list[str] = []

        if look and look.negative_constraints:
            constraints.extend(look.negative_constraints)
        if entry.negative_constraints:
            constraints.extend(entry.negative_constraints)

        if not constraints:
            return None

        prefixed = [f"Personaje {entry.character_name}: evitar {c}" for c in constraints]
        return " | ".join(prefixed)

    def build_trace_metadata(
        self,
        entry: CharacterBibleEntry,
        look: CharacterLookVariant | None,
        primary: ApprovedReferenceAsset | None,
        secondary: list[ApprovedReferenceAsset],
        unresolved_props: list[str],
        confidence: float,
        director_notes_override: bool = False,
        overridden_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        trace: dict[str, Any] = {
            "character_id": entry.character_id,
            "character_name": entry.character_name,
            "project_id": entry.project_id,
            "bible_version": entry.version,
            "approved_reference_asset_ids": [],
            "look_variant_applied": look.look_id if look else None,
            "look_variant_name": look.look_name if look else None,
            "confidence": confidence,
            "unresolved_props": unresolved_props,
            "director_notes_override_applied": director_notes_override,
        }

        asset_ids: list[str] = []
        if primary and primary.asset_id:
            asset_ids.append(primary.asset_id)
        for ref in secondary:
            if ref.asset_id:
                asset_ids.append(ref.asset_id)
        trace["approved_reference_asset_ids"] = asset_ids

        if director_notes_override and overridden_fields:
            trace["director_notes_overridden_fields"] = overridden_fields

        return trace

    def _resolve_single(
        self,
        entry: CharacterBibleEntry,
        request: CharacterBibleResolveRequest,
        director_notes_result: DirectorNotesResolveResult | None = None,
    ) -> CharacterBibleResolveResult:
        if not entry:
            return self._unresolved_result(request.character_id)

        look = self.select_look_variant(entry, request)
        primary, secondary = self.select_approved_reference(entry, look)

        overridden_fields: list[str] = []
        director_notes_override = False
        effective_character_lock: str | None = None
        effective_negative_block: str | None = None
        effective_continuity_block: str | None = None

        bible_lock = self.build_character_lock_block(entry, look, primary, secondary)
        bible_negative = self.build_negative_constraints(entry, look)
        bible_continuity = self._build_continuity_block(entry, look)

        if director_notes_result and director_notes_result.prompt_blocks:
            pb = director_notes_result.prompt_blocks

            if pb.character_lock_block:
                director_notes_override = True
                overridden_fields.append("character_lock_block")
                effective_character_lock = pb.character_lock_block
            else:
                effective_character_lock = bible_lock

            if pb.prompt_negative_constraints:
                director_notes_override = True
                overridden_fields.append("negative_constraints")
                dn_negatives = "; ".join(pb.prompt_negative_constraints)
                effective_negative_block = (
                    f"{bible_negative} | Director Notes: {dn_negatives}"
                    if bible_negative
                    else f"Director Notes: {dn_negatives}"
                )
            else:
                effective_negative_block = bible_negative

            if pb.continuity_prompt_block:
                director_notes_override = True
                overridden_fields.append("continuity_block")
                effective_continuity_block = pb.continuity_prompt_block
            else:
                effective_continuity_block = bible_continuity
        else:
            effective_character_lock = bible_lock
            effective_negative_block = bible_negative
            effective_continuity_block = bible_continuity

        unresolved = self._find_unresolved_props(entry, look)
        confidence = self._compute_confidence(entry, look, primary)

        character_reference_ids = [
            r.reference_id or r.asset_id
            for r in ([primary] + secondary)
            if r and (r.reference_id or r.asset_id)
        ]

        trace = self.build_trace_metadata(
            entry, look, primary, secondary, unresolved,
            confidence, director_notes_override, overridden_fields,
        )
        trace["character_reference_ids_used"] = character_reference_ids
        trace["character_lock_applied"] = (
            "director_notes" if director_notes_override and overridden_fields
            else "character_bible"
        )

        return CharacterBibleResolveResult(
            project_id=entry.project_id,
            character_id=entry.character_id,
            character_name=entry.character_name,
            resolved_look=look,
            primary_reference=primary,
            secondary_references=secondary,
            prompt_lock_block=effective_character_lock,
            prompt_negative_block=effective_negative_block,
            continuity_block=effective_continuity_block,
            applied_reference_ids=character_reference_ids,
            unresolved_props=unresolved,
            trace_metadata=trace,
        )

    def _unresolved_result(self, character_id: str) -> CharacterBibleResolveResult:
        return CharacterBibleResolveResult(
            project_id="",
            character_id=character_id,
            character_name="",
            prompt_lock_block=None,
            prompt_negative_block=None,
            continuity_block=None,
            applied_reference_ids=[],
            unresolved_props=[],
            trace_metadata={
                "character_id": character_id,
                "unresolved": True,
                "confidence": 0.0,
            },
        )

    def _find_entry(
        self,
        entries: list[CharacterBibleEntry],
        character_id: str,
    ) -> CharacterBibleEntry | None:
        for e in entries:
            if e.character_id == character_id:
                return e
        return None

    def _build_continuity_block(
        self,
        entry: CharacterBibleEntry,
        look: CharacterLookVariant | None,
    ) -> str | None:
        parts: list[str] = []

        if look and look.continuity_rules:
            parts.extend(look.continuity_rules)
        if entry.continuity_rules:
            parts.extend(entry.continuity_rules)

        if look and look.wardrobe_notes:
            parts.append(f"Vestuario consistente: {look.wardrobe_notes}")
        elif entry.wardrobe_notes:
            parts.append(f"Vestuario consistente: {entry.wardrobe_notes}")

        if look and look.hair_makeup_notes:
            parts.append(f"Pelo/maquillaje consistente: {look.hair_makeup_notes}")
        elif entry.hair_makeup_notes:
            parts.append(f"Pelo/maquillaje consistente: {entry.hair_makeup_notes}")

        return " | ".join(parts) if parts else None

    def _find_unresolved_props(
        self,
        entry: CharacterBibleEntry,
        look: CharacterLookVariant | None,
    ) -> list[str]:
        all_defined: list[str] = []
        if look and look.key_props:
            all_defined.extend(look.key_props)
        if entry.key_props:
            all_defined.extend(entry.key_props)

        all_resolved: list[str] = []
        if look and look.approved_references:
            for ref in look.approved_references:
                if ref.asset_type.value == "prop_reference" and ref.reference_id:
                    all_resolved.append(ref.reference_id)
        if entry.approved_references:
            for ref in entry.approved_references:
                if ref.asset_type.value == "prop_reference" and ref.reference_id:
                    all_resolved.append(ref.reference_id)

        unresolved = [p for p in all_defined if p not in all_resolved]
        return list(set(unresolved))

    def _compute_confidence(
        self,
        entry: CharacterBibleEntry,
        look: CharacterLookVariant | None,
        primary: ApprovedReferenceAsset | None,
    ) -> float:
        score = 0.0
        if primary:
            score += 0.4
        if look:
            score += 0.3
        if entry.approved_reference_asset_id:
            score += 0.2
        if entry.wardrobe_notes or (look and look.wardrobe_notes):
            score += 0.1
        return min(round(score, 2), 1.0)


character_bible_resolver = CharacterBibleResolver()
