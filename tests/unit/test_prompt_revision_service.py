from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from schemas.cid_director_feedback_schema import (
    DirectorFeedbackInterpretation,
    DirectorFeedbackNote,
    FeedbackCategory,
    FeedbackSeverity,
)
from services.prompt_revision_service import PromptRevisionService


service = PromptRevisionService()


def _make_interpretation(
    requested: list[str] | None = None,
    protected_story: list[str] | None = None,
    protected_visual: list[str] | None = None,
    conflict_script: bool = False,
    conflict_ref: bool = False,
    conflict_prompt: bool = False,
) -> DirectorFeedbackInterpretation:
    return DirectorFeedbackInterpretation(
        requested_changes=requested or [],
        protected_story_elements=protected_story or [],
        protected_visual_elements=protected_visual or [],
        conflict_with_script=conflict_script,
        conflict_with_script_details="Script conflict" if conflict_script else "",
        conflict_with_reference=conflict_ref,
        conflict_with_reference_details="Reference conflict" if conflict_ref else "",
        conflict_with_initial_prompt=conflict_prompt,
        conflict_with_initial_prompt_details="Prompt conflict" if conflict_prompt else "",
        recommended_action="Apply changes",
        risk_level="low" if not conflict_script else "high",
        explanation="Test interpretation",
    )


def test_lighting_note_adds_brightness_and_negative() -> None:
    prompt_spec = {
        "positive_prompt": "dark dramatic scene, low key lighting, deep shadows",
        "negative_prompt": "overexposed, blown out highlights",
    }
    interpretation = _make_interpretation(
        requested=["Increase overall brightness and exposure", "Reduce shadow density"],
    )
    revision = service.revise_prompt_with_director_feedback(
        prompt_spec=prompt_spec,
        feedback_interpretation=interpretation,
    )
    assert "well-lit" in revision.revised_prompt.lower(), (
        f"Expected well-lit in revised prompt, got: {revision.revised_prompt}"
    )
    assert "underexposed" in revision.revised_negative_prompt.lower(), (
        f"Expected underexposed in negative, got: {revision.revised_negative_prompt}"
    )
    assert revision.version_number == 1


def test_camera_medium_shot_replaces_shot_type() -> None:
    prompt_spec = {
        "positive_prompt": "wide shot of a character walking through a corridor, cinematic lighting",
        "negative_prompt": "low quality, blurry",
    }
    interpretation = _make_interpretation(
        requested=["Change shot type to medium shot (MS)", "Frame from waist up"],
    )
    revision = service.revise_prompt_with_director_feedback(
        prompt_spec=prompt_spec,
        feedback_interpretation=interpretation,
    )
    assert "medium" in revision.revised_prompt.lower(), (
        f"Expected medium shot in revised prompt, got: {revision.revised_prompt}"
    )


def test_preserves_protected_elements() -> None:
    prompt_spec = {
        "positive_prompt": "nocturnal scene, moonlight through window",
        "negative_prompt": "overexposed",
    }
    interpretation = _make_interpretation(
        requested=["Increase overall brightness and exposure"],
        protected_story=["Location: Interior habitación", "Time: Noche", "Character actions: Marta mira por la ventana"],
        protected_visual=["Reference visual summary: Noir oscuro"],
    )
    revision = service.revise_prompt_with_director_feedback(
        prompt_spec=prompt_spec,
        feedback_interpretation=interpretation,
    )
    assert len(revision.preserved_elements) >= 3, (
        f"Expected at least 3 preserved elements, got: {revision.preserved_elements}"
    )
    assert any("Noche" in e or "night" in e.lower() for e in revision.preserved_elements), (
        f"Expected night/location preserved, got: {revision.preserved_elements}"
    )


def test_shot_reverse_adds_eyeline_continuity() -> None:
    prompt_spec = {
        "positive_prompt": "two characters sitting at a table, medium shot",
        "negative_prompt": "generic",
    }
    interpretation = _make_interpretation(
        requested=[
            "Add over-the-shoulder shot",
            "Add reverse shot",
            "Maintain eyeline match",
            "Add shot/reverse-shot coverage",
        ],
    )
    revision = service.revise_prompt_with_director_feedback(
        prompt_spec=prompt_spec,
        feedback_interpretation=interpretation,
    )
    revised = revision.revised_prompt.lower()
    assert "eyeline" in revised, f"Expected eyeline in revised prompt, got: {revised}"
    assert "over-the-shoulder" in revised, f"Expected OTS in revised prompt, got: {revised}"


def test_rejected_changes_when_no_match() -> None:
    prompt_spec = {
        "positive_prompt": "standard scene",
        "negative_prompt": "",
    }
    interpretation = _make_interpretation(
        requested=["This specific change has no matching pattern xyz123"],
    )
    revision = service.revise_prompt_with_director_feedback(
        prompt_spec=prompt_spec,
        feedback_interpretation=interpretation,
    )
    assert len(revision.rejected_changes) >= 1, (
        f"Expected rejected changes for unmatchable request, got: {revision.rejected_changes}"
    )


def test_conflict_script_blocks_negative_prompt() -> None:
    prompt_spec = {
        "positive_prompt": "night exterior, dark alley, moonlight",
        "negative_prompt": "daylight",
    }
    interpretation = _make_interpretation(
        requested=["Increase overall brightness and exposure"],
        conflict_script=True,
        protected_story=["Time: Noche"],
    )
    revision = service.revise_prompt_with_director_feedback(
        prompt_spec=prompt_spec,
        feedback_interpretation=interpretation,
    )
    assert "SCRIPT CONFLICT" in revision.revision_reason or "conflict_with_script" in revision.revision_reason.lower() or "conflict" in revision.revision_reason.lower(), (
        f"Expected script conflict in reason, got: {revision.revision_reason}"
    )


def test_character_not_from_behind() -> None:
    prompt_spec = {
        "positive_prompt": "medium shot showing character from behind, walking away",
        "negative_prompt": "generic",
    }
    interpretation = _make_interpretation(
        requested=["Rotate character to face camera or action", "Do NOT show character from behind"],
    )
    revision = service.revise_prompt_with_director_feedback(
        prompt_spec=prompt_spec,
        feedback_interpretation=interpretation,
    )
    assert "character facing" in revision.revised_prompt.lower() or "front" in revision.revised_prompt.lower(), (
        f"Expected front-facing character in revised, got: {revision.revised_prompt}"
    )
    assert "facing away" in revision.revised_negative_prompt.lower(), (
        f"Expected 'facing away' in negative, got: {revision.revised_negative_prompt}"
    )
