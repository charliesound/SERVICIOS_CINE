from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)

from schemas.director_notes_schema import (
    CharacterDirectorNotes,
    DirectorNoteOverride,
    DirectorNoteOverrideLevel,
    DirectorNoteSource,
    DirectorNotesBundle,
    LocationDirectorNotes,
    ProjectDirectorNotes,
    PropDirectorNotes,
    SequenceDirectorNotes,
    ShotDirectorNotes,
    VoiceDirectorNoteDraft,
)
from services.director_notes_resolver_service import director_notes_resolver


MARTA_CHARACTER = CharacterDirectorNotes(
    character_id="char_marta",
    character_name="Marta",
    age_range="30-35",
    face_description="Ovalada, ojos oscuros, expresión seria",
    hair="Castaño largo recogido",
    wardrobe="Chaqueta oscura, vaqueros, botas",
    body_language="Tensa, alerta, movimientos calculados",
    emotional_state="Asustada pero decidida",
    continuity_constraints=["Misma chaqueta en toda la escena", "Mismo peinado"],
    forbidden_changes=["No cambiar peinado", "No cambiar chaqueta"],
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)

MARTA_LOCATION = LocationDirectorNotes(
    location_id="loc_casa",
    location_name="Casa abandonada",
    period="contemporáneo",
    architecture_style="rural abandonada",
    atmosphere="silencioso, polvoriento, opresivo",
    lighting="Oscuridad total, solo linterna como luz motriz",
    color_palette=["negro", "marrón oscuro", "gris"],
    textures=["madera agrietada", "yeso descascarillado", "óxido"],
    spatial_layout="Pasillo estrecho con puerta al fondo",
    recurring_elements=["puerta al fondo del pasillo", "sombras danzantes"],
    forbidden_elements=["luz blanca fría", "mobiliario moderno"],
    continuity_constraints=["Misma disposición en todos los planos"],
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)

MARTA_FLASHLIGHT = PropDirectorNotes(
    prop_id="prop_linterna",
    prop_name="Linterna",
    description="Linterna metálica negra, haz potente",
    placement="mano derecha de Marta",
    dramatic_importance="alta — luz motriz de la escena",
    continuity_rule="Misma linterna en todos los planos",
    must_appear=True,
    forbidden_changes=["No cambiar tamaño", "No cambiar color del haz"],
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)

PROJECT_NOTES = ProjectDirectorNotes(
    project_id="proj_corto",
    project_title="Cortometraje suspense",
    global_tone="suspense",
    global_visual_style="noir contemporáneo",
    global_lighting="low_key",
    global_atmosphere="opresivo, claustrofóbico",
    notes="Mantener tensión constante durante toda la escena",
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)

SEQUENCE_NOTES = SequenceDirectorNotes(
    sequence_id="seq_entrada",
    sequence_title="Entrada a la casa",
    tone="suspense creciente",
    rhythm="lento, pausado",
    emotional_goal="Generar inquietud en el espectador",
    visual_metaphor="La oscuridad como amenaza latente",
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.SEQUENCE_SHOT,
    reviewed_by_user=True,
)

SHOT_NOTES = ShotDirectorNotes(
    shot_number=1,
    sequence_id="seq_entrada",
    notes="Primer plano de la entrada, cámara lenta",
    coverage_pattern_override="suspense_coverage",
    shot_type_override="extreme_long_shot",
    priority_override="must_have",
    reference_mode_override="filmic",
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.SEQUENCE_SHOT,
    reviewed_by_user=True,
)


def _bundle_with_marta() -> DirectorNotesBundle:
    return DirectorNotesBundle(
        project=PROJECT_NOTES,
        sequences=[SEQUENCE_NOTES],
        shots=[SHOT_NOTES],
        characters=[MARTA_CHARACTER],
        locations=[MARTA_LOCATION],
        props=[MARTA_FLASHLIGHT],
    )


class TestResolveProject:
    def test_resolve_empty_bundle(self) -> None:
        bundle = DirectorNotesBundle()
        result = director_notes_resolver.resolve_notes_for_project("proj_test", bundle)
        assert result.project_id == "proj_test"
        assert len(result.prompt_blocks.prompt_positive_additions) == 0

    def test_resolve_project_with_notes(self) -> None:
        bundle = _bundle_with_marta()
        result = director_notes_resolver.resolve_notes_for_project("proj_corto", bundle)
        additions = result.prompt_blocks.prompt_positive_additions
        assert any("Tono global: suspense" in a for a in additions)
        assert any("noir contemporáneo" in a for a in additions)
        assert any("low_key" in a for a in additions)

    def test_project_mismatch_ignores_project(self) -> None:
        bundle = _bundle_with_marta()
        result = director_notes_resolver.resolve_notes_for_project("other_proj", bundle)
        assert result.project_id == "other_proj"
        assert len(result.prompt_blocks.prompt_positive_additions) == 0


class TestResolveSequence:
    def test_resolve_sequence_merges_project_and_sequence(self) -> None:
        bundle = _bundle_with_marta()
        result = director_notes_resolver.resolve_notes_for_sequence(
            "proj_corto", "seq_entrada", bundle
        )
        assert result.sequence_id == "seq_entrada"
        additions = result.prompt_blocks.prompt_positive_additions
        assert any("Tono" in a for a in additions)
        assert any("suspense creciente" in a or "suspense" in a for a in additions)

    def test_sequence_cg_overrides(self) -> None:
        bundle = _bundle_with_marta()
        result = director_notes_resolver.resolve_notes_for_sequence(
            "proj_corto", "seq_entrada", bundle
        )
        assert result.cinematic_grammar_overrides.get("tone") == "suspense creciente"
        assert result.cinematic_grammar_overrides.get("rhythm") == "lento, pausado"


class TestResolveShot:
    def test_resolve_shot_merges_all(self) -> None:
        bundle = _bundle_with_marta()
        result = director_notes_resolver.resolve_notes_for_shot(
            "proj_corto", "seq_entrada", 1, bundle
        )
        assert result.shot_number == 1
        assert result.cinematic_grammar_overrides.get("coverage_pattern") == "suspense_coverage"
        assert result.cinematic_grammar_overrides.get("shot_type") == "extreme_long_shot"

    def test_resolve_shot_no_match(self) -> None:
        bundle = _bundle_with_marta()
        result = director_notes_resolver.resolve_notes_for_shot(
            "proj_corto", "seq_entrada", 99, bundle
        )
        assert result.shot_number == 99
        assert len(result.cinematic_grammar_overrides) == 0


class TestMergePriority:
    def test_override_manual_wins(self) -> None:
        project_auto = ProjectDirectorNotes(
            project_id="proj_001",
            global_tone="comedia",
            source=DirectorNoteSource.SYSTEM,
            override_priority=DirectorNoteOverrideLevel.AUTOMATIC_HEURISTIC,
            reviewed_by_user=True,
        )
        project_manual = ProjectDirectorNotes(
            project_id="proj_001",
            global_tone="suspense",
            source=DirectorNoteSource.MANUAL,
            override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
            reviewed_by_user=True,
        )
        merged = director_notes_resolver.merge_notes_by_priority(
            project_notes=project_manual,
        )
        assert merged.get("global_tone") == "suspense"

    def test_manual_overrides_visual_bible(self) -> None:
        char_vb = CharacterDirectorNotes(
            character_id="c1",
            character_name="Marta",
            wardrobe="Vestido rojo",
            source=DirectorNoteSource.IMPORTED,
            override_priority=DirectorNoteOverrideLevel.VISUAL_BIBLE,
            reviewed_by_user=True,
        )
        char_manual = CharacterDirectorNotes(
            character_id="c1",
            character_name="Marta",
            wardrobe="Chaqueta negra",
            source=DirectorNoteSource.MANUAL,
            override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
            reviewed_by_user=True,
        )
        merged = director_notes_resolver.merge_notes_by_priority(
            character_notes=[char_vb, char_manual],
        )
        merges = merged.get("wardrobe", "")
        assert "Chaqueta negra" in str(merged)
        assert "Vestido rojo" not in str(merged)

    def test_sequence_overrides_project(self) -> None:
        merged = director_notes_resolver.merge_notes_by_priority(
            project_notes=PROJECT_NOTES,
            sequence_notes=SEQUENCE_NOTES,
        )
        assert merged.get("tone") == "suspense creciente"

    def test_shot_overrides_sequence(self) -> None:
        merged = director_notes_resolver.merge_notes_by_priority(
            project_notes=PROJECT_NOTES,
            sequence_notes=SEQUENCE_NOTES,
            shot_notes=SHOT_NOTES,
        )
        if merged.get("coverage_pattern_override"):
            assert merged["coverage_pattern_override"] == "suspense_coverage"


class TestPromptBlocks:
    def test_character_lock_block(self) -> None:
        bundle = _bundle_with_marta()
        blocks = director_notes_resolver.build_prompt_blocks(bundle)
        assert blocks.character_lock_block is not None
        assert "Marta" in blocks.character_lock_block
        assert "Chaqueta oscura" in blocks.character_lock_block

    def test_location_lock_block(self) -> None:
        bundle = _bundle_with_marta()
        blocks = director_notes_resolver.build_prompt_blocks(bundle)
        assert blocks.location_lock_block is not None
        assert "Casa abandonada" in blocks.location_lock_block

    def test_prop_lock_block(self) -> None:
        bundle = _bundle_with_marta()
        blocks = director_notes_resolver.build_prompt_blocks(bundle)
        assert blocks.prop_lock_block is not None
        assert "Linterna" in blocks.prop_lock_block

    def test_visual_raccord_block(self) -> None:
        bundle = _bundle_with_marta()
        blocks = director_notes_resolver.build_prompt_blocks(bundle)
        assert blocks.visual_raccord_block is not None
        assert "Vestuario consistente" in blocks.visual_raccord_block
        assert "Iluminación consistente" in blocks.visual_raccord_block

    def test_continuity_block(self) -> None:
        bundle = _bundle_with_marta()
        blocks = director_notes_resolver.build_prompt_blocks(bundle)
        assert blocks.continuity_prompt_block is not None
        assert "Misma chaqueta" in blocks.continuity_prompt_block

    def test_negative_constraints(self) -> None:
        bundle = _bundle_with_marta()
        blocks = director_notes_resolver.build_prompt_blocks(bundle)
        assert len(blocks.prompt_negative_constraints) > 0
        negatives = " ".join(blocks.prompt_negative_constraints)
        assert "evitar" in negatives.lower()

    def test_positive_additions(self) -> None:
        bundle = _bundle_with_marta()
        blocks = director_notes_resolver.build_prompt_blocks(bundle)
        assert len(blocks.prompt_positive_additions) > 0


class TestVoiceDraft:
    def test_voice_draft_not_applied_without_review(self) -> None:
        draft = VoiceDirectorNoteDraft(
            transcript="Marta entra en silencio con la linterna",
            transcript_confidence=0.85,
            extracted_entities={"character": ["Marta"], "prop": ["linterna"]},
            reviewed_by_user=False,
        )
        bundle = DirectorNotesBundle(
            project=PROJECT_NOTES,
            characters=[MARTA_CHARACTER],
            voice_drafts=[draft],
        )
        result = director_notes_resolver.resolve_notes_for_project("proj_corto", bundle)
        assert len(result.voice_drafts_pending_review) == 1
        pending = result.voice_drafts_pending_review[0]
        assert pending.transcript == "Marta entra en silencio con la linterna"

    def test_reviewed_draft_not_pending(self) -> None:
        draft = VoiceDirectorNoteDraft(
            transcript="Marta entra en silencio",
            transcript_confidence=0.95,
            reviewed_by_user=True,
        )
        bundle = DirectorNotesBundle(voice_drafts=[draft])
        result = director_notes_resolver.resolve_notes_for_project("proj_test", bundle)
        assert len(result.voice_drafts_pending_review) == 0

    def test_voice_draft_extracted_entities(self) -> None:
        draft = VoiceDirectorNoteDraft(
            transcript="Marta entra en silencio con la linterna",
            transcript_confidence=0.92,
            extracted_entities={"character": ["Marta"], "prop": ["linterna"]},
            reviewed_by_user=False,
        )
        assert "character" in draft.extracted_entities
        assert "Marta" in draft.extracted_entities["character"]


class TestTraceMetadata:
    def test_trace_includes_director_note_refs(self) -> None:
        bundle = _bundle_with_marta()
        trace = director_notes_resolver.build_trace_metadata(
            bundle, project_id="proj_corto", sequence_id="seq_entrada", shot_number=1
        )
        assert trace["project_id"] == "proj_corto"
        assert trace["sequence_id"] == "seq_entrada"
        assert trace["shot_number"] == 1
        assert "director_note_refs" in trace
        assert trace["character_notes_count"] == 1
        assert trace["location_notes_count"] == 1
        assert trace["prop_notes_count"] == 1

    def test_trace_applied_sources_sorted_by_priority(self) -> None:
        bundle = _bundle_with_marta()
        trace = director_notes_resolver.build_trace_metadata(bundle, project_id="proj_corto")
        sources = trace["applied_sources"]
        assert len(sources) >= 4
        priorities = [s["priority"] for s in sources]
        order = {
            "override_manual": 0,
            "sequence_shot": 1,
            "visual_bible": 2,
            "script_analysis": 3,
            "automatic_heuristic": 4,
        }
        for i in range(len(priorities) - 1):
            assert order[priorities[i]] <= order[priorities[i + 1]]

    def test_trace_with_empty_bundle(self) -> None:
        bundle = DirectorNotesBundle()
        trace = director_notes_resolver.build_trace_metadata(bundle)
        assert trace["override_count"] == 0
        assert trace["voice_drafts_pending"] == 0


class TestMergeEmpty:
    def test_merge_no_notes(self) -> None:
        merged = director_notes_resolver.merge_notes_by_priority()
        assert merged.get("sources") == []
        assert merged.get("tone") is None

    def test_merge_only_project(self) -> None:
        merged = director_notes_resolver.merge_notes_by_priority(
            project_notes=PROJECT_NOTES,
        )
        assert "project" in merged["sources"]
        assert merged.get("global_tone") == "suspense"


class TestOverrideManualEdgeCases:
    def test_override_tracks_field_path(self) -> None:
        override = DirectorNoteOverride(
            field_path="character.Marta.wardrobe",
            previous_value="Chaqueta marrón",
            new_value="Chaqueta negra",
        )
        assert override.field_path == "character.Marta.wardrobe"
        assert override.previous_value == "Chaqueta marrón"

    def test_multiple_overrides_same_field(self) -> None:
        bundle = DirectorNotesBundle(
            project=PROJECT_NOTES,
            overrides=[
                DirectorNoteOverride(
                    field_path="global_tone",
                    previous_value="comedia",
                    new_value="suspense",
                ),
            ],
        )
        result = director_notes_resolver.resolve_notes_for_project("proj_corto", bundle)
        assert len(result.applied_overrides) == 1
        assert result.applied_overrides[0].field_path == "global_tone"
