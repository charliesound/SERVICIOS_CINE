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
    BlockingNotes,
    CharacterDirectorNotes,
    DirectorNoteOverride,
    DirectorNoteOverrideLevel,
    DirectorNoteSource,
    DirectorNotesBundle,
    DirectorNotesResolveRequest,
    DirectorNotesResolveResult,
    DramaticIntent,
    LocationDirectorNotes,
    ProjectDirectorNotes,
    PromptBlocks,
    PropDirectorNotes,
    SequenceDirectorNotes,
    ShotDirectorNotes,
    VoiceDirectorNoteDraft,
)


class TestBlockingNotes:
    def test_defaults(self) -> None:
        b = BlockingNotes()
        assert b.blocking_notes is None
        assert b.entrance_direction is None

    def test_with_values(self) -> None:
        b = BlockingNotes(
            blocking_notes="Entra por la izquierda",
            entrance_direction="left",
            exit_direction="right",
            eyeline_target="Marta",
            axis_rule="180_degree",
        )
        assert b.blocking_notes == "Entra por la izquierda"
        assert b.axis_rule == "180_degree"


class TestDramaticIntent:
    def test_defaults(self) -> None:
        d = DramaticIntent()
        assert d.tone is None

    def test_with_values(self) -> None:
        d = DramaticIntent(
            tone="suspense",
            emotional_goal="tension",
            suspense_level="high",
            director_intent="Crear incertidumbre",
        )
        assert d.tone == "suspense"
        assert d.director_intent == "Crear incertidumbre"


class TestCharacterDirectorNotes:
    def test_minimal(self) -> None:
        c = CharacterDirectorNotes(
            character_id="char_001",
            character_name="Marta",
        )
        assert c.character_id == "char_001"
        assert c.character_name == "Marta"
        assert c.source == DirectorNoteSource.MANUAL
        assert c.override_priority == DirectorNoteOverrideLevel.OVERRIDE_MANUAL

    def test_full(self) -> None:
        c = CharacterDirectorNotes(
            character_id="char_001",
            character_name="Marta",
            age_range="30-35",
            face_description="Ovalada, ojos oscuros",
            hair="Castaño largo",
            wardrobe="Chaqueta oscura, vaqueros",
            body_language="Tensa, alerta",
            emotional_state="Asustada pero decidida",
            continuity_constraints=["Misma chaqueta en toda la escena"],
            forbidden_changes=["No cambiar peinado"],
            visual_references=["ref_marta_001.jpg"],
        )
        assert c.face_description == "Ovalada, ojos oscuros"
        assert len(c.continuity_constraints) == 1
        assert c.forbidden_changes[0] == "No cambiar peinado"

    def test_serialize_roundtrip(self) -> None:
        c = CharacterDirectorNotes(
            character_id="char_001",
            character_name="Marta",
            age_range="30-35",
        )
        data = c.model_dump()
        restored = CharacterDirectorNotes.model_validate(data)
        assert restored.character_id == "char_001"
        assert restored.age_range == "30-35"


class TestLocationDirectorNotes:
    def test_minimal(self) -> None:
        loc = LocationDirectorNotes(
            location_id="loc_001",
            location_name="Casa abandonada",
        )
        assert loc.location_id == "loc_001"
        assert loc.atmosphere is None

    def test_with_values(self) -> None:
        loc = LocationDirectorNotes(
            location_id="loc_001",
            location_name="Casa abandonada",
            period="contemporáneo",
            architecture_style="rural",
            atmosphere="silencioso, polvoriento",
            lighting="oscuro, linterna como luz motriz",
            color_palette=["negro", "marrón", "gris"],
            textures=["madera agrietada", "yeso descascarillado"],
            spatial_layout="pasillo estrecho",
            recurring_elements=["puerta al fondo"],
            forbidden_elements=["luz blanca", "mobiliario moderno"],
            continuity_constraints=["Misma disposición en todos los planos"],
        )
        assert loc.architecture_style == "rural"
        assert len(loc.color_palette) == 3

    def test_serialize_roundtrip(self) -> None:
        loc = LocationDirectorNotes(
            location_id="loc_001",
            location_name="Casa abandonada",
            atmosphere="silencioso",
        )
        data = loc.model_dump()
        restored = LocationDirectorNotes.model_validate(data)
        assert restored.location_name == "Casa abandonada"


class TestPropDirectorNotes:
    def test_minimal(self) -> None:
        p = PropDirectorNotes(prop_id="prop_001", prop_name="Linterna")
        assert p.must_appear is True
        assert p.source == DirectorNoteSource.MANUAL

    def test_with_values(self) -> None:
        p = PropDirectorNotes(
            prop_id="prop_001",
            prop_name="Linterna",
            description="Linterna metálica negra",
            placement="mano derecha de Marta",
            dramatic_importance="alta",
            continuity_rule="Misma linterna en todos los planos",
            must_appear=True,
            forbidden_changes=["No cambiar tamaño"],
        )
        assert p.dramatic_importance == "alta"

    def test_serialize_roundtrip(self) -> None:
        p = PropDirectorNotes(prop_id="prop_001", prop_name="Linterna")
        data = p.model_dump()
        restored = PropDirectorNotes.model_validate(data)
        assert restored.prop_name == "Linterna"


class TestSequenceDirectorNotes:
    def test_minimal(self) -> None:
        s = SequenceDirectorNotes(sequence_id="seq_001")
        assert s.override_priority == DirectorNoteOverrideLevel.SEQUENCE_SHOT

    def test_with_visual_metaphor(self) -> None:
        s = SequenceDirectorNotes(
            sequence_id="seq_001",
            sequence_title="Entrada a la casa",
            tone="suspense",
            rhythm="lento",
            emotional_goal="tensión creciente",
            visual_metaphor="La oscuridad como amenaza",
        )
        assert s.visual_metaphor == "La oscuridad como amenaza"


class TestShotDirectorNotes:
    def test_minimal(self) -> None:
        s = ShotDirectorNotes()
        assert s.source == DirectorNoteSource.MANUAL

    def test_with_overrides(self) -> None:
        s = ShotDirectorNotes(
            shot_number=3,
            sequence_id="seq_001",
            coverage_pattern_override="suspense_coverage",
            shot_type_override="close_up",
            priority_override="must_have",
            reference_mode_override="filmic",
        )
        assert s.coverage_pattern_override == "suspense_coverage"
        assert s.shot_type_override == "close_up"


class TestProjectDirectorNotes:
    def test_minimal(self) -> None:
        p = ProjectDirectorNotes(project_id="proj_001")
        assert p.global_tone is None

    def test_with_values(self) -> None:
        p = ProjectDirectorNotes(
            project_id="proj_001",
            project_title="Cortometraje suspense",
            global_tone="suspense",
            global_visual_style="noir",
            global_lighting="low_key",
            global_atmosphere="opresivo",
            notes="Mantener tensión constante",
        )
        assert p.global_visual_style == "noir"


class TestVoiceDirectorNoteDraft:
    def test_default_not_reviewed(self) -> None:
        v = VoiceDirectorNoteDraft(transcript="Marta entra en silencio")
        assert v.source == DirectorNoteSource.VOICE
        assert v.reviewed_by_user is False
        assert v.transcript_confidence == 0.0

    def test_high_confidence(self) -> None:
        v = VoiceDirectorNoteDraft(
            transcript="Marta entra en silencio con la linterna",
            transcript_confidence=0.92,
            extracted_entities={"character": ["Marta"], "prop": ["linterna"]},
        )
        assert v.transcript_confidence == 0.92
        assert "Marta" in v.extracted_entities["character"]


class TestDirectorNoteOverride:
    def test_minimal(self) -> None:
        o = DirectorNoteOverride(
            field_path="character.Marta.wardrobe",
            new_value="Chaqueta negra",
        )
        assert o.previous_value is None

    def test_with_previous(self) -> None:
        o = DirectorNoteOverride(
            field_path="character.Marta.wardrobe",
            previous_value="Chaqueta marrón",
            new_value="Chaqueta negra",
            override_source=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
        )
        assert o.previous_value == "Chaqueta marrón"


class TestDirectorNotesBundle:
    def test_empty(self) -> None:
        b = DirectorNotesBundle()
        assert len(b.sequences) == 0
        assert len(b.characters) == 0

    def test_with_all_entities(self) -> None:
        b = DirectorNotesBundle(
            project=ProjectDirectorNotes(project_id="proj_001"),
            sequences=[SequenceDirectorNotes(sequence_id="seq_001")],
            shots=[ShotDirectorNotes(shot_number=1)],
            characters=[CharacterDirectorNotes(character_id="char_001", character_name="Marta")],
            locations=[LocationDirectorNotes(location_id="loc_001", location_name="Casa")],
            props=[PropDirectorNotes(prop_id="prop_001", prop_name="Linterna")],
            voice_drafts=[VoiceDirectorNoteDraft(transcript="test")],
        )
        assert b.project is not None
        assert len(b.sequences) == 1
        assert len(b.shots) == 1
        assert len(b.characters) == 1
        assert len(b.locations) == 1
        assert len(b.props) == 1
        assert len(b.voice_drafts) == 1

    def test_serialize_roundtrip(self) -> None:
        b = DirectorNotesBundle(
            project=ProjectDirectorNotes(project_id="proj_001"),
            characters=[
                CharacterDirectorNotes(character_id="char_001", character_name="Marta")
            ],
        )
        data = b.model_dump()
        restored = DirectorNotesBundle.model_validate(data)
        assert restored.project is not None
        assert restored.project.project_id == "proj_001"
        assert len(restored.characters) == 1


class TestDirectorNotesResolveRequest:
    def test_minimal(self) -> None:
        r = DirectorNotesResolveRequest(
            project_id="proj_001",
            bundle=DirectorNotesBundle(),
        )
        assert r.sequence_id is None
        assert r.shot_number is None

    def test_with_context(self) -> None:
        r = DirectorNotesResolveRequest(
            project_id="proj_001",
            sequence_id="seq_001",
            shot_number=3,
            bundle=DirectorNotesBundle(
                characters=[CharacterDirectorNotes(character_id="c1", character_name="Ana")]
            ),
            scene_text="Ana entra en la habitación",
            character_names=["Ana"],
        )
        assert r.sequence_id == "seq_001"
        assert r.shot_number == 3


class TestDirectorNotesResolveResult:
    def test_defaults(self) -> None:
        r = DirectorNotesResolveResult(project_id="proj_001")
        assert r.prompt_blocks is not None
        assert len(r.applied_overrides) == 0

    def test_with_cg_overrides(self) -> None:
        r = DirectorNotesResolveResult(
            project_id="proj_001",
            cinematic_grammar_overrides={"coverage_pattern": "suspense_coverage"},
        )
        assert r.cinematic_grammar_overrides["coverage_pattern"] == "suspense_coverage"


class TestPromptBlocks:
    def test_defaults(self) -> None:
        pb = PromptBlocks()
        assert len(pb.prompt_positive_additions) == 0

    def test_with_blocks(self) -> None:
        pb = PromptBlocks(
            prompt_positive_additions=["Tono: suspense"],
            prompt_negative_constraints=["Evitar luz blanca"],
            continuity_prompt_block="Mantener raccord",
            character_lock_block="Marta: chaqueta negra",
            location_lock_block="Casa abandonada",
            prop_lock_block="Linterna",
            visual_raccord_block="Consistencia visual",
        )
        assert len(pb.prompt_positive_additions) == 1
        assert pb.character_lock_block == "Marta: chaqueta negra"
