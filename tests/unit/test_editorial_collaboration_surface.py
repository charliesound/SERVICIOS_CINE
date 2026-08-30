from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.local_media_agent.editorial_collaboration_surface import (
    FORMAT_HTML,
    SurfaceError,
    SurfaceInternalError,
    build_board_model,
    render_html_board,
    render_terminal_board,
    write_html_board,
)
from scripts.local_media_agent.editorial_selection import (
    DAVINCI_GENERATED,
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
    SelectionStore,
    apply_transition,
    create_selection,
)


def _write_evidence(tmp_path: Path) -> str:
    rows = [
        {
            "cid": "SIRUELA-CTX-400",
            "subject": "Zebra-A",
            "topic": "problemas/dificultades",
            "excerpt": "mapped zeta zebra",
            "mapped": True,
            "note": "note-400",
        },
        {
            "cid": "SIRUELA-CTX-401",
            "subject": "Alpha-1",
            "topic": "problemas/dificultades",
            "excerpt": "mapped alpha one",
            "mapped": True,
            "note": "note-401",
        },
        {
            "cid": "SIRUELA-CTX-402",
            "subject": "Alpha-2",
            "topic": "ovejas/ovino",
            "excerpt": "mapped alpha two",
            "mapped": True,
            "note": "note-402",
        },
        {
            "cid": "SIRUELA-CTX-403",
            "subject": "Mango",
            "topic": "campo",
            "excerpt": "mapped beta mango",
            "mapped": True,
            "note": "note-403",
        },
        {
            "cid": "SIRUELA-CTX-404",
            "subject": "Lima",
            "topic": "campo",
            "excerpt": "mapped beta lima",
            "mapped": True,
            "note": "note-404",
        },
        {
            "cid": "SIRUELA-CTX-405",
            "subject": "Roc & <script>alert(1)</script>",
            "topic": "ganado/ganadería",
            "excerpt": "mapped escape & stuff",
            "mapped": True,
            "note": "note-405",
        },
        {
            "cid": "SIRUELA-CTX-022",
            "subject": "Pruden",
            "topic": "ovejas/ovino",
            "excerpt": "el rebaño por la mañana",
            "mapped": False,
            "note": "audio-only",
        },
    ]
    items = []
    for r in rows:
        items.append(
            {
                "candidate_id": r["cid"],
                "interview_subject": r["subject"],
                "topic": r["topic"],
                "PRODUCER_CONTEXT_EXCERPT": r["excerpt"],
                "EXCERPT_AUDIO_START": 10.0,
                "EXCERPT_AUDIO_END": 12.0,
                "EXCERPT_VIDEO_MAPPING_STATUS": (
                    "MAPPED" if r["mapped"] else "AUDIO_ONLY_VIDEO_UNMAPPED"
                ),
                "video_clip": "A7IV_SL31277.MP4" if r["mapped"] else None,
                "EXCERPT_VIDEO_RELATIVE_START": 554.125 if r["mapped"] else None,
                "EXCERPT_VIDEO_RELATIVE_END": 560.225 if r["mapped"] else None,
                "SPEAKER_ATTRIBUTION": "UNKNOWN",
                "EDITORIAL_NOTE": r["note"],
            }
        )
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


def _store_with_statuses(
    evidence: str, store_path: str, *, make_generated: bool = True
) -> SelectionStore:
    """Build a temp store covering SELECTED/READY/IN_EDIT/USED/REJECTED + audio-only."""
    s = SelectionStore(store_path)

    def base(cid: str, role: str = ROLE_PRODUCER):
        return create_selection(evidence, cid, role)

    sel = base("SIRUELA-CTX-400")  # SELECTED
    s.write(sel)

    ready = apply_transition(base("SIRUELA-CTX-401"), STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)
    if make_generated:
        ready["davinci_reference_status"] = DAVINCI_GENERATED
    s.write(ready)

    in_edit = apply_transition(
        apply_transition(base("SIRUELA-CTX-402"), STATUS_READY_FOR_EDITOR, ROLE_PRODUCER),
        STATUS_IN_EDIT,
        ROLE_EDITOR,
    )
    s.write(in_edit)

    used = apply_transition(
        apply_transition(apply_transition(base("SIRUELA-CTX-403"), STATUS_READY_FOR_EDITOR, ROLE_PRODUCER), STATUS_IN_EDIT, ROLE_EDITOR),
        STATUS_USED,
        ROLE_EDITOR,
    )
    s.write(used)

    rejected = apply_transition(
        apply_transition(apply_transition(base("SIRUELA-CTX-404"), STATUS_READY_FOR_EDITOR, ROLE_PRODUCER), STATUS_IN_EDIT, ROLE_EDITOR),
        STATUS_REJECTED,
        ROLE_EDITOR,
        editor_note="rejected note",
    )
    s.write(rejected)

    escape = base("SIRUELA-CTX-405")
    if make_generated:
        escape["davinci_reference_status"] = DAVINCI_GENERATED
    s.write(escape)

    audio = base("SIRUELA-CTX-022")
    s.write(audio)

    return s


# ---------------- deterministic ordering ----------------

def _exact_status_store(evidence: str) -> str:
    import tempfile
    store_path = tempfile.mkdtemp(prefix="board-status-")
    s = SelectionStore(store_path)

    def base(cid: str, role: str = ROLE_PRODUCER):
        return create_selection(evidence, cid, role)

    s.write(base("SIRUELA-CTX-400"))  # SELECTED
    s.write(
        apply_transition(base("SIRUELA-CTX-401"), STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)
    )
    s.write(
        apply_transition(
            apply_transition(base("SIRUELA-CTX-402"), STATUS_READY_FOR_EDITOR, ROLE_PRODUCER),
            STATUS_IN_EDIT,
            ROLE_EDITOR,
        )
    )
    s.write(
        apply_transition(
            apply_transition(
                apply_transition(base("SIRUELA-CTX-403"), STATUS_READY_FOR_EDITOR, ROLE_PRODUCER),
                STATUS_IN_EDIT,
                ROLE_EDITOR,
            ),
            STATUS_USED,
            ROLE_EDITOR,
        )
    )
    s.write(
        apply_transition(
            apply_transition(
                apply_transition(base("SIRUELA-CTX-404"), STATUS_READY_FOR_EDITOR, ROLE_PRODUCER),
                STATUS_IN_EDIT,
                ROLE_EDITOR,
            ),
            STATUS_REJECTED,
            ROLE_EDITOR,
            editor_note="rejected note",
        )
    )
    return store_path


def test_deterministic_status_ordering(evidence, tmp_path) -> None:
    store_path = _exact_status_store(evidence)
    model = build_board_model(store_path, ROLE_PRODUCER)
    texts = [it["view_text"] for it in model["items"]]

    def status_of(text: str) -> str:
        for line in text.splitlines():
            if line.startswith("Status: "):
                return line.split("Status: ", 1)[1]
        raise AssertionError("status not in view_text")

    got = [status_of(t) for t in texts]
    assert got == [STATUS_SELECTED, STATUS_READY_FOR_EDITOR, STATUS_IN_EDIT, STATUS_USED, STATUS_REJECTED]


def test_statuses_secondary_order_within_group(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "s3")
    s = SelectionStore(store_path)
    b = create_selection(evidence, "SIRUELA-CTX-401", ROLE_PRODUCER)
    a = create_selection(evidence, "SIRUELA-CTX-403", ROLE_PRODUCER)
    # same status, subjects Alpha-1 vs Mango; insertion order 403 then 401
    s.write(a)
    s.write(b)
    model = build_board_model(store_path, ROLE_PRODUCER)
    subjects = [
        t["view_text"].splitlines()[0].replace("Subject: ", "") for t in model["items"]
    ]
    assert subjects == ["Alpha-1", "Mango"]


# ---------------- counts ----------------

def test_all_five_workflow_counts(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "c1"))
    model = build_board_model(str(tmp_path / "c1"), ROLE_PRODUCER)
    sc = model["status_counts"]
    # store holds 7 records: SELECTED (400, 405, 022), READY (401), IN_EDIT (402),
    # USED (403), REJECTED (404)
    assert sc == {
        STATUS_SELECTED: 3,
        STATUS_READY_FOR_EDITOR: 1,
        STATUS_IN_EDIT: 1,
        STATUS_USED: 1,
        STATUS_REJECTED: 1,
    }


def test_all_three_davinci_counts(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "c2"))
    model = build_board_model(str(tmp_path / "c2"), ROLE_PRODUCER)
    dc = model["davinci_counts"]
    # 400 SELECTED: NOT_REQUESTED; 401 GENERATED; 402 IN_EDIT: NOT_REQUESTED;
    # 403 USED: NOT_REQUESTED; 404 REJECTED: NOT_REQUESTED; 405 GENERATED; 022 UNAVAILABLE
    assert dc[DAVINCI_GENERATED] == 2
    assert dc[DAVINCI_UNAVAILABLE] == 1
    assert dc[DAVINCI_NOT_REQUESTED] == 4


# ---------------- role projection ----------------

def test_producer_projection_redaction(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "p1"))
    model = build_board_model(str(tmp_path / "p1"), ROLE_PRODUCER)
    for item in model["items"]:
        vt = item["view_text"]
        assert "DaVinci reference status" not in vt
        assert "Video clip:" not in vt
        # app-level davinci augmentation is present on the item model
        assert item["davinci_status"] in (DAVINCI_NOT_REQUESTED, DAVINCI_GENERATED, DAVINCI_UNAVAILABLE)


def test_director_projection_redaction(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "d1"))
    model = build_board_model(str(tmp_path / "d1"), ROLE_DIRECTOR)
    for item in model["items"]:
        vt = item["view_text"]
        assert "DaVinci reference status" not in vt
        assert "Video clip:" not in vt


def test_editor_operational_projection(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "e1"))
    model = build_board_model(str(tmp_path / "e1"), ROLE_EDITOR)
    for item in model["items"]:
        vt = item["view_text"]
        assert "Video clip: " in vt
        assert "Source range: " in vt
        assert "Status: " in vt


def test_editor_includes_davinci_status(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "e2"))
    model = build_board_model(str(tmp_path / "e2"), ROLE_EDITOR)
    assert any("DaVinci reference status" in it["view_text"] for it in model["items"])


# ---------------- davinci rendering ----------------

def test_generated_mapped_entry(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "g1"))
    model = build_board_model(str(tmp_path / "g1"), ROLE_PRODUCER)
    gen = [it for it in model["items"] if it["davinci_status"] == DAVINCI_GENERATED]
    assert gen, "expected at least one GENERATED mapped entry"
    term = render_terminal_board(model)
    assert term.count("DaVinci: GENERATED") >= 1


def test_unavailable_audio_only_entry(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "u1"))
    model = build_board_model(str(tmp_path / "u1"), ROLE_PRODUCER)
    una = [it for it in model["items"] if it["davinci_status"] == DAVINCI_UNAVAILABLE]
    assert len(una) == 1
    assert una[0]["davinci_reason"] == REASON_AUDIO_ONLY
    term = render_terminal_board(model)
    assert "DaVinci: UNAVAILABLE" in term
    assert REASON_AUDIO_ONLY in term


def test_each_workflow_state_present(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "w1"))
    model = build_board_model(str(tmp_path / "w1"), ROLE_EDITOR)
    texts = "".join(it["view_text"] for it in model["items"])
    for status in (STATUS_SELECTED, STATUS_READY_FOR_EDITOR, STATUS_IN_EDIT, STATUS_USED, STATUS_REJECTED):
        assert f"Status: {status}" in texts


# ---------------- deterministic rendering ----------------

def test_deterministic_terminal_output(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "t1"))
    a = render_terminal_board(build_board_model(str(tmp_path / "t1"), ROLE_PRODUCER))
    b = render_terminal_board(build_board_model(str(tmp_path / "t1"), ROLE_PRODUCER))
    assert a == b


def test_deterministic_html_bytes(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "t2")
    _store_with_statuses(evidence, store_path)
    a = render_html_board(build_board_model(store_path, ROLE_DIRECTOR))
    b = render_html_board(build_board_model(store_path, ROLE_DIRECTOR))
    assert a == b


def test_html_escaping(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "h1"))
    html_doc = render_html_board(build_board_model(str(tmp_path / "h1"), ROLE_PRODUCER))
    assert "<script>" not in html_doc
    assert "&lt;script&gt;" in html_doc
    assert "&amp;" in html_doc


def test_html_self_contained_no_external(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "h2"))
    html_doc = render_html_board(build_board_model(str(tmp_path / "h2"), ROLE_PRODUCER))
    assert "http://" not in html_doc
    assert "https://" not in html_doc
    assert "<script" not in html_doc
    assert "<link" not in html_doc
    assert "{/cdn" not in html_doc
    assert "src=" not in html_doc.replace("class", "class")  # no external assets


def test_html_valid_doctype_and_role(evidence, tmp_path) -> None:
    _store_with_statuses(evidence, str(tmp_path / "h3"))
    html_doc = render_html_board(build_board_model(str(tmp_path / "h3"), ROLE_DIRECTOR))
    assert html_doc.startswith("<!DOCTYPE html>")
    assert 'Role: DIRECTOR' in html_doc
    assert "CID Editorial Board" in html_doc


# ---------------- empty / refusal ----------------

def test_empty_existing_store(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "empty")
    SelectionStore(store_path).write(
        create_selection(evidence, "SIRUELA-CTX-400", ROLE_PRODUCER)
    )
    # clear all files to simulate real empty store dir
    for f in Path(store_path).glob("*.json"):
        f.unlink()
    model = build_board_model(store_path, ROLE_PRODUCER)
    assert model["total"] == 0
    assert model["items"] == []
    term = render_terminal_board(model)
    assert "Total: 0" in term


def test_nonexistent_store_refusal(evidence, tmp_path) -> None:
    with pytest.raises(SurfaceError):
        build_board_model(str(tmp_path / "missing"), ROLE_PRODUCER)


def test_store_path_not_directory(evidence, tmp_path) -> None:
    p = tmp_path / "afile"
    p.write_text("x", encoding="utf-8")
    with pytest.raises(SurfaceError):
        build_board_model(str(p), ROLE_PRODUCER)


def test_invalid_role(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "ir")
    SelectionStore(store_path).write(create_selection(evidence, "SIRUELA-CTX-400", ROLE_PRODUCER))
    with pytest.raises(SurfaceError):
        build_board_model(store_path, "ADMIN")


def test_malformed_record(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "mr")
    SelectionStore(store_path).write(create_selection(evidence, "SIRUELA-CTX-400", ROLE_PRODUCER))
    bad = Path(store_path) / "SEL-SIRUELA-CTX-999.json"
    bad.write_text(
        json.dumps({"selection_id": "SIRUELA-CTX-999", "subject": "x"}),
        encoding="utf-8",
    )
    with pytest.raises(SurfaceError):
        build_board_model(store_path, ROLE_PRODUCER)


# ---------------- no mutation ----------------

def test_board_generation_does_not_mutate_store(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "nm1")
    _store_with_statuses(evidence, store_path)
    before = {p.name: p.read_text(encoding="utf-8") for p in Path(store_path).glob("*.json")}
    build_board_model(store_path, ROLE_PRODUCER)
    build_board_model(store_path, ROLE_DIRECTOR)
    build_board_model(store_path, ROLE_EDITOR)
    after = {p.name: p.read_text(encoding="utf-8") for p in Path(store_path).glob("*.json")}
    assert before == after


def test_html_write_does_not_mutate_store(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "nm2")
    _store_with_statuses(evidence, store_path)
    before = {p.name: p.read_text(encoding="utf-8") for p in Path(store_path).glob("*.json")}
    model = build_board_model(store_path, ROLE_DIRECTOR)
    out = tmp_path / "nm2" / "board.html"
    write_html_board(model, out)
    after = {p.name: p.read_text(encoding="utf-8") for p in Path(store_path).glob("*.json")}
    assert before == after
    assert out.exists()


def test_html_write_refuses_existing(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "nm3")
    _store_with_statuses(evidence, store_path)
    model = build_board_model(store_path, ROLE_DIRECTOR)
    out = tmp_path / "nm3" / "board.html"
    out.write_text("existing", encoding="utf-8")
    with pytest.raises(SurfaceError):
        write_html_board(model, out)


def test_terminal_header(evidence, tmp_path) -> None:
    store_path = str(tmp_path / "th")
    SelectionStore(store_path).write(create_selection(evidence, "SIRUELA-CTX-400", ROLE_PRODUCER))
    term = render_terminal_board(build_board_model(store_path, ROLE_PRODUCER))
    assert term.startswith("CID EDITORIAL BOARD\n")
    assert "Role: PRODUCER" in term
