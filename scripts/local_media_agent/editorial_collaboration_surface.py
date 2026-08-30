"""CID local operator surface for EDITORIAL_SELECTION (board).

Read-only, deterministic, local human-facing board for the PRODUCER /
DIRECTOR / EDITOR collaboration workflow. Canon is the EDITORIAL_SELECTION
store; this surface never mutates selections, never reads source media, never
talks to the network or a DB, and never launches DaVinci.

Role redaction is fully delegated to the released ``render_view`` projection
(called with the lowercase view name, matching the released contract). Every
board card is exactly that role-projected text plus a tiny safe DaVinci
readiness hint; no canonical/internal selection field leaks to a role whose
projection hides it. Output is either a concise terminal view or a
self-contained static HTML file (embedded CSS, no JS, no external assets).
"""

from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Any

from scripts.local_media_agent.editorial_selection import (
    DAVINCI_GENERATED,
    DAVINCI_NOT_REQUESTED,
    DAVINCI_UNAVAILABLE,
    STATUSES,
    ROLE_PRODUCER,
    ROLE_DIRECTOR,
    ROLE_EDITOR,
    SelectionStore,
    render_view,
)

ROLES = (ROLE_PRODUCER, ROLE_DIRECTOR, ROLE_EDITOR)
STATUS_ORDER = {status: idx for idx, status in enumerate(STATUSES)}
DAVINCI_ORDER = (DAVINCI_NOT_REQUESTED, DAVINCI_GENERATED, DAVINCI_UNAVAILABLE)
DAVINCI_COUNTS_KEYS = (DAVINCI_NOT_REQUESTED, DAVINCI_GENERATED, DAVINCI_UNAVAILABLE)

FORMAT_TERMINAL = "terminal"
FORMAT_HTML = "html"
FORMATS = (FORMAT_TERMINAL, FORMAT_HTML)


class SurfaceError(ValueError):
    """Controlled board-construction failure."""


class SurfaceInternalError(RuntimeError):
    """Unexpected board I/O/internal failure."""


def _validate_store_dir(store: str | Path) -> None:
    path = Path(store)
    if not path.exists():
        raise SurfaceError("BOARD_STORE_NOT_FOUND")
    if not path.is_dir():
        raise SurfaceError("BOARD_STORE_NOT_DIRECTORY")


def build_board_model(store: str | Path, role: str) -> dict[str, Any]:
    """Load and project a deterministic board model for one role.

    The uppercase canonical role is validated; the released ``render_view``
    projection is invoked with the lowercase view name. Canonical selections
    are used only for deterministic ordering and derived counts; human-facing
    items carry the exact released role projection plus a safe DaVinci
    readiness hint.
    """
    if role not in ROLES:
        raise SurfaceError("INVALID_BOARD_ROLE")
    _validate_store_dir(store)

    listings = SelectionStore(store)
    try:
        raw_entries = listings.list()
        canonical: list[dict[str, Any]] = []
        for entry in raw_entries:
            selection = listings.read(entry["selection_id"])
            render_view(role.lower(), selection)
            canonical.append(selection)
    except Exception as exc:
        raise SurfaceError("MALFORMED_SELECTION_RECORD") from exc

    canonical.sort(
        key=lambda s: (
            STATUS_ORDER.get(s.get("status"), len(STATUS_ORDER)),
            str(s.get("subject") or ""),
            str(s.get("topic") or ""),
            str(s.get("selection_id") or ""),
        )
    )

    status_counts: dict[str, int] = {status: 0 for status in STATUSES}
    davinci_counts: dict[str, int] = {
        DAVINCI_NOT_REQUESTED: 0,
        DAVINCI_GENERATED: 0,
        DAVINCI_UNAVAILABLE: 0,
    }
    for selection in canonical:
        status = selection.get("status")
        if status in status_counts:
            status_counts[status] += 1
        dstatus = selection.get("davinci_reference_status")
        if dstatus in davinci_counts:
            davinci_counts[dstatus] += 1

    items: list[dict[str, Any]] = []
    for selection in canonical:
        dstatus = selection.get("davinci_reference_status")
        davinci_status = (
            dstatus if dstatus in DAVINCI_COUNTS_KEYS else DAVINCI_NOT_REQUESTED
        )
        items.append(
            {
                "view_text": render_view(role.lower(), selection).rstrip("\n"),
                "davinci_status": davinci_status,
                "davinci_reason": (
                    selection.get("davinci_reference_reason")
                    if davinci_status == DAVINCI_UNAVAILABLE
                    else None
                ),
            }
        )

    return {
        "role": role,
        "total": len(canonical),
        "status_counts": status_counts,
        "davinci_counts": davinci_counts,
        "items": items,
    }


def render_terminal_board(model: dict[str, Any]) -> str:
    """Render the board as a concise, human-readable terminal view."""
    role = model["role"]
    status_counts = model["status_counts"]
    davinci_counts = model["davinci_counts"]

    lines: list[str] = []
    lines.append("CID EDITORIAL BOARD")
    lines.append("Role: " + str(role))
    lines.append("")
    lines.append("Total: " + str(model["total"]))
    lines.append(
        "Selected: {sd} | Ready: {rd} | In edit: {ie} | Used: {us} | Rejected: {rj}".format(
            sd=status_counts["SELECTED"],
            rd=status_counts["READY_FOR_EDITOR"],
            ie=status_counts["IN_EDIT"],
            us=status_counts["USED"],
            rj=status_counts["REJECTED"],
        )
    )
    dav_line = "DaVinci: " + " | ".join(
        str(name) + ": " + str(davinci_counts[name]) for name in DAVINCI_ORDER
    )
    lines.append(dav_line)
    lines.append("")

    is_editor = role == ROLE_EDITOR
    for index, item in enumerate(model["items"]):
        lines.append(item["view_text"])
        if not is_editor:
            if item["davinci_status"] == DAVINCI_UNAVAILABLE:
                lines.append("DaVinci: UNAVAILABLE")
                lines.append("Reason: " + str(item["davinci_reason"]))
            else:
                lines.append("DaVinci: " + str(item["davinci_status"]))
        if index != len(model["items"]) - 1:
            lines.append("")

    return "\n".join(lines) + "\n"


def render_html_board(model: dict[str, Any]) -> str:
    """Render the board as a self-contained static HTML5 document (no JS/network)."""
    role = model["role"]
    status_counts = model["status_counts"]
    davinci_counts = model["davinci_counts"]

    badge_rows = "".join(
        _badge(status, status_counts[status]) for status in STATUSES
    )
    dav_rows = "".join(
        _badge(name, davinci_counts.get(name, 0)) for name in DAVINCI_ORDER
    )

    is_editor = role == ROLE_EDITOR
    cards: list[str] = []
    for item in model["items"]:
        text = _esc(item["view_text"])
        extra = ""
        if not is_editor:
            if item["davinci_status"] == DAVINCI_UNAVAILABLE:
                extra = (
                    "\nDaVinci: UNAVAILABLE\nReason: " + _esc(item["davinci_reason"])
                )
            else:
                extra = "\nDaVinci: " + _esc(item["davinci_status"])
        cards.append('<div class="card">\n<pre>' + text + extra + "</pre>\n</div>")

    body = "\n".join(cards) if cards else '<p class="empty">No selections.</p>'

    document = (
        """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CID Editorial Board \u2014 {role}</title>
<style>
:root {{
  --bg: #f4f5f7;
  --card: #ffffff;
  --ink: #1f2430;
  --muted: #5b6472;
  --line: #e3e6ea;
  --accent: #2f6fed;
}}
* {{ box-sizing: border-box; }}
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
.badge.una {{ background:#fdecec; color:#b23b3b; }}
.badge.dn {{ background:#eaf3fb; color:#245c9c; }}
.total {{ font-weight:600; }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:14px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px; }}
.card pre {{ margin:0; font-size:13px; white-space:pre-wrap; word-wrap:break-word;
             font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
.empty {{ color:var(--muted); }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>CID Editorial Board</h1>
  <div class="role">Role: {role}</div>
</header>
<section class="summary">
  <div class="total">Total: {total}</div>
  <div class="badges">{badge_rows}</div>
  <div class="badges">{dav_rows}</div>
</section>
<section class="cards">
{body}
</section>
</div>
</body>
</html>
""".format(
            role=_esc(role),
            total=str(model["total"]),
            badge_rows=badge_rows,
            dav_rows=dav_rows,
            body=body,
        )
    )
    return document


def _badge(name: str, count: int) -> str:
    label = name.replace("_", " ")
    cls = ""
    if name == DAVINCI_UNAVAILABLE:
        cls = " una"
    elif name == DAVINCI_GENERATED:
        cls = " dn"
    return (
        '<span class="badge'
        + cls
        + '">'
        + _esc(label)
        + ": "
        + str(count)
        + "</span>"
    )


def _esc(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def write_html_board(model: dict[str, Any], output_path: str | Path) -> Path:
    """Write the self-contained HTML board deterministically (no silent overwrite)."""
    target = Path(output_path)
    if target.exists():
        raise SurfaceError("BOARD_OUTPUT_EXISTS")
    target.parent.mkdir(parents=True, exist_ok=True)
    content = render_html_board(model)
    tmp = target.with_name(target.name + ".tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, target)
    except OSError as exc:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        raise SurfaceInternalError("BOARD_WRITE_FAILED") from exc
    return target


__all__ = [
    "ROLES",
    "FORMATS",
    "FORMAT_TERMINAL",
    "FORMAT_HTML",
    "SurfaceError",
    "SurfaceInternalError",
    "build_board_model",
    "render_terminal_board",
    "render_html_board",
    "write_html_board",
]
