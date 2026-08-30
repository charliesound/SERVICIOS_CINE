"""CID local interactive operator surface for EDITORIAL_SELECTION (serve).

Local-only read/write HTTP operator board. The canonical selection store and
the released transition engine (EDITORIAL_SELECTION) remain authoritative; the
browser/server layer only validates a request, reads the canonical selection,
applies an already-legal ``apply_transition``, writes atomically, and re-renders.

Security contract: bind to loopback only, no outbound HTTP, no DB, no SaaS, no
source-media reads, no DaVinci launch, stdlib HTTP server only. Mutation forms
carry a per-process unpredictable request token (stdlib ``secrets``) for local
CSRF / request-integrity protection; POST can never override the fixed server
role, and stale forms (expected status mismatch) are refused without mutation.
"""

from __future__ import annotations

import html
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from scripts.local_media_agent.editorial_collaboration_surface import (
    ROLES,
    SurfaceError,
    build_board_model,
)
from scripts.local_media_agent.editorial_selection import (
    LEGAL_TRANSITIONS,
    ROLE_EDITOR,
    ROLE_PRODUCER,
    ROLE_DIRECTOR,
    STATUS_IN_EDIT,
    STATUS_READY_FOR_EDITOR,
    STATUS_REJECTED,
    STATUS_SELECTED,
    STATUS_USED,
    SelectionError,
    SelectionStore,
    apply_transition,
    render_view,
)

ALLOWED_HOSTS = ("127.0.0.1", "localhost", "::1")
DEFAULT_PORT = 8765

HOST_NOT_LOOPBACK = "CID_EDITORIAL_BOARD_HOST_NOT_LOOPBACK"
REQUEST_TOKEN_INVALID = "CID_EDITORIAL_BOARD_REQUEST_TOKEN_INVALID"
STALE_SELECTION_STATE = "CID_EDITORIAL_BOARD_STALE_SELECTION_STATE"
SELECTION_NOT_FOUND = "CID_EDITORIAL_BOARD_SELECTION_NOT_FOUND"
TRANSITION_REJECTED = "CID_EDITORIAL_BOARD_TRANSITION_REJECTED"
BAD_REQUEST = "CID_EDITORIAL_BOARD_BAD_REQUEST"
INTERNAL_FAILURE = "CID_EDITORIAL_BOARD_INTERNAL_FAILURE"
METHOD_NOT_ALLOWED = "CID_EDITORIAL_BOARD_METHOD_NOT_ALLOWED"
SHUTDOWN_PATH = "/shutdown"

# Deterministic target-status ordering (constructive action before reject).
_TARGET_PRIORITY = (
    STATUS_READY_FOR_EDITOR,
    STATUS_IN_EDIT,
    STATUS_USED,
    STATUS_REJECTED,
)
_HUMAN_LABELS = {
    STATUS_READY_FOR_EDITOR: "READY FOR EDITOR",
    STATUS_IN_EDIT: "START EDITING",
    STATUS_USED: "MARK USED",
    STATUS_REJECTED: "REJECT",
}
_REQUIRES_NOTE = {STATUS_REJECTED}


class BoardError(Exception):
    """Base for controlled board failures."""


class BoardRequestError(BoardError):
    """Controlled refusal carrying a sanitized CID_ code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class BoardHostError(BoardError):
    """Controlled refusal for a non-loopback bind host."""

    def __init__(self, host: str) -> None:
        super().__init__(HOST_NOT_LOOPBACK)
        self.host = host
        self.code = HOST_NOT_LOOPBACK


class BoardRequestTokenInvalid(BoardRequestError):
    pass


class BoardStaleSelection(BoardRequestError):
    pass


class BoardSelectionNotFound(BoardRequestError):
    pass


class BoardTransitionRejected(BoardRequestError):
    pass


class BoardBadRequest(BoardRequestError):
    pass


class BoardInternalError(BoardError):
    """Unexpected internal failure (sanitized to a generic 500)."""


def validate_loopback_host(host: str) -> str:
    """Return the normalized host only for a safe loopback address."""
    if not isinstance(host, str) or not host.strip():
        raise BoardHostError(host)
    normalized = host.strip().lower()
    if normalized not in ALLOWED_HOSTS:
        raise BoardHostError(normalized)
    return normalized


def legal_actions_for(status: str, role: str) -> list[tuple[str, str]]:
    """Deterministic legal (target_status, human_label) actions for a status/role."""
    actions: list[tuple[str, str]] = []
    for target in _TARGET_PRIORITY:
        allowed = LEGAL_TRANSITIONS.get((status, target), ())
        if role in allowed:
            actions.append((target, _HUMAN_LABELS[target]))
    return actions


def make_request_token() -> str:
    """Return one unpredictable per-process request token (no URL, no logging)."""
    return secrets.token_urlsafe(32)


def _canonical_key(selection: dict[str, Any]) -> tuple:
    from scripts.local_media_agent.editorial_selection import STATUSES

    order = {s: i for i, s in enumerate(STATUSES)}
    return (
        order.get(selection.get("status"), len(STATUSES)),
        str(selection.get("subject") or ""),
        str(selection.get("topic") or ""),
        str(selection.get("selection_id") or ""),
    )


def _project_items(store: str | Path, role: str) -> list[dict[str, Any]]:
    listings = SelectionStore(store)
    try:
        selections = listings.list()
        parsed = [listings.read(raw["selection_id"]) for raw in selections]
    except Exception as exc:
        raise BoardRequestError("CID_EDITORIAL_BOARD_BAD_REQUEST") from exc
    parsed.sort(key=_canonical_key)
    items: list[dict[str, Any]] = []
    for selection in parsed:
        dstatus = selection.get("davinci_reference_status")
        items.append(
            {
                "selection_id": selection.get("selection_id"),
                "status": selection.get("status"),
                "view_text": render_view(role.lower(), selection).rstrip("\n"),
                "davinci_status": dstatus,
            }
        )
    return items


def apply_board_transition(
    store: str | Path,
    selection_id: str,
    expected_status: str,
    to_status: str,
    actor_role: str,
    request_token: str | None,
    server_token: str | None,
    editor_note: str | None = None,
) -> dict[str, Any]:
    """Validate and apply one canonical transition (no store mutation on refusal).

    Order: token integrity -> selection existence -> stale guard -> canonical
    transition -> atomic write. Returns the updated canonical selection.
    """
    if actor_role not in ROLES:
        raise BoardRequestError(TRANSITION_REJECTED)
    if not isinstance(selection_id, str) or not selection_id.strip():
        raise BoardRequestError(BAD_REQUEST)
    if not isinstance(to_status, str) or not to_status.strip():
        raise BoardRequestError(BAD_REQUEST)
    if not isinstance(expected_status, str):
        raise BoardRequestError(BAD_REQUEST)

    provided = "" if request_token is None else request_token
    expected = "" if server_token is None else server_token
    if not secrets.compare_digest(provided, expected) or not server_token:
        raise BoardRequestTokenInvalid(REQUEST_TOKEN_INVALID)

    listings = SelectionStore(store)
    try:
        current = listings.read(selection_id)
    except SelectionError as exc:
        raise BoardSelectionNotFound(SELECTION_NOT_FOUND) from exc

    if current.get("status") != expected_status:
        raise BoardStaleSelection(STALE_SELECTION_STATE)

    try:
        updated = apply_transition(
            current,
            to_status,
            actor_role,
            editor_note=editor_note,
        )
    except SelectionError as exc:
        raise BoardTransitionRejected(TRANSITION_REJECTED) from exc

    listings.write(updated)
    return updated


def render_interactive_board(
    store: str | Path,
    role: str,
    token: str,
    *,
    actions_for=legal_actions_for,
) -> str:
    """Render a self-contained interactive HTML board for one fixed role."""
    model = build_board_model(store, role)
    items = _project_items(store, role)

    for item in items:
        item["actions"] = actions_for(item["status"], role)

    status_counts = model["status_counts"]
    davinci_counts = model["davinci_counts"]

    summary = "".join(
        _badge(status, status_counts[status])
        for status in (STATUS_SELECTED, STATUS_READY_FOR_EDITOR, STATUS_IN_EDIT, STATUS_USED, STATUS_REJECTED)
    )
    dav_summary = "".join(
        f'<span class="badge">{_esc(k)}: {v}</span>'
        for k, v in davinci_counts.items()
    )

    cards = "".join(_render_card(item, role, token) for item in items)
    if not items:
        cards = '<p class="empty">No selections.</p>'

    document = (
        """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CID Editorial Board \u2014 {role}</title>
<style>
:root {{
  --bg:#f4f5f7; --card:#ffffff; --ink:#1f2430; --muted:#5b6472;
  --line:#e3e6ea; --accent:#2f6fed; --danger:#b23b3b;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
       font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }}
.wrap {{ max-width:980px; margin:0 auto; padding:24px 16px; }}
header h1 {{ font-size:22px; margin:0 0 4px; }}
header .role {{ color:var(--accent); font-weight:600; }}
.summary {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
            padding:16px; margin:16px 0; }}
.badges {{ display:flex; flex-wrap:wrap; gap:8px; margin:8px 0; }}
.badge {{ display:inline-block; padding:4px 10px; border-radius:999px;
          background:#eef1f6; color:#334; font-size:13px; }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:14px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px; }}
.card pre {{ margin:0 0 10px; font-size:13px; white-space:pre-wrap; word-wrap:break-word;
             font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
.card .status {{ font-weight:600; margin-bottom:8px; }}
.actions {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }}
.actions form {{ margin:0; }}
button {{ cursor:pointer; border:1px solid var(--line); background:#eef1f6;
          border-radius:8px; padding:6px 12px; font-size:13px; }}
button.reject {{ background:#fdecec; color:var(--danger); border-color:#f3cfcf; }}
button.primary {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
.note-field {{ display:block; margin-top:4px; }}
.empty {{ color:var(--muted); }}
.role-tag {{ display:inline-block; padding:2px 8px; border-radius:999px;
             background:#eaf3fb; color:#245c9c; font-size:12px; }}
.close {{ margin-top:32px; padding-top:16px; border-top:1px solid var(--line); }}
.close form {{ margin:0 0 6px; }}
.close-btn {{ background:#1f2430; color:#fff; border-color:#1f2430; }}
.close-hint {{ margin:0; color:var(--muted); font-size:12px; }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>CID Editorial Board</h1>
  <div class="role">Role: {role} <span class="role-tag">local read/write operator surface</span></div>
</header>
<section class="summary">
  <div class="badges">{summary}</div>
  <div class="badges">{dav_summary}</div>
</section>
<section class="cards">
{cards}
</section>
<section class="close">
  <form method="post" action="{shutdown_path}">
    <input type="hidden" name="request_token" value="{token}">
    <button type="submit" class="close-btn">Close CID Editorial</button>
  </form>
  <p class="close-hint">This stops the local operator server and lets you close this tab.</p>
</section>
</div>
</body>
</html>
""".format(
            role=_esc(role),
            summary=summary,
            dav_summary=dav_summary,
            cards=cards,
            shutdown_path=_esc(SHUTDOWN_PATH),
            token=_esc(token),
        )
    )
    return document


def _render_card(item: dict[str, Any], role: str, token: str) -> str:
    note = _esc(item.get("view_text") or "")
    status = _esc(item.get("status") or "")
    selection_id = _esc(item.get("selection_id") or "")
    raw_id = item.get("selection_id") or ""
    actions = item.get("actions") or []

    status_html = f'<div class="status">Status: {status}</div>'
    actions_html = ""
    if actions:
        parts: list[str] = []
        for target, label in actions:
            requires_note = target in _REQUIRES_NOTE
            button_cls = "reject" if target == STATUS_REJECTED else "primary"
            field = (
                f'<input class="note-field" type="text" name="editor_note" '
                f'placeholder="Reject reason (required)" required>'
                if requires_note
                else ""
            )
            parts.append(
                f'<form method="post" action="/transition">'
                f'<input type="hidden" name="selection_id" value="{selection_id}">'
                f'<input type="hidden" name="expected_status" value="{status}">'
                f'<input type="hidden" name="to_status" value="{_esc(target)}">'
                f'<input type="hidden" name="request_token" value="{_esc(token)}">'
                f'{field}'
                f'<button type="submit" class="{button_cls}">{_esc(label)}</button>'
                f"</form>"
            )
        actions_html = f'<div class="actions">{"".join(parts)}</div>'
    return (
        f'<div class="card">{status_html}<pre>{note}</pre>{actions_html}</div>'
    )


def _badge(name: str, count: int) -> str:
    return f'<span class="badge">{_esc(name.replace("_", " "))}: {count}</span>'


def _esc(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _make_handler(
    store: str | Path,
    role: str,
    token: str,
    close: callable | None = None,
) -> type[BaseHTTPRequestHandler]:
    class EditorialBoardHandler(BaseHTTPRequestHandler):
        server_version = "CIDEditorialBoard/1.0"

        def log_message(self, format: str, *args: Any) -> None:
            # keep server console quiet; do not log the request token.
            return

        def _send(self, status: int, body: str, headers: dict[str, str] | None = None) -> None:
            payload = body.encode("utf-8")
            self.send_response(status)
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:
            if self.path == SHUTDOWN_PATH:
                # Shutdown is POST-only by contract; a GET must not stop the server.
                self._send(405, _esc(METHOD_NOT_ALLOWED))
                return
            if self.path != "/":
                self._send(404, _esc("CID_EDITORIAL_BOARD_NOT_FOUND"))
                return
            try:
                board = render_interactive_board(store, role, token)
            except BoardError as exc:
                self._send(400, _esc(getattr(exc, "code", BAD_REQUEST)))
                return
            except SurfaceError:
                self._send(400, _esc(BAD_REQUEST))
                return
            except Exception:
                self._send(500, _esc(INTERNAL_FAILURE))
                return
            self._send(200, board)

        def _handle_shutdown(self) -> None:
            if close is None:
                self._send(500, _esc(INTERNAL_FAILURE))
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                self._send(400, _esc(BAD_REQUEST))
                return
            if length < 0 or length > 65536:
                self._send(400, _esc(BAD_REQUEST))
                return
            raw = self.rfile.read(length)
            try:
                fields = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
            except Exception:
                self._send(400, _esc(BAD_REQUEST))
                return
            values = fields.get("request_token")
            provided = "" if not values else values[0]
            if not secrets.compare_digest(provided, token) or not token:
                self._send(400, _esc(REQUEST_TOKEN_INVALID))
                return
            # Respond BEFORE stopping the server so the client receives the
            # confirmation; no selection state is touched on shutdown.
            self._send(
                200,
                "CID Editorial closed \u2014 safe to close this tab.",
            )
            close()

        def do_POST(self) -> None:
            if self.path == SHUTDOWN_PATH:
                self._handle_shutdown()
                return
            if self.path != "/transition":
                self._send(404, _esc("CID_EDITORIAL_BOARD_NOT_FOUND"))
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                self._send(400, _esc(BAD_REQUEST))
                return
            if length < 0 or length > 65536:
                self._send(400, _esc(BAD_REQUEST))
                return
            raw = self.rfile.read(length)
            try:
                fields = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
            except Exception:
                self._send(400, _esc(BAD_REQUEST))
                return

            def field(name: str) -> str | None:
                values = fields.get(name)
                if not values:
                    return None
                return values[0]

            selection_id = field("selection_id")
            expected_status = field("expected_status")
            to_status = field("to_status")
            editor_note = field("editor_note")
            request_token = field("request_token")
            if selection_id is None or expected_status is None or to_status is None or request_token is None:
                self._send(400, _esc(BAD_REQUEST))
                return

            try:
                apply_board_transition(
                    store,
                    selection_id,
                    expected_status,
                    to_status,
                    role,
                    request_token,
                    token,
                    editor_note=editor_note,
                )
            except BoardRequestTokenInvalid as exc:
                self._send(400, _esc(exc.code))
                return
            except BoardStaleSelection as exc:
                self._send(409, _esc(exc.code))
                return
            except BoardRequestError as exc:
                self._send(400, _esc(exc.code))
                return
            except Exception:
                self._send(500, _esc(INTERNAL_FAILURE))
                return

            self._send(
                303,
                "",
                headers={
                    "Location": "/",
                    "Content-Type": "text/plain; charset=utf-8",
                },
            )

        def do_PUT(self) -> None:
            self._send(405, _esc(METHOD_NOT_ALLOWED))

        def do_DELETE(self) -> None:
            self._send(405, _esc(METHOD_NOT_ALLOWED))

    return EditorialBoardHandler


def create_server(
    store: str | Path,
    role: str,
    host: str = "127.0.0.1",
    port: int = DEFAULT_PORT,
    token: str | None = None,
    shutdown_handler: callable | None = None,
) -> ThreadingHTTPServer:
    """Build a loopback-bound stdlib HTTP server; returns the live server object.

    ``shutdown_handler`` is an optional callable invoked (after the shutdown
    response has been sent) when a valid ``POST /shutdown`` is received. It is
    the launcher's responsibility to stop and join the server thread cleanly.
    """
    if role not in ROLES:
        raise BoardRequestError(TRANSITION_REJECTED)
    safe_host = validate_loopback_host(host)
    server_token = make_request_token() if token is None else token
    handler = _make_handler(store, role, server_token, shutdown_handler)
    server = ThreadingHTTPServer((safe_host, port), handler)
    return server


__all__ = [
    "ALLOWED_HOSTS",
    "DEFAULT_PORT",
    "HOST_NOT_LOOPBACK",
    "REQUEST_TOKEN_INVALID",
    "STALE_SELECTION_STATE",
    "SELECTION_NOT_FOUND",
    "TRANSITION_REJECTED",
    "BAD_REQUEST",
    "INTERNAL_FAILURE",
    "SHUTDOWN_PATH",
    "BoardError",
    "BoardHostError",
    "BoardRequestError",
    "BoardRequestTokenInvalid",
    "BoardStaleSelection",
    "BoardSelectionNotFound",
    "BoardTransitionRejected",
    "BoardBadRequest",
    "BoardInternalError",
    "validate_loopback_host",
    "legal_actions_for",
    "make_request_token",
    "apply_board_transition",
    "render_interactive_board",
    "create_server",
]
