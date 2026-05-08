from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from schemas.cid_director_feedback_schema import (
    DirectorFeedbackNote,
    FeedbackCategory,
    FeedbackSeverity,
    FeedbackTargetType,
)
from services.director_feedback_interpretation_service import (
    DirectorFeedbackInterpretationService,
)


service = DirectorFeedbackInterpretationService()


def test_too_dark_increases_clarity() -> None:
    note = DirectorFeedbackNote(
        note_id="test_01",
        target_type=FeedbackTargetType.shot,
        target_id="shot_001",
        note_text="Esto está demasiado oscuro",
        category=FeedbackCategory.lighting,
        severity=FeedbackSeverity.medium,
    )
    interpretation = service.interpret_feedback(note)
    assert any("brightness" in c.lower() or "exposure" in c.lower() for c in interpretation.requested_changes), (
        f"Expected brightness/exposure change, got: {interpretation.requested_changes}"
    )
    assert interpretation.risk_level in ("low", "medium")


def test_quiero_plano_medio_changes_camera() -> None:
    note = DirectorFeedbackNote(
        note_id="test_02",
        target_type=FeedbackTargetType.shot,
        target_id="shot_002",
        note_text="Quiero un plano medio",
        category=FeedbackCategory.camera,
        severity=FeedbackSeverity.minor,
    )
    interpretation = service.interpret_feedback(note)
    assert any("medium" in c.lower() for c in interpretation.requested_changes), (
        f"Expected medium shot change, got: {interpretation.requested_changes}"
    )


def test_plano_contraplano_adds_eyeline() -> None:
    note = DirectorFeedbackNote(
        note_id="test_03",
        target_type=FeedbackTargetType.shot,
        target_id="shot_003",
        note_text="Aquí necesito plano contraplano",
        category=FeedbackCategory.camera,
        severity=FeedbackSeverity.minor,
    )
    interpretation = service.interpret_feedback(note)
    changes_text = " ".join(interpretation.requested_changes).lower()
    assert "over-the-shoulder" in changes_text or "eyeline" in changes_text or "reverse" in changes_text, (
        f"Expected OTS/eyeline/reverse change, got: {interpretation.requested_changes}"
    )


def test_contradicts_script_marks_conflict() -> None:
    note = DirectorFeedbackNote(
        note_id="test_04",
        target_type=FeedbackTargetType.shot,
        target_id="shot_004",
        note_text="Quiero más luz natural",
        category=FeedbackCategory.lighting,
        severity=FeedbackSeverity.medium,
    )
    prompt_spec = {
        "positive_prompt": "nocturnal dark night scene, moonlight only, deep shadows",
    }
    interpretation = service.interpret_feedback(
        note,
        original_prompt=prompt_spec,
        script_context={"location": "Cementerio", "time_of_day": "Noche", "action_summary": "Escena nocturna"},
    )
    assert interpretation.conflict_with_initial_prompt, (
        "Should detect conflict: note requests light but script/prompt says night"
    )


def test_no_script_conflict_for_minor_change() -> None:
    note = DirectorFeedbackNote(
        note_id="test_05",
        target_type=FeedbackTargetType.shot,
        target_id="shot_005",
        note_text="El personaje no debería estar de espaldas",
        category=FeedbackCategory.character,
        severity=FeedbackSeverity.minor,
    )
    interpretation = service.interpret_feedback(note)
    assert not interpretation.conflict_with_script, "Minor character note should not conflict with script"
    assert any("face camera" in c.lower() or "front" in c.lower() for c in interpretation.requested_changes), (
        f"Expected front-facing change, got: {interpretation.requested_changes}"
    )


def test_protected_story_elements_from_metadata() -> None:
    note = DirectorFeedbackNote(
        note_id="test_06",
        target_type=FeedbackTargetType.shot,
        target_id="shot_006",
        note_text="Cambiar iluminación a más natural",
        category=FeedbackCategory.lighting,
        severity=FeedbackSeverity.minor,
    )
    metadata = {
        "script_visual_alignment": {
            "non_negotiable_story_elements": [
                "Location: Interior oficina",
                "Time: Noche",
                "Character actions: Juan entra y enciende la luz",
            ],
            "non_negotiable_visual_elements": [
                "Do not copy specific content from reference",
            ],
        },
        "visual_reference_profile": {
            "visual_summary": "Noir oscuro con luces de neón",
            "non_transferable_traits": ["specific people", "brand logos"],
        },
    }
    interpretation = service.interpret_feedback(note, storyboard_metadata=metadata)
    assert any("Location" in e for e in interpretation.protected_story_elements), (
        f"Expected protected location, got: {interpretation.protected_story_elements}"
    )
    assert any("Time" in e for e in interpretation.protected_story_elements), (
        f"Expected protected time, got: {interpretation.protected_story_elements}"
    )


def test_camera_note_wide_shot() -> None:
    note = DirectorFeedbackNote(
        note_id="test_07",
        target_type=FeedbackTargetType.shot,
        target_id="shot_007",
        note_text="Este plano debería ser un plano general",
        category=FeedbackCategory.camera,
        severity=FeedbackSeverity.minor,
    )
    interpretation = service.interpret_feedback(note)
    assert any("wide" in c.lower() for c in interpretation.requested_changes), (
        f"Expected wide shot change, got: {interpretation.requested_changes}"
    )


def test_tone_note_detected() -> None:
    note = DirectorFeedbackNote(
        note_id="test_08",
        target_type=FeedbackTargetType.shot,
        target_id="shot_008",
        note_text="No me gusta el tono, quiero algo más serio",
        category=FeedbackCategory.tone,
        severity=FeedbackSeverity.medium,
    )
    interpretation = service.interpret_feedback(note)
    assert any("serious" in c.lower() or "dramatic" in c.lower() for c in interpretation.requested_changes), (
        f"Expected serious/dramatic change, got: {interpretation.requested_changes}"
    )
