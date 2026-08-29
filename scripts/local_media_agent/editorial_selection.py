"""CID EDITORIAL_SELECTION domain module.

Local collaboration contract for producer/director-driven editorial decisions.

Product principle:
    PRODUCER / DIRECTOR decide what should be edited.
    EDITOR executes the edit (in DaVinci).
    CID keeps the shared selection / status visible.

The EDITORIAL_SELECTION is the canonical editorial decision. DaVinci FCPXML
generation is a downstream EXECUTION ARTIFACT, not the canon. This module tracks
selection, status, role authorization and DaVinci-reference readiness only; it
never generates FCPXML and never reads or mutates source media.

All editorial fields are derived unchanged from the released producer-evidence
authority (see scripts/local_media_agent/producer_editorial_query.py). No
parallel evidence parser, no sync/timing recomputation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

FORMAT = "CID_PRODUCER_EDITORIAL_SELECTION"
VERSION = 1

ROLE_PRODUCER = "PRODUCER"
ROLE_DIRECTOR = "DIRECTOR"
ROLE_EDITOR = "EDITOR"
ROLES = (ROLE_PRODUCER, ROLE_DIRECTOR, ROLE_EDITOR)

STATUS_SELECTED = "SELECTED"
STATUS_READY_FOR_EDITOR = "READY_FOR_EDITOR"
STATUS_IN_EDIT = "IN_EDIT"
STATUS_USED = "USED"
STATUS_REJECTED = "REJECTED"
STATUSES = (
    STATUS_SELECTED,
    STATUS_READY_FOR_EDITOR,
    STATUS_IN_EDIT,
    STATUS_USED,
    STATUS_REJECTED,
)
TERMINAL_STATUSES = (STATUS_USED, STATUS_REJECTED)

DAVINCI_NOT_REQUESTED = "NOT_REQUESTED"
DAVINCI_READY = "READY"
DAVINCI_GENERATED = "GENERATED"
DAVINCI_UNAVAILABLE = "UNAVAILABLE"
DAVINCI_ERROR = "ERROR"
DAVINCI_REFERENCE_STATUSES = (
    DAVINCI_NOT_REQUESTED,
    DAVINCI_READY,
    DAVINCI_GENERATED,
    DAVINCI_UNAVAILABLE,
    DAVINCI_ERROR,
)

REASON_AUDIO_ONLY = "AUDIO_ONLY_VIDEO_UNMAPPED"

MAPPED = "MAPPED"
AUDIO_ONLY = "AUDIO_ONLY_VIDEO_UNMAPPED"

# (from_status, to_status) -> allowed actor roles.
LEGAL_TRANSITIONS: dict[tuple[str, str], tuple[str, ...]] = {
    (STATUS_SELECTED, STATUS_READY_FOR_EDITOR): (ROLE_PRODUCER, ROLE_DIRECTOR),
    (STATUS_SELECTED, STATUS_REJECTED): (ROLE_PRODUCER, ROLE_DIRECTOR),
    (STATUS_READY_FOR_EDITOR, STATUS_IN_EDIT): (ROLE_EDITOR,),
    (STATUS_READY_FOR_EDITOR, STATUS_REJECTED): (ROLE_EDITOR,),
    (STATUS_IN_EDIT, STATUS_USED): (ROLE_EDITOR,),
    (STATUS_IN_EDIT, STATUS_REJECTED): (ROLE_EDITOR,),
}


class SelectionError(ValueError):
    """Sanitized validation/domain failure for editorial selections."""


def selection_id_for(candidate_id: str) -> str:
    """Deterministic canonical selection id: SEL-<candidate_id>."""
    return f"SEL-{candidate_id}"


def _require(value: Any) -> Any:
    if value is None:
        raise SelectionError("INVALID_SELECTION_RECORD")
    return value


def create_selection(
    evidence_path: str | Path,
    candidate_id: str,
    requested_by_role: str,
    note: str | None = None,
) -> dict[str, Any]:
    """Create an EDITORIAL_SELECTION from released evidence authority.

    Uses released evidence-loading/model components only. MAPPED items keep the
    exact V2 relative source interval; AUDIO_ONLY items still produce a valid
    editorial selection with DaVinci marked UNAVAILABLE (editorial decision is
    separate from DaVinci execution capability).
    """
    if requested_by_role not in (ROLE_PRODUCER, ROLE_DIRECTOR):
        raise SelectionError("SELECTION_REQUESTED_BY_ROLE_INVALID")
    item = find_evidence_item(evidence_path, candidate_id)

    editorial_note = note if note is not None else item.editorial_note

    if item.excerpt_video_mapping_status == MAPPED:
        video_clip = item.video_clip
        source_in = item.excerpt_video_relative_start
        source_out = item.excerpt_video_relative_end
        dstatus = DAVINCI_NOT_REQUESTED
        dreason = None
    else:
        video_clip = None
        source_in = None
        source_out = None
        dstatus = DAVINCI_UNAVAILABLE
        dreason = REASON_AUDIO_ONLY

    return {
        "format": FORMAT,
        "version": VERSION,
        "selection_id": selection_id_for(candidate_id),
        "candidate_id": _require(item.candidate_id),
        "subject": _require(item.interview_subject),
        "topic": _require(item.topic),
        "excerpt": _require(item.producer_context_excerpt),
        "editorial_note": editorial_note,
        "video_clip": video_clip,
        "source_in_seconds": source_in,
        "source_out_seconds": source_out,
        "requested_by_role": requested_by_role,
        "status": STATUS_SELECTED,
        "davinci_reference_status": dstatus,
        "davinci_reference_path": None,
        "davinci_reference_reason": dreason,
        "editor_note": None,
    }


def find_evidence_item(
    evidence_path: str | Path,
    candidate_id: str,
):
    """Locate one released ProducerEvidenceItem by candidate_id (reuse, no re-parse).

    Uses the released ``load_evidence`` + ``query_producer_evidence`` projection
    so the returned item is the exact released model.
    """
    from scripts.local_media_agent.producer_editorial_query import (
        load_evidence,
        query_producer_evidence,
    )

    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise SelectionError("CANDIDATE_ID_REQUIRED")
    records = load_evidence(evidence_path)
    record = next(
        (r for r in records if r.get("candidate_id") == candidate_id),
        None,
    )
    if record is None:
        raise SelectionError("CANDIDATE_NOT_FOUND")
    topic = record.get("topic")
    if not isinstance(topic, str) or not topic.strip():
        raise SelectionError("EVIDENCE_ITEM_FIELDS_INVALID")
    # Query with a released-valid topic alias derived from the topic's first
    # segment (e.g. "problemas" for "problemas/dificultades"), so the released
    # projection is reused rather than re-parsing the evidence record.
    alias = topic.partition("/")[0]
    result = query_producer_evidence(evidence_path, alias)
    item = next((i for i in result.results if i.candidate_id == candidate_id), None)
    if item is None:
        raise SelectionError("CANDIDATE_NOT_FOUND")
    return item


def apply_transition(
    selection: dict[str, Any],
    to_status: str,
    actor_role: str,
    editor_note: str | None = None,
) -> dict[str, Any]:
    """Return a new selection after a legal, role-authorized transition.

    Raises SelectionError for terminal-state, illegal, or unauthorized moves.
    REJECTED requires a non-empty editor_note.
    """
    if to_status not in STATUSES:
        raise SelectionError("SELECTION_TARGET_STATUS_INVALID")
    if actor_role not in ROLES:
        raise SelectionError("SELECTION_ACTOR_ROLE_INVALID")

    current = selection.get("status")
    if current not in STATUSES:
        raise SelectionError("INVALID_SELECTION_RECORD")

    if current in TERMINAL_STATUSES:
        raise SelectionError("SELECTION_TERMINAL_STATUS")

    allowed_roles = LEGAL_TRANSITIONS.get((current, to_status))
    if allowed_roles is None:
        raise SelectionError("SELECTION_ILLEGAL_TRANSITION")
    if actor_role not in allowed_roles:
        raise SelectionError("SELECTION_ROLE_NOT_AUTHORIZED")

    updated = dict(selection)
    updated["status"] = to_status
    if to_status == STATUS_REJECTED:
        if not editor_note or not editor_note.strip():
            raise SelectionError("EDITOR_NOTE_REQUIRED_FOR_REJECTED")
        updated["editor_note"] = editor_note.strip()

    if to_status in TERMINAL_STATUSES and not editor_note:
        pass  # USED does not require a note.

    return updated


def human_range(source_in: float | None, source_out: float | None) -> str | None:
    """Render the relative source interval as MM:SS.mmm (no FCPXML fractions)."""
    if source_in is None or source_out is None:
        return None
    return f"{_n_range(source_in)} → {_n_range(source_out)}"


def _n_range(seconds: float) -> str:
    value = max(0.0, float(seconds))
    minutes = int(value // 60)
    secs = value - minutes * 60
    return f"{minutes:02d}:{secs:06.3f}"


def render_view(view: str, selection: dict[str, Any]) -> str:
    """Render a human-readable role view (no candidate_id / FCPXML internals)."""
    lines: list[str] = []
    lines.append(f"Subject: {selection.get('subject')}")
    lines.append(f"Topic: {selection.get('topic')}")
    lines.append("Excerpt:")
    lines.append(f"{selection.get('excerpt')}")
    if selection.get("editorial_note"):
        lines.append(f"Editorial note: {selection.get('editorial_note')}")
    source_rendered = human_range(
        selection.get("source_in_seconds"), selection.get("source_out_seconds")
    )
    if view == "editor":
        lines.append(f"Video clip: {selection.get('video_clip')}")
        lines.append(
            f"Source range: {source_rendered if source_rendered else 'UNMAPPED'}"
        )
        lines.append(f"Status: {selection.get('status')}")
        dstatus = selection.get("davinci_reference_status")
        if dstatus == DAVINCI_UNAVAILABLE:
            lines.append("DaVinci reference status: UNAVAILABLE")
            lines.append(f"Reason: {selection.get('davinci_reference_reason')}")
        else:
            lines.append(f"DaVinci reference status: {dstatus}")
    else:
        if selection.get("video_clip"):
            lines.append(f"Source clip: {selection.get('video_clip')}")
            lines.append(f"Source range: {source_rendered}")
        else:
            lines.append("Source clip: UNMAPPED (audio evidence)")
        lines.append(f"Status: {selection.get('status')}")
    if selection.get("editor_note"):
        lines.append(f"Editor note: {selection.get('editor_note')}")
    return "\n".join(lines) + "\n"


class SelectionStore:
    """Deterministic, atomic, local JSON-file selection store (no DB)."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def _path_for(self, selection_id: str) -> Path:
        if not isinstance(selection_id, str) or not selection_id.strip():
            raise SelectionError("SELECTION_ID_INVALID")
        return self.root / f"{selection_id}.json"

    def exists(self, selection_id: str) -> bool:
        return self._path_for(selection_id).is_file()

    def write(self, selection: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        target = self._path_for(_require(selection.get("selection_id")))
        payload = json.dumps(
            selection, ensure_ascii=False, sort_keys=True, indent=2
        )
        tmp = target.with_suffix(".json.tmp")
        tmp.write_text(payload + "\n", encoding="utf-8")
        os.replace(tmp, target)

    def read(self, selection_id: str) -> dict[str, Any]:
        target = self._path_for(selection_id)
        if not target.is_file():
            raise SelectionError("SELECTION_NOT_FOUND")
        try:
            value = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SelectionError("SELECTION_RECORD_INVALID") from exc
        if (
            not isinstance(value, dict)
            or _require(value.get("format")) != FORMAT
            or _require(value.get("selection_id")) != selection_id
        ):
            raise SelectionError("SELECTION_RECORD_INVALID")
        return value

    def list(
        self, status: str | None = None
    ) -> list[dict[str, Any]]:
        if not self.root.is_dir():
            return []
        selections: list[dict[str, Any]] = []
        for path in sorted(self.root.glob("SEL-*.json")):
            try:
                selection = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if status is not None and selection.get("status") != status:
                continue
            selections.append(selection)
        return selections


__all__ = [
    "FORMAT",
    "VERSION",
    "ROLE_PRODUCER",
    "ROLE_DIRECTOR",
    "ROLE_EDITOR",
    "ROLES",
    "STATUS_SELECTED",
    "STATUS_READY_FOR_EDITOR",
    "STATUS_IN_EDIT",
    "STATUS_USED",
    "STATUS_REJECTED",
    "STATUSES",
    "TERMINAL_STATUSES",
    "DAVINCI_NOT_REQUESTED",
    "DAVINCI_READY",
    "DAVINCI_GENERATED",
    "DAVINCI_UNAVAILABLE",
    "DAVINCI_ERROR",
    "DAVINCI_REFERENCE_STATUSES",
    "REASON_AUDIO_ONLY",
    "MAPPED",
    "AUDIO_ONLY",
    "LEGAL_TRANSITIONS",
    "SelectionError",
    "selection_id_for",
    "create_selection",
    "find_evidence_item",
    "apply_transition",
    "human_range",
    "render_view",
    "SelectionStore",
]
