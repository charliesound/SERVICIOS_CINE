from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from scripts.local_media_agent.editorial_selection import (
    DAVINCI_NOT_REQUESTED,
    DAVINCI_UNAVAILABLE,
    REASON_AUDIO_ONLY,
    ROLE_DIRECTOR,
    ROLE_EDITOR,
    ROLE_PRODUCER,
    STATUS_IN_EDIT,
    STATUS_READY_FOR_EDITOR,
    STATUS_REJECTED,
    STATUS_SELECTED,
    STATUS_USED,
    SelectionError,
    SelectionStore,
    apply_transition,
    create_selection,
    render_view,
    selection_id_for,
)


def _write_evidence(tmp_path: Path) -> str:
    items = [
        {
            "candidate_id": "SIRUELA-CTX-045",
            "interview_subject": "Pruden",
            "topic": "problemas/dificultades",
            "PRODUCER_CONTEXT_EXCERPT": "en las vacas si no son capaces de echar la cría",
            "EXCERPT_AUDIO_START": 902.17,
            "EXCERPT_AUDIO_END": 908.27,
            "EXCERPT_VIDEO_MAPPING_STATUS": "MAPPED",
            "video_clip": "A7IV_SL31277.MP4",
            "EXCERPT_VIDEO_RELATIVE_START": 554.125,
            "EXCERPT_VIDEO_RELATIVE_END": 560.225,
            "SPEAKER_ATTRIBUTION": "UNKNOWN",
            "EDITORIAL_NOTE": "Calving difficulty and a calf's high economic value.",
        },
        {
            "candidate_id": "SIRUELA-CTX-022",
            "interview_subject": "Pruden",
            "topic": "ovejas/ovino",
            "PRODUCER_CONTEXT_EXCERPT": "el rebaño por la mañana",
            "EXCERPT_AUDIO_START": 10.0,
            "EXCERPT_AUDIO_END": 12.0,
            "EXCERPT_VIDEO_MAPPING_STATUS": "AUDIO_ONLY_VIDEO_UNMAPPED",
            "video_clip": None,
            "EXCERPT_VIDEO_RELATIVE_START": None,
            "EXCERPT_VIDEO_RELATIVE_END": None,
            "SPEAKER_ATTRIBUTION": "UNKNOWN",
            "EDITORIAL_NOTE": "Audio-only recollection.",
        },
    ]
    evidence = {
        "REFERENCE_SET_TYPE": "producer",
        "PROJECT": "Siruela",
        "items": items,
    }
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(evidence, ensure_ascii=False), encoding="utf-8")
    return str(path)


@pytest.fixture()
def evidence(tmp_path: Path) -> str:
    return _write_evidence(tmp_path)


@pytest.fixture()
def store(tmp_path: Path) -> str:
    return str(tmp_path / "selections")


# ---------------- creation ----------------

def test_mapped_selection_creation(evidence, store) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER, note="nota")
    assert sel["candidate_id"] == "SIRUELA-CTX-045"
    assert sel["status"] == STATUS_SELECTED
    assert sel["video_clip"] == "A7IV_SL31277.MP4"
    assert sel["source_in_seconds"] == 554.125
    assert sel["source_out_seconds"] == 560.225
    assert sel["davinci_reference_status"] == DAVINCI_NOT_REQUESTED


def test_deterministic_selection_id(evidence) -> None:
    assert selection_id_for("SIRUELA-CTX-045") == "SEL-SIRUELA-CTX-045"
    a = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    b = create_selection(evidence, "SIRUELA-CTX-045", ROLE_DIRECTOR)
    assert a["selection_id"] == b["selection_id"] == "SEL-SIRUELA-CTX-045"


def test_evidence_fields_preserved_exactly(evidence, store) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    assert sel["subject"] == "Pruden"
    assert sel["topic"] == "problemas/dificultades"
    assert sel["excerpt"] == "en las vacas si no son capaces de echar la cría"
    store = SelectionStore(store)
    store.write(sel)
    loaded = store.read("SEL-SIRUELA-CTX-045")
    assert loaded["subject"] == "Pruden"
    assert loaded["source_in_seconds"] == 554.125
    assert loaded["source_out_seconds"] == 560.225


def test_duplicate_create_safely_rejected(evidence, store) -> None:
    from scripts.local_media_agent.editorial_selection_cli import run_cli

    argv = [
        "create",
        "--evidence-path", evidence,
        "--candidate", "SIRUELA-CTX-045",
        "--requested-by-role", ROLE_PRODUCER,
        "--store", store,
    ]
    import io

    out1, err1 = io.StringIO(), io.StringIO()
    code1 = run_cli(argv, stdout=out1, stderr=err1)
    assert code1 == 0
    out2, err2 = io.StringIO(), io.StringIO()
    code2 = run_cli(argv, stdout=out2, stderr=err2)
    assert code2 == 2
    assert "CID_EDITORIAL_SELECTION_ALREADY_EXISTS" in err2.getvalue()


def test_audio_only_selection_creation_succeeds(evidence, store) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-022", ROLE_PRODUCER)
    assert sel["status"] == STATUS_SELECTED
    assert sel["video_clip"] is None
    assert sel["source_in_seconds"] is None
    assert sel["source_out_seconds"] is None
    assert sel["davinci_reference_status"] == DAVINCI_UNAVAILABLE
    assert sel["davinci_reference_reason"] == REASON_AUDIO_ONLY


def test_audio_only_editorial_fields_preserved(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-022", ROLE_DIRECTOR)
    assert sel["topic"] == "ovejas/ovino"
    assert sel["excerpt"] == "el rebaño por la mañana"
    assert sel["davinci_reference_status"] == DAVINCI_UNAVAILABLE


def test_candidate_not_found_raises(evidence) -> None:
    with pytest.raises(SelectionError):
        create_selection(evidence, "SIRUELA-CTX-999", ROLE_PRODUCER)


# ---------------- transitions ----------------

def test_selected_to_ready_producer(evidence, store) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    updated = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)
    assert updated["status"] == STATUS_READY_FOR_EDITOR


def test_selected_to_ready_director(evidence, store) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_DIRECTOR)
    updated = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_DIRECTOR)
    assert updated["status"] == STATUS_READY_FOR_EDITOR


def test_editor_cannot_prepare_for_editor(evidence, store) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    with pytest.raises(SelectionError):
        apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_EDITOR)


def test_ready_to_in_edit_only_editor(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)
    with pytest.raises(SelectionError):
        apply_transition(ready, STATUS_IN_EDIT, ROLE_PRODUCER)
    in_edit = apply_transition(ready, STATUS_IN_EDIT, ROLE_EDITOR)
    assert in_edit["status"] == STATUS_IN_EDIT


def test_in_edit_to_used(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)
    in_edit = apply_transition(ready, STATUS_IN_EDIT, ROLE_EDITOR)
    used = apply_transition(in_edit, STATUS_USED, ROLE_EDITOR)
    assert used["status"] == STATUS_USED


def test_in_edit_to_rejected_requires_note(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)
    in_edit = apply_transition(ready, STATUS_IN_EDIT, ROLE_EDITOR)
    with pytest.raises(SelectionError):
        apply_transition(in_edit, STATUS_REJECTED, ROLE_EDITOR)
    rejected = apply_transition(
        in_edit, STATUS_REJECTED, ROLE_EDITOR, editor_note="repetido"
    )
    assert rejected["status"] == STATUS_REJECTED
    assert rejected["editor_note"] == "repetido"


def test_terminal_used_rejects_further_transition(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)
    in_edit = apply_transition(ready, STATUS_IN_EDIT, ROLE_EDITOR)
    used = apply_transition(in_edit, STATUS_USED, ROLE_EDITOR)
    with pytest.raises(SelectionError):
        apply_transition(used, STATUS_IN_EDIT, ROLE_EDITOR)


def test_terminal_rejected_rejects_further_transition(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    rejected = apply_transition(
        sel, STATUS_REJECTED, ROLE_PRODUCER, editor_note="no"
    )
    with pytest.raises(SelectionError):
        apply_transition(rejected, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)


def test_illegal_transition_rejected(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    with pytest.raises(SelectionError):
        apply_transition(sel, STATUS_IN_EDIT, ROLE_DIRECTOR)


# ---------------- store ----------------

def test_status_filtering(evidence, store) -> None:
    s = SelectionStore(store)
    a = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    b = create_selection(evidence, "SIRUELA-CTX-022", ROLE_PRODUCER)
    s.write(a)
    s.write(b)
    s.write(apply_transition(b, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER))
    ready = s.list(status=STATUS_READY_FOR_EDITOR)
    assert [x["selection_id"] for x in ready] == ["SEL-SIRUELA-CTX-022"]
    assert len(s.list()) == 2


def test_atomic_store_write_no_partial_overwrite(evidence, store) -> None:
    s = SelectionStore(store)
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    s.write(sel)
    original = s.read("SEL-SIRUELA-CTX-045")
    # Overwrite with a transitioned selection atomically.
    s.write(apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER))
    updated = s.read("SEL-SIRUELA-CTX-045")
    assert updated["status"] == STATUS_READY_FOR_EDITOR
    assert updated["candidate_id"] == original["candidate_id"]
    # No leftover temp files.
    assert list((Path(store) / "SEL-SIRUELA-CTX-045.json").parent.glob("*.tmp")) == []


def test_deterministic_json(evidence, store) -> None:
    s = SelectionStore(store)
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    s.write(sel)
    target = Path(store) / "SEL-SIRUELA-CTX-045.json"
    first = target.read_text(encoding="utf-8")
    s.write(sel)
    second = target.read_text(encoding="utf-8")
    assert first == second


# ---------------- role views ----------------

def test_producer_view_hides_internals(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    text = render_view("producer", sel)
    assert "Pruden" in text
    assert "problemas/dificultades" in text
    assert "09:14.125 → 09:20.225" in text
    assert "SIRUELA-CTX-045" not in text
    assert "4433" not in text and "media-rep" not in text


def test_director_view_hides_internals(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER, note="nota d")
    text = render_view("director", sel)
    assert "Editorial note: nota d" in text
    assert "SIRUELA-CTX-045" not in text
    assert "media-rep" not in text


def test_editor_view_includes_operational_details(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    text = render_view("editor", sel)
    assert "Video clip: A7IV_SL31277.MP4" in text
    assert "Source range: 09:14.125 → 09:20.225" in text
    assert "DaVinci reference status: NOT_REQUESTED" in text


def test_editor_view_audio_only_shows_unavailable(evidence) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-022", ROLE_PRODUCER)
    text = render_view("editor", sel)
    assert "Source range: UNMAPPED" in text
    assert "DaVinci reference status: UNAVAILABLE" in text
    assert "AUDIO_ONLY_VIDEO_UNMAPPED" in text
