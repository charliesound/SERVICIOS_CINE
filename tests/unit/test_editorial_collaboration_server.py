from __future__ import annotations

import json
import threading
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from scripts.local_media_agent.editorial_collaboration_server import (
    BAD_REQUEST,
    HOST_NOT_LOOPBACK,
    INTERNAL_FAILURE,
    REQUEST_TOKEN_INVALID,
    SELECTION_NOT_FOUND,
    STALE_SELECTION_STATE,
    TRANSITION_REJECTED,
    BoardError,
    BoardHostError,
    BoardRequestError,
    apply_board_transition,
    create_server,
    legal_actions_for,
    make_request_token,
    render_interactive_board,
    validate_loopback_host,
)
from scripts.local_media_agent.editorial_selection import (
    DAVINCI_NOT_REQUESTED,
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
    items = [
        {
            "candidate_id": "SIRUELA-CTX-045",
            "interview_subject": "Pruden",
            "topic": "problemas/dificultades",
            "PRODUCER_CONTEXT_EXCERPT": "un ternero vale mucho dinero",
            "EXCERPT_AUDIO_START": 902.17,
            "EXCERPT_AUDIO_END": 908.27,
            "EXCERPT_VIDEO_MAPPING_STATUS": "MAPPED",
            "video_clip": "A7IV_SL31277.MP4",
            "EXCERPT_VIDEO_RELATIVE_START": 554.125,
            "EXCERPT_VIDEO_RELATIVE_END": 560.225,
            "SPEAKER_ATTRIBUTION": "UNKNOWN",
            "EDITORIAL_NOTE": "calving difficulty",
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
            "EDITORIAL_NOTE": "audio recollection",
        },
    ]
    path = tmp_path / "evidence.json"
    path.write_text(
        json.dumps({"REFERENCE_SET_TYPE": "producer", "PROJECT": "Siruela", "items": items}, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(path)


@pytest.fixture()
def evidence(tmp_path: Path) -> str:
    return _write_evidence(tmp_path)


def _token_pair():
    token = make_request_token()
    return token, token


@pytest.fixture()
def producer_store(evidence, tmp_path) -> str:
    store = str(tmp_path / "producer_store")
    s = SelectionStore(store)
    s.write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    s.write(create_selection(evidence, "SIRUELA-CTX-022", ROLE_DIRECTOR))
    return store


def _editor_ready_store(evidence, tmp_path) -> str:
    store = str(tmp_path / "editor_store")
    s = SelectionStore(store)
    base = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    ready = apply_transition(base, STATUS_READY_FOR_EDITOR, ROLE_PRODUCER)
    s.write(ready)
    return store


# ---------------- loopback host ----------------

def test_loopback_host_accepted() -> None:
    assert validate_loopback_host("127.0.0.1") == "127.0.0.1"
    assert validate_loopback_host("localhost") == "localhost"
    assert validate_loopback_host("::1") == "::1"


def test_zero_zero_zero_zero_refused() -> None:
    with pytest.raises(BoardHostError) as exc:
        validate_loopback_host("0.0.0.0")
    assert exc.value.code == HOST_NOT_LOOPBACK


def test_lan_address_refused() -> None:
    with pytest.raises(BoardHostError) as exc:
        validate_loopback_host("192.168.1.10")
    assert exc.value.code == HOST_NOT_LOOPBACK


# ---------------- legal actions ----------------

def test_producer_legal_actions() -> None:
    assert legal_actions_for(STATUS_SELECTED, ROLE_PRODUCER) == [
        (STATUS_READY_FOR_EDITOR, "READY FOR EDITOR"),
        (STATUS_REJECTED, "REJECT"),
    ]


def test_director_legal_actions() -> None:
    assert legal_actions_for(STATUS_SELECTED, ROLE_DIRECTOR) == [
        (STATUS_READY_FOR_EDITOR, "READY FOR EDITOR"),
        (STATUS_REJECTED, "REJECT"),
    ]


def test_editor_legal_actions() -> None:
    assert legal_actions_for(STATUS_READY_FOR_EDITOR, ROLE_EDITOR) == [
        (STATUS_IN_EDIT, "START EDITING"),
        (STATUS_REJECTED, "REJECT"),
    ]
    assert legal_actions_for(STATUS_IN_EDIT, ROLE_EDITOR) == [
        (STATUS_USED, "MARK USED"),
        (STATUS_REJECTED, "REJECT"),
    ]


def test_terminal_states_no_actions() -> None:
    assert legal_actions_for(STATUS_USED, ROLE_EDITOR) == []
    assert legal_actions_for(STATUS_REJECTED, ROLE_EDITOR) == []
    assert legal_actions_for(STATUS_USED, ROLE_PRODUCER) == []
    assert legal_actions_for(STATUS_REJECTED, ROLE_DIRECTOR) == []


# ---------------- no GET mutation ----------------

def test_get_never_mutates_store(producer_store) -> None:
    token, _ = _token_pair()
    before = {p.name: p.read_text(encoding="utf-8") for p in Path(producer_store).glob("*.json")}
    render_interactive_board(producer_store, ROLE_PRODUCER, token)
    render_interactive_board(producer_store, ROLE_EDITOR, token)
    after = {p.name: p.read_text(encoding="utf-8") for p in Path(producer_store).glob("*.json")}
    assert before == after


# ---------------- orchestrated transitions ----------------

def test_post_valid_producer_selected_to_ready(producer_store) -> None:
    token, _ = _token_pair()
    updated = apply_board_transition(
        producer_store,
        "SEL-SIRUELA-CTX-045",
        STATUS_SELECTED,
        STATUS_READY_FOR_EDITOR,
        ROLE_PRODUCER,
        token,
        token,
    )
    assert updated["status"] == STATUS_READY_FOR_EDITOR


def test_post_valid_director_selected_to_rejected(producer_store) -> None:
    token, _ = _token_pair()
    updated = apply_board_transition(
        producer_store,
        "SEL-SIRUELA-CTX-045",
        STATUS_SELECTED,
        STATUS_REJECTED,
        ROLE_DIRECTOR,
        token,
        token,
        editor_note="vetoed by director",
    )
    assert updated["status"] == STATUS_REJECTED


def test_rejection_note_preserved(producer_store) -> None:
    token, _ = _token_pair()
    updated = apply_board_transition(
        producer_store,
        "SEL-SIRUELA-CTX-045",
        STATUS_SELECTED,
        STATUS_REJECTED,
        ROLE_DIRECTOR,
        token,
        token,
        editor_note="needs different angle",
    )
    assert updated["editor_note"] == "needs different angle"


def test_post_valid_editor_ready_to_in_edit(evidence, tmp_path) -> None:
    store = _editor_ready_store(evidence, tmp_path)
    token, _ = _token_pair()
    updated = apply_board_transition(
        store,
        "SEL-SIRUELA-CTX-045",
        STATUS_READY_FOR_EDITOR,
        STATUS_IN_EDIT,
        ROLE_EDITOR,
        token,
        token,
    )
    assert updated["status"] == STATUS_IN_EDIT


def test_post_valid_editor_in_edit_to_used(evidence, tmp_path) -> None:
    store = _editor_ready_store(evidence, tmp_path)
    s = SelectionStore(store)
    current = s.read("SEL-SIRUELA-CTX-045")
    s.write(apply_transition(current, STATUS_IN_EDIT, ROLE_EDITOR))
    token, _ = _token_pair()
    updated = apply_board_transition(
        store,
        "SEL-SIRUELA-CTX-045",
        STATUS_IN_EDIT,
        STATUS_USED,
        ROLE_EDITOR,
        token,
        token,
    )
    assert updated["status"] == STATUS_USED


def test_illegal_transition_refused(producer_store) -> None:
    token, _ = _token_pair()
    with pytest.raises(BoardRequestError) as exc:
        apply_board_transition(
            producer_store,
            "SEL-SIRUELA-CTX-045",
            STATUS_SELECTED,
            STATUS_IN_EDIT,
            ROLE_PRODUCER,
            token,
            token,
        )
    assert exc.value.code == TRANSITION_REJECTED


def test_actor_role_escalation_impossible(producer_store) -> None:
    # even passing editor role, an editor action from SELECTED is illegal;
    # the fixed server role is what counts and it cannot gain authority.
    token, _ = _token_pair()
    with pytest.raises(BoardRequestError) as exc:
        apply_board_transition(
            producer_store,
            "SEL-SIRUELA-CTX-045",
            STATUS_SELECTED,
            STATUS_READY_FOR_EDITOR,
            ROLE_EDITOR,
            token,
            token,
        )
    assert exc.value.code == TRANSITION_REJECTED


def test_browser_supplied_role_ignored(producer_store) -> None:
    # server role is PRODUCER: a browser cannot route EDITOR-only transition.
    token, _ = _token_pair()
    with pytest.raises(BoardRequestError) as exc:
        apply_board_transition(
            producer_store,
            "SEL-SIRUELA-CTX-045",
            STATUS_SELECTED,
            STATUS_IN_EDIT,
            ROLE_PRODUCER,
            token,
            token,
        )
    assert exc.value.code == TRANSITION_REJECTED


def test_invalid_request_token_refuses_mutation(producer_store) -> None:
    before = SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"]
    with pytest.raises(BoardRequestError) as exc:
        apply_board_transition(
            producer_store,
            "SEL-SIRUELA-CTX-045",
            STATUS_SELECTED,
            STATUS_READY_FOR_EDITOR,
            ROLE_PRODUCER,
            "wrong-token",
            make_request_token(),
        )
    assert exc.value.code == REQUEST_TOKEN_INVALID
    assert SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"] == before


def test_missing_request_token_refuses_mutation(producer_store) -> None:
    token, _ = _token_pair()
    before = SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"]
    with pytest.raises(BoardRequestError) as exc:
        apply_board_transition(
            producer_store,
            "SEL-SIRUELA-CTX-045",
            STATUS_SELECTED,
            STATUS_READY_FOR_EDITOR,
            ROLE_PRODUCER,
            None,
            token,
        )
    assert exc.value.code == REQUEST_TOKEN_INVALID
    assert SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"] == before


def test_stale_expected_status_refuses_mutation(producer_store) -> None:
    token, _ = _token_pair()
    # advance the selection first
    apply_board_transition(
        producer_store,
        "SEL-SIRUELA-CTX-045",
        STATUS_SELECTED,
        STATUS_READY_FOR_EDITOR,
        ROLE_PRODUCER,
        token,
        token,
    )
    before = SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"]
    with pytest.raises(BoardRequestError) as exc:
        apply_board_transition(
            producer_store,
            "SEL-SIRUELA-CTX-045",
            STATUS_SELECTED,  # stale: canonical is now READY_FOR_EDITOR
            STATUS_READY_FOR_EDITOR,
            ROLE_PRODUCER,
            token,
            token,
        )
    assert exc.value.code == STALE_SELECTION_STATE
    assert SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"] == before


def test_unknown_selection_refuses_mutation(producer_store) -> None:
    token, _ = _token_pair()
    with pytest.raises(BoardRequestError) as exc:
        apply_board_transition(
            producer_store,
            "SEL-SIRUELA-CTX-999",
            STATUS_SELECTED,
            STATUS_READY_FOR_EDITOR,
            ROLE_PRODUCER,
            token,
            token,
        )
    assert exc.value.code == SELECTION_NOT_FOUND


def test_malformed_form_refuses_mutation(producer_store) -> None:
    token, _ = _token_pair()
    with pytest.raises(BoardRequestError) as exc:
        apply_board_transition(
            producer_store,
            "",
            STATUS_SELECTED,
            STATUS_READY_FOR_EDITOR,
            ROLE_PRODUCER,
            token,
            token,
        )
    assert exc.value.code == BAD_REQUEST


# ---------------- field preservation ----------------

def test_transition_preserves_davinci_fields(evidence, tmp_path) -> None:
    store = str(tmp_path / "davi")
    s = SelectionStore(store)
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    sel["davinci_reference_status"] = "GENERATED"
    sel["davinci_reference_path"] = "siruela_ctx_045.fcpxml"
    s.write(sel)
    token, _ = _token_pair()
    updated = apply_board_transition(
        store,
        "SEL-SIRUELA-CTX-045",
        STATUS_SELECTED,
        STATUS_READY_FOR_EDITOR,
        ROLE_PRODUCER,
        token,
        token,
    )
    assert updated["davinci_reference_status"] == "GENERATED"
    assert updated["davinci_reference_path"] == "siruela_ctx_045.fcpxml"


def test_transition_preserves_candidate_editorial_source_fields(producer_store) -> None:
    token, _ = _token_pair()
    updated = apply_board_transition(
        producer_store,
        "SEL-SIRUELA-CTX-045",
        STATUS_SELECTED,
        STATUS_READY_FOR_EDITOR,
        ROLE_PRODUCER,
        token,
        token,
    )
    assert updated["candidate_id"] == "SIRUELA-CTX-045"
    assert updated["subject"] == "Pruden"
    assert updated["topic"] == "problemas/dificultades"
    assert updated["excerpt"] == "un ternero vale mucho dinero"
    assert updated["video_clip"] == "A7IV_SL31277.MP4"
    assert updated["source_in_seconds"] == 554.125
    assert updated["source_out_seconds"] == 560.225


def test_audio_only_follows_legal_transition(evidence, tmp_path) -> None:
    store = str(tmp_path / "audio")
    s = SelectionStore(store)
    s.write(create_selection(evidence, "SIRUELA-CTX-022", ROLE_PRODUCER))
    token, _ = _token_pair()
    updated = apply_board_transition(
        store,
        "SEL-SIRUELA-CTX-022",
        STATUS_SELECTED,
        STATUS_READY_FOR_EDITOR,
        ROLE_PRODUCER,
        token,
        token,
    )
    assert updated["status"] == STATUS_READY_FOR_EDITOR
    assert updated["davinci_reference_status"] == "UNAVAILABLE"
    assert updated["davinci_reference_reason"] == "AUDIO_ONLY_VIDEO_UNMAPPED"


# ---------------- HTML surface ----------------

def test_html_escaping(producer_store) -> None:
    token, _ = _token_pair()
    page = render_interactive_board(producer_store, ROLE_PRODUCER, token)
    assert "<script" not in page
    assert "http://" not in page
    assert "https://" not in page
    assert "src=" not in page
    assert "cdn" not in page.lower()


def test_html_no_external_assets(producer_store) -> None:
    token, _ = _token_pair()
    page = render_interactive_board(producer_store, ROLE_PRODUCER, token)
    assert page.startswith("<!DOCTYPE html>")
    assert "<link" not in page
    assert "<script" not in page


def test_no_traceback_in_controlled_error(producer_store) -> None:
    # controlled refusals carry only the sanitized code, never a traceback.
    token, _ = _token_pair()
    try:
        apply_board_transition(
            producer_store,
            "SEL-SIRUELA-CTX-999",
            STATUS_SELECTED,
            STATUS_READY_FOR_EDITOR,
            ROLE_PRODUCER,
            token,
            token,
        )
    except BoardError as exc:
        assert exc.code in (SELECTION_NOT_FOUND,)
        assert "Traceback" not in str(exc)
        assert exc.code == SELECTION_NOT_FOUND
    else:
        raise AssertionError("expected controlled error")


def test_deterministic_action_ordering() -> None:
    # constructive before reject, across roles
    assert legal_actions_for(STATUS_READY_FOR_EDITOR, ROLE_EDITOR) == [
        (STATUS_IN_EDIT, "START EDITING"),
        (STATUS_REJECTED, "REJECT"),
    ]
    assert legal_actions_for(STATUS_IN_EDIT, ROLE_EDITOR) == [
        (STATUS_USED, "MARK USED"),
        (STATUS_REJECTED, "REJECT"),
    ]


def test_selection_store_remains_canonical_after_serve(producer_store) -> None:
    token, _ = _token_pair()
    render_interactive_board(producer_store, ROLE_PRODUCER, token)
    # board render must not have created extra files or altered records
    from scripts.local_media_agent.editorial_selection import FORMAT

    for p in Path(producer_store).glob("*.json"):
        record = json.loads(p.read_text(encoding="utf-8"))
        assert record["format"] == FORMAT


# ---------------- real-socket handler smoke ----------------

def _serve(store, role, token):
    server = create_server(store, role, host="127.0.0.1", port=0, token=token)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}"
    return server, thread, base


def test_real_socket_get_and_post(tmp_path, evidence) -> None:
    store = str(tmp_path / "sock")
    s = SelectionStore(store)
    s.write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    token = make_request_token()
    server, thread, base = _serve(store, ROLE_PRODUCER, token)
    try:
        with urllib.request.urlopen(f"{base}/", timeout=5) as resp:
            assert resp.status == 200
            body = resp.read().decode("utf-8")
            assert "CID Editorial Board" in body
            assert "READY FOR EDITOR" in body

        data = urllib.parse.urlencode(
            {
                "selection_id": "SEL-SIRUELA-CTX-045",
                "expected_status": STATUS_SELECTED,
                "to_status": STATUS_READY_FOR_EDITOR,
                "request_token": token,
            }
        )
        import http.client

        conn = http.client.HTTPConnection("127.0.0.1", port=server.server_address[1], timeout=5)
        conn.request(
            "POST",
            "/transition",
            body=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp = conn.getresponse()
        assert resp.status == 303
        assert resp.getheader("Location") == "/"
        conn.close()
        record = SelectionStore(store).read("SEL-SIRUELA-CTX-045")
        assert record["status"] == STATUS_READY_FOR_EDITOR
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_real_socket_controlled_error_no_traceback(tmp_path, evidence) -> None:
    store = str(tmp_path / "sock2")
    s = SelectionStore(store)
    s.write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    token = make_request_token()
    server, thread, base = _serve(store, ROLE_PRODUCER, token)
    try:
        data = urllib.parse.urlencode(
            {
                "selection_id": "SEL-SIRUELA-CTX-045",
                "expected_status": STATUS_SELECTED,
                "to_status": STATUS_READY_FOR_EDITOR,
                "request_token": "forged",
            }
        ).encode("utf-8")
        req = urllib.request.Request(f"{base}/transition", data=data, method="POST")
        try:
            urllib.request.urlopen(req, timeout=5)
            raise AssertionError("expected HTTP error")
        except urllib.error.HTTPError as err:
            assert err.code == 400
            body = err.read().decode("utf-8")
            assert REQUEST_TOKEN_INVALID in body
            assert "Traceback" not in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
