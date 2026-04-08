from src.services.continuity_formal_service import ContinuityFormalService


def test_continuity_assigns_axis_for_two_character_dialogue() -> None:
    service = ContinuityFormalService()

    continuity_a = service.assign_continuity(
        shot_intent="two_shot",
        beat_type="dialogue",
        characters=["Carlos", "Marta"],
        shot_index=1,
        previous_shots=[],
    )

    assert continuity_a is not None
    assert continuity_a["axis_side"] == "center"
    assert continuity_a["eyeline_direction"] == "mutual"
    assert continuity_a["screen_position"] == "centered"
    assert continuity_a["counterpart_anchor"] == "both_characters"


def test_continuity_over_shoulder_and_reverse_eyeline() -> None:
    service = ContinuityFormalService()

    os1 = service.assign_continuity(
        shot_intent="over_shoulder",
        beat_type="dialogue",
        characters=["Carlos", "Marta"],
        shot_index=1,
        previous_shots=[],
    )

    os2 = service.assign_continuity(
        shot_intent="over_shoulder",
        beat_type="dialogue",
        characters=["Marta", "Carlos"],
        shot_index=2,
        previous_shots=[{"continuity_formal": os1}] if os1 else [],
    )

    assert os1 is not None
    assert os2 is not None
    assert os1["axis_side"] == os2["axis_side"]
    assert "carlos" in os1["eyeline_direction"].lower() or "marta" in os1["eyeline_direction"].lower()
    assert os1["screen_position"] != os2["screen_position"] or os1["screen_position"] == os2["screen_position"]


def test_continuity_reaction_with_counterpart_anchor() -> None:
    service = ContinuityFormalService()

    continuity = service.assign_continuity(
        shot_intent="reaction",
        beat_type="reaction",
        characters=["Marta", "Carlos"],
        shot_index=3,
        previous_shots=[],
    )

    assert continuity is not None
    assert continuity["counterpart_anchor"] == "Carlos"
    assert "marta" in continuity["eyeline_direction"].lower() or "towards" in continuity["eyeline_direction"].lower()


def test_continuity_does_not_force_non_conversational_scene() -> None:
    service = ContinuityFormalService()

    continuity = service.assign_continuity(
        shot_intent="establishing",
        beat_type="exposition",
        characters=["Carlos"],
        shot_index=1,
        previous_shots=[],
    )

    assert continuity is None


def test_continuity_fallback_with_single_character() -> None:
    service = ContinuityFormalService()

    continuity = service.assign_continuity(
        shot_intent="close_up",
        beat_type="dialogue",
        characters=["Carlos"],
        shot_index=1,
        previous_shots=[],
    )

    assert continuity is not None
    assert continuity["axis_side"] == "left_of_axis"
    assert continuity["eyeline_direction"] == "neutral"
    assert continuity["counterpart_anchor"] is None
