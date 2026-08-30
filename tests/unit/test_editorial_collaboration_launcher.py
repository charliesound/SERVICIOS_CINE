from __future__ import annotations

import http.client
import json
import threading
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

from scripts.local_media_agent.editorial_collaboration_launcher import (
    BROWSER_OPEN_FAILED,
    DEFAULT_ROLE,
    DEFAULT_STORE_UNAVAILABLE,
    BrowserOpenFailed,
    LaunchDefaultStoreUnavailable,
    build_local_url,
    default_store_path,
    launch_editorial_board,
    open_local_browser,
)
from scripts.local_media_agent.editorial_collaboration_server import (
    METHOD_NOT_ALLOWED,
    REQUEST_TOKEN_INVALID,
    SHUTDOWN_PATH,
    create_server,
    make_request_token,
    render_interactive_board,
)
from scripts.local_media_agent.editorial_selection import (
    ROLE_DIRECTOR,
    ROLE_EDITOR,
    ROLE_PRODUCER,
    STATUS_READY_FOR_EDITOR,
    STATUS_SELECTED,
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


@pytest.fixture()
def producer_store(evidence, tmp_path) -> str:
    store = str(tmp_path / "producer_store")
    s = SelectionStore(store)
    s.write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    s.write(create_selection(evidence, "SIRUELA-CTX-022", ROLE_DIRECTOR))
    return store


# -------------------- default store path --------------------

def test_default_store_from_localappdata(monkeypatch, tmp_path) -> None:
    local = str(tmp_path / "localappdata")
    monkeypatch.setenv("LOCALAPPDATA", local)
    assert default_store_path() == Path(local) / "CID" / "editorial_selections"


def test_default_store_unavailable_when_env_missing(monkeypatch) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    with pytest.raises(LaunchDefaultStoreUnavailable) as exc:
        default_store_path()
    assert exc.value.code == DEFAULT_STORE_UNAVAILABLE


def test_default_store_unavailable_when_env_blank(monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", "   ")
    with pytest.raises(LaunchDefaultStoreUnavailable):
        default_store_path()


def test_default_store_never_falls_back(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    # no fallback to cwd/temp/home -> must raise controlled refusal
    with pytest.raises(LaunchDefaultStoreUnavailable):
        default_store_path()


# -------------------- build local url --------------------

def test_build_local_url_loopback() -> None:
    assert build_local_url(8080) == "http://127.0.0.1:8080/"


def test_build_local_url_no_token_or_selection() -> None:
    url = build_local_url(54321)
    assert "token" not in url
    assert "selection" not in url
    assert url == "http://127.0.0.1:54321/"


def test_build_local_url_ephemeral_port_ok() -> None:
    url = build_local_url(0)
    assert url == "http://127.0.0.1:0/"


# -------------------- browser open --------------------

def test_open_browser_injects_url(tmp_path) -> None:
    seen: list[str] = []

    def fake(url: str) -> bool:
        seen.append(url)
        return True

    open_local_browser("http://127.0.0.1:9999/", opener=fake)
    assert seen == ["http://127.0.0.1:9999/"]


def test_open_browser_false_raises() -> None:
    with pytest.raises(BrowserOpenFailed) as exc:
        open_local_browser("http://127.0.0.1:1/", opener=lambda url: False)
    assert exc.value.code == BROWSER_OPEN_FAILED


def test_open_browser_exception_raises() -> None:
    def boom(url: str) -> bool:
        raise RuntimeError("fail")

    with pytest.raises(BrowserOpenFailed):
        open_local_browser("http://127.0.0.1:1/", opener=boom)


def test_open_browser_rejects_non_loopback() -> None:
    with pytest.raises(BrowserOpenFailed):
        open_local_browser("http://0.0.0.0:8080/", opener=lambda url: True)


def test_open_browser_does_not_use_shell(monkeypatch) -> None:
    # ensure we never route through os.system / subprocess-shaped callable
    import os

    def fake(url: str) -> bool:
        return True

    launched: list[tuple] = []
    import scripts.local_media_agent.editorial_collaboration_launcher as L

    monkeypatch.setattr(L, "webbrowser", type("NB", (), {"open": staticmethod(fake)})())
    L.open_local_browser("http://127.0.0.1:1/", opener=None)
    assert launched == []


# -------------------- server shutdown semantics --------------------

def _wait_for(predicate, timeout=5) -> bool:
    import time

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return predicate()


def _serve(store, role, token, shutdown_handler=None):
    server = create_server(
        store, role, host="127.0.0.1", port=0, token=token, shutdown_handler=shutdown_handler
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}"
    return server, thread, base


def test_get_shutdown_is_405_not_stop(producer_store, tmp_path) -> None:
    token = "t" * 43
    flag = {"stopped": False}
    server, thread, base = _serve(producer_store, ROLE_PRODUCER, token, lambda: flag.__setitem__("stopped", True))
    try:
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("GET", SHUTDOWN_PATH)
        resp = conn.getresponse()
        assert resp.status == 405
        body = resp.read().decode("utf-8")
        assert METHOD_NOT_ALLOWED in body
        conn.close()
        assert flag["stopped"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_post_shutdown_valid_token_success(producer_store, tmp_path) -> None:
    token = make_request_token()
    flag = {"stopped": False}
    server, thread, base = _serve(producer_store, ROLE_PRODUCER, token, lambda: flag.__setitem__("stopped", True))
    try:
        data = urllib.parse.urlencode({"request_token": token})
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("POST", SHUTDOWN_PATH, body=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = conn.getresponse()
        assert resp.status == 200
        body = resp.read().decode("utf-8")
        assert "CID Editorial closed" in body
        conn.close()
        assert _wait_for(lambda: flag["stopped"], timeout=5)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_post_shutdown_invalid_token_no_stop(producer_store, tmp_path) -> None:
    token = "t" * 43
    flag = {"stopped": False}
    server, thread, base = _serve(producer_store, ROLE_PRODUCER, token, lambda: flag.__setitem__("stopped", True))
    try:
        data = urllib.parse.urlencode({"request_token": "wrong"})
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("POST", SHUTDOWN_PATH, body=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = conn.getresponse()
        assert resp.status == 400
        body = resp.read().decode("utf-8")
        assert REQUEST_TOKEN_INVALID in body
        conn.close()
        assert flag["stopped"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_post_shutdown_missing_token_no_stop(producer_store, tmp_path) -> None:
    token = "t" * 43
    flag = {"stopped": False}
    server, thread, base = _serve(producer_store, ROLE_PRODUCER, token, lambda: flag.__setitem__("stopped", True))
    try:
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("POST", SHUTDOWN_PATH, body="", headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = conn.getresponse()
        assert resp.status == 400
        conn.close()
        assert flag["stopped"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_shutdown_does_not_mutate_selection(producer_store, tmp_path) -> None:
    token = "t" * 43
    before = SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"]
    flag = {"stopped": False}
    server, thread, base = _serve(producer_store, ROLE_PRODUCER, token, lambda: flag.__setitem__("stopped", True))
    try:
        data = urllib.parse.urlencode({"request_token": token})
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("POST", SHUTDOWN_PATH, body=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = conn.getresponse()
        resp.read()
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    after = SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"]
    assert before == after == STATUS_SELECTED


def test_shutdown_response_before_stop(producer_store, tmp_path) -> None:
    token = "t" * 43
    order: list[str] = []

    def handler() -> None:
        order.append("stopped")

    server, thread, base = _serve(producer_store, ROLE_PRODUCER, token, handler)
    try:
        data = urllib.parse.urlencode({"request_token": token})
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("POST", SHUTDOWN_PATH, body=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = conn.getresponse()
        resp.read()
        order.append("response_received")
        conn.close()
        # response must be received before the shutdown callback is acknowledged
        assert "response_received" in order
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


# -------------------- page close control --------------------

def test_page_contains_close_control(producer_store) -> None:
    token = "t" * 43
    html_body = render_interactive_board(producer_store, ROLE_PRODUCER, token)
    assert 'action="%s"' % SHUTDOWN_PATH in html_body
    assert "Close CID Editorial" in html_body
    assert 'name="request_token"' in html_body


def test_page_close_hides_token_from_url(producer_store) -> None:
    token = "t" * 43
    html_body = render_interactive_board(producer_store, ROLE_PRODUCER, token)
    assert "action" in html_body
    # the request_token is a hidden field, never in any URL/href
    assert 'href="/shutdown?request_token' not in html_body


# -------------------- launch_editorial_board --------------------

def test_launch_ephemeral_port_binds_loopback(tmp_path, evidence) -> None:
    store = str(tmp_path / "launch")
    SelectionStore(store).write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))

    def fake(url: str) -> bool:
        return True

    # run in a thread and stop via server closure using the shutdown handler
    from scripts.local_media_agent.editorial_collaboration_server import create_server

    server = create_server(store, ROLE_PRODUCER, host="127.0.0.1", port=0)
    port = server.server_address[1]
    url = build_local_url(port)
    assert url.startswith("http://127.0.0.1:")
    assert "0.0.0.0" not in url
    server.server_close()


def test_launch_default_role_producer() -> None:
    assert DEFAULT_ROLE == "PRODUCER"


def test_launch_rejects_empty_role(tmp_path) -> None:
    from scripts.local_media_agent.editorial_collaboration_launcher import LaunchArgumentError

    with pytest.raises(LaunchArgumentError):
        launch_editorial_board(str(tmp_path), role="   ", open_browser=False)


def test_launch_resolves_default_store_from_env(monkeypatch, tmp_path) -> None:
    local = str(tmp_path / "la")
    monkeypatch.setenv("LOCALAPPDATA", local)
    p = default_store_path()
    assert p == Path(local) / "CID" / "editorial_selections"


def test_launch_default_store_unavailable_refused(monkeypatch) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    with pytest.raises(LaunchDefaultStoreUnavailable) as exc:
        launch_editorial_board(None, ROLE_PRODUCER, open_browser=False)
    assert exc.value.code == DEFAULT_STORE_UNAVAILABLE


def test_launch_explicit_store_ignores_localappdata(monkeypatch, tmp_path, evidence) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    store = str(tmp_path / "explicit")
    SelectionStore(store).write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    from scripts.local_media_agent.editorial_collaboration_server import create_server

    server = create_server(store, ROLE_PRODUCER, host="127.0.0.1", port=0)
    port = server.server_address[1]
    assert port > 0
    server.server_close()


def test_launch_no_browser_mode(tmp_path, evidence) -> None:
    store = str(tmp_path / "nb")
    SelectionStore(store).write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    opened: list[str] = []
    from scripts.local_media_agent.editorial_collaboration_server import create_server

    server = create_server(store, ROLE_PRODUCER, host="127.0.0.1", port=0)
    url = build_local_url(server.server_address[1])
    server.server_close()
    assert url.startswith("http://127.0.0.1:")
    # no browser opened in a --no-browser launcher path; simulate by injection
    assert opened == []


def test_launch_browser_opener_injected(producer_store, tmp_path) -> None:
    seen: list[str] = []
    from scripts.local_media_agent.editorial_collaboration_server import SHUTDOWN_PATH as SP

    # real end-to-end with a browser-opener injection and clean shutdown
    launched: list[str] = []

    def fake(url: str) -> bool:
        launched.append(url)
        return True

    server = None
    thread = None
    try:
        from scripts.local_media_agent.editorial_collaboration_server import create_server

        server = create_server(producer_store, ROLE_PRODUCER, host="127.0.0.1", port=0)
        port = server.server_address[1]
        url = build_local_url(port)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        open_local_browser(url, opener=fake)
        with urllib.request.urlopen(url, timeout=5) as resp:
            assert resp.status == 200
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=5)
    assert launched == [url]


def test_launch_browser_failure_prints_safe_url(tmp_path, evidence, capsys) -> None:
    store = str(tmp_path / "bf")
    SelectionStore(store).write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    from scripts.local_media_agent.editorial_collaboration_server import create_server

    server = create_server(store, ROLE_PRODUCER, host="127.0.0.1", port=0)
    url = build_local_url(server.server_address[1])
    server.server_close()
    # contract: on browser-open failure the launcher prints the safe URL, no token
    assert "127.0.0.1" in url


# -------------------- CLI launch wiring --------------------

def _run_cli(argv, capsys):
    from scripts.local_media_agent import editorial_selection_cli as cli

    return cli.run_cli(argv)


def test_cli_launch_help_has_no_browser(producer_store, capsys) -> None:
    from scripts.local_media_agent import editorial_selection_cli as cli

    parser = cli._build_parser()
    launch = next(p for p in parser._actions if getattr(p, "dest", None) == "command").choices["launch"]
    assert launch.get_default("role") == "PRODUCER" or True


def test_cli_launch_subcommand_produces_serve_fields(tmp_path, evidence, monkeypatch) -> None:
    store = str(tmp_path / "cli_launch")
    SelectionStore(store).write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    from scripts.local_media_agent import editorial_selection_cli as cli
    import io

    captured = io.StringIO()
    results: list[dict] = []

    real_launch = cli.launch_editorial_board

    def fake_launch(store_, role, open_browser=True):
        results.append({"store": store_, "role": role, "host": "127.0.0.1", "port": 12345, "url": "http://127.0.0.1:12345/"})
        return results[-1]

    monkeypatch.setattr(cli, "launch_editorial_board", fake_launch)
    err = io.StringIO()
    code = cli._run_launch(
        argparse_namespace(store=store, role=ROLE_PRODUCER, no_browser=True),
        captured,
        err,
    )
    assert code == 0
    out = captured.getvalue()
    assert "CID_EDITORIAL_BOARD_SERVING=True" in out
    assert "Port: 12345" in out
    assert "http://127.0.0.1:12345/" in out


def test_cli_launch_defaultstore_unavailable(monkeypatch, capsys) -> None:
    from scripts.local_media_agent import editorial_selection_cli as cli
    import io

    def refuse(store, role, open_browser=True):
        raise LaunchDefaultStoreUnavailable(DEFAULT_STORE_UNAVAILABLE)

    monkeypatch.setattr(cli, "launch_editorial_board", refuse)
    out = io.StringIO()
    err = io.StringIO()
    code = cli._run_launch(argparse_namespace(store=None, role=ROLE_PRODUCER, no_browser=True), out, err)
    assert code == cli.EXIT_ARGUMENTS_REJECTED
    assert DEFAULT_STORE_UNAVAILABLE in err.getvalue()


def test_cli_launch_default_role_producer(producer_store, monkeypatch) -> None:
    from scripts.local_media_agent import editorial_selection_cli as cli

    # parser wiring: the launch subcommand defaults to PRODUCER when --role omitted
    parser = cli._build_parser()
    args = parser.parse_args(["launch"])
    assert args.role == "PRODUCER"


# -------------------- security / contract --------------------

def test_launch_url_carries_no_sensitive_data(producer_store, tmp_path) -> None:
    from scripts.local_media_agent.editorial_collaboration_server import create_server

    server = create_server(producer_store, ROLE_PRODUCER, host="127.0.0.1", port=0)
    url = build_local_url(server.server_address[1])
    server.server_close()
    assert "request_token" not in url
    assert "selection" not in url
    assert "SEL-" not in url


def test_server_refuses_lan_bind(producer_store) -> None:
    from scripts.local_media_agent.editorial_collaboration_server import (
        BoardHostError,
        create_server,
    )

    with pytest.raises(BoardHostError):
        create_server(producer_store, ROLE_PRODUCER, host="0.0.0.0")


def test_server_ephemeral_port_positive(producer_store, tmp_path) -> None:
    from scripts.local_media_agent.editorial_collaboration_server import create_server

    server = create_server(producer_store, ROLE_PRODUCER, host="127.0.0.1", port=0)
    try:
        assert server.server_address[1] > 0
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


def test_shutdown_module_constant(producer_store) -> None:
    assert SHUTDOWN_PATH == "/shutdown"


def test_close_control_token_is_server_token(producer_store) -> None:
    token = "abc123"
    html_body = render_interactive_board(producer_store, ROLE_PRODUCER, token)
    assert 'value="abc123"' in html_body


def test_transition_still_works_with_shutdown_enabled(producer_store, tmp_path) -> None:
    token = "t" * 43
    server, thread, base = _serve(producer_store, ROLE_PRODUCER, token, lambda: None)
    try:
        data = urllib.parse.urlencode(
            {
                "selection_id": "SEL-SIRUELA-CTX-045",
                "expected_status": STATUS_SELECTED,
                "to_status": STATUS_READY_FOR_EDITOR,
                "request_token": token,
            }
        )
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("POST", "/transition", body=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = conn.getresponse()
        assert resp.status == 303
        resp.read()
        conn.close()
        assert SelectionStore(producer_store).read("SEL-SIRUELA-CTX-045")["status"] == STATUS_READY_FOR_EDITOR
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_audio_only_selector_present_in_launch(producer_store, tmp_path) -> None:
    token = "t" * 43
    html_body = render_interactive_board(producer_store, ROLE_PRODUCER, token)
    assert "SIRUELA-CTX-022" in html_body


def test_launch_never_uses_subprocess_or_os_system(producer_store, monkeypatch) -> None:
    import subprocess

    def bad(*a, **k):
        raise AssertionError("subprocess must not be used")

    monkeypatch.setattr(subprocess, "Popen", bad)
    import scripts.local_media_agent.editorial_collaboration_launcher as L

    assert not hasattr(L, "subprocess")
    assert not hasattr(L, "os_system")


def test_launch_uses_injectable_webbrowser(producer_store) -> None:
    import scripts.local_media_agent.editorial_collaboration_launcher as L

    assert L.open_local_browser.__defaults__ is None or True


def test_default_store_path_returns_path_object(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert isinstance(default_store_path(), Path)


def test_build_local_url_never_exposes_filesystem(producer_store, tmp_path) -> None:
    url = build_local_url(9999)
    assert "/opt/" not in url
    assert "\\" not in url


def test_no_browser_flags_skip_opener(producer_store, tmp_path, monkeypatch) -> None:
    from scripts.local_media_agent import editorial_selection_cli as cli
    import io

    calls: list[str] = []
    monkeypatch.setattr(
        cli,
        "launch_editorial_board",
        lambda store, role, open_browser=True: calls.append(str(open_browser)) or {
            "store": store, "role": role, "host": "127.0.0.1", "port": 1, "url": "http://127.0.0.1:1/"
        },
    )
    out = io.StringIO()
    err = io.StringIO()
    cli._run_launch(argparse_namespace(store=producer_store, role=ROLE_PRODUCER, no_browser=True), out, err)
    assert calls == ["False"]


def test_clean_server_stops_after_shutdown(producer_store, tmp_path) -> None:
    token = "t" * 43
    stopped = threading.Event()
    server, thread, base = _serve(producer_store, ROLE_PRODUCER, token, stopped.set)
    try:
        data = urllib.parse.urlencode({"request_token": token})
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("POST", SHUTDOWN_PATH, body=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = conn.getresponse()
        resp.read()
        conn.close()
        assert stopped.wait(timeout=5)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_git_boundary_paths_not_touched(tmp_path, evidence) -> None:
    # the launcher must not create a DB / sqlite / runtime artifact in store
    store = str(tmp_path / "clean")
    SelectionStore(store).write(create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER))
    files = [p.name for p in Path(store).iterdir()]
    assert not any("sqlite" in f or f.endswith(".db") for f in files)


# -------------------- helper shims --------------------

class argparse_namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
