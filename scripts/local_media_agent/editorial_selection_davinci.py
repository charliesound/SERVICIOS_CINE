"""CID DaVinci reference orchestration for EDITORIAL_SELECTION.

Bridges an approved EDITORIAL_SELECTION (status READY_FOR_EDITOR) to the
already-proven DaVinci FCPXML reference, tracking "reference prepared" without
collapsing the editorial status flow.

Product principle:
    PRODUCER / DIRECTOR decide and observe.
    EDITOR executes (in DaVinci).
    CID tracks both decision and execution readiness.

This slice only *prepares* the reference sidecar. It does NOT start editing:
the editor must explicitly transition READY_FOR_EDITOR -> IN_EDIT when actual
editing begins. It never reads source media, never launches Resolve, and never
mutates any project.

Canonical authority is the EDITORIAL_SELECTION itself. The released evidence /
handoff chain is reused to locate the candidate; the historical audio/video
timing contract (exact Decimal/Fraction) is preserved as released.
"""

from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from scripts.local_media_agent.davinci_marker_reference import (
    build_davinci_reference,
    ndf_timecode_to_seconds_exact,
)
from scripts.local_media_agent.editorial_selection import (
    DAVINCI_GENERATED,
    DAVINCI_UNAVAILABLE,
    REASON_AUDIO_ONLY,
    STATUS_READY_FOR_EDITOR,
    SelectionError,
    SelectionStore,
    find_evidence_item,
)
from scripts.local_media_agent.producer_editorial_query import (
    build_editor_handoff_package,
)
from scripts.local_media_agent.local_project import (
    LocalProjectError,
    load_active_project,
    project_selection_store_path,
)
from scripts.local_media_agent.project_video_profile import (
    ProjectVideoProfileError,
    profile_frame_duration_text,
    require_confirmed_project_video_profile,
)
from scripts.local_media_agent.source_video_profile import (
    SourceVideoProfileError,
    load_source_video_profiles,
    resolve_source_media_path,
    resolve_source_video_profile,
)

ERR_NOT_READY = "CID_DAVINCI_SELECTION_NOT_READY_FOR_EDITOR"
ERR_ALREADY_GENERATED = "CID_DAVINCI_REFERENCE_ALREADY_GENERATED"
ERR_UNAVAILABLE = "CID_DAVINCI_REFERENCE_UNAVAILABLE"
ERR_OUTPUT_EXISTS = "CID_DAVINCI_REFERENCE_OUTPUT_EXISTS"
ERR_EVIDENCE_MISMATCH = "CID_EDITORIAL_SELECTION_EVIDENCE_MISMATCH"
ERR_INTERNAL = "CID_EDITORIAL_DAVINCI_INTERNAL_FAILURE"


class EditorialDavinciError(RuntimeError):
    """Controlled product refusal (wrong state, audio-only, mismatch, etc.)."""


class EditorialDavinciInternalError(RuntimeError):
    """Controlled internal orchestration failure (unexpected, not a refusal)."""


def _decimal_equal(left: Any, right: Any) -> bool:
    """Exact Decimal equality; malformed values fail closed (no traceback)."""
    try:
        return Decimal(str(left)) == Decimal(str(right))
    except (InvalidOperation, ValueError, TypeError):
        return False


def prepare_davinci_reference_for_selection(
    *,
    store: str | Path,
    selection_id: str,
    evidence_path: str | Path,
    media_path: str,
    frame_duration: str,
    source_timecode_start: str,
    source_duration: str | float,
    source_frame_rate: str | None = None,
    output_path: str | Path,
) -> dict[str, Any]:
    """Prepare the DaVinci FCPXML reference for one approved selection.

    Returns a concise editor-facing result on success. Raises controlled
    ``EditorialDavinciError`` for every refusal/generation failure; the
    selection is never mutated unless FCPXML output was fully materialized.
    """
    selector = SelectionStore(store)
    selection = selector.read(selection_id)

    if selection.get("status") != STATUS_READY_FOR_EDITOR:
        raise EditorialDavinciError(ERR_NOT_READY)
    if selection.get("davinci_reference_status") == DAVINCI_GENERATED:
        raise EditorialDavinciError(ERR_ALREADY_GENERATED)
    if selection.get("davinci_reference_status") == DAVINCI_UNAVAILABLE:
        raise EditorialDavinciError(
            f"{ERR_UNAVAILABLE}:{selection.get('davinci_reference_reason')}"
        )

    item = find_evidence_item(evidence_path, selection["candidate_id"])
    package = build_editor_handoff_package(item)

    _verify_canonical_selection(selection, package)

    result = build_davinci_reference(
        package,
        media_path=media_path,
        frame_duration=frame_duration,
        source_timecode_start=source_timecode_start,
        source_duration=source_duration,
        source_frame_rate=source_frame_rate,
    )
    if not result.get("davinci_reference_available"):
        raise EditorialDavinciInternalError(ERR_INTERNAL)
    fcpxml_text = result["fcpxml_text"]

    try:
        _materialize_output(output_path, fcpxml_text)
    except OSError as exc:
        _cleanup_output(output_path)
        raise EditorialDavinciInternalError(ERR_INTERNAL) from exc

    updated = dict(selection)
    updated["davinci_reference_status"] = DAVINCI_GENERATED
    updated["davinci_reference_path"] = str(output_path)
    updated["davinci_reference_reason"] = None
    try:
        selector.write(updated)
    except Exception as exc:
        _cleanup_output(output_path)
        raise EditorialDavinciInternalError(ERR_INTERNAL) from exc

    return {
        "selection_id": selection["selection_id"],
        "subject": selection.get("subject"),
        "topic": selection.get("topic"),
        "editorial_note": selection.get("editorial_note"),
        "video_clip": selection.get("video_clip"),
        "source_in_seconds": selection.get("source_in_seconds"),
        "source_out_seconds": selection.get("source_out_seconds"),
        "status": updated["status"],
        "davinci_reference_status": updated["davinci_reference_status"],
        "davinci_reference_path": updated["davinci_reference_path"],
    }


def prepare_project_davinci_reference(
    *,
    selection_id: str,
    evidence_path: str | Path,
    active_media_root: str | Path | None,
    output_path: str | Path,
    local_appdata: str | Path | None = None,
) -> dict[str, Any]:
    """Prepare through active project, confirmed timeline, and source authorities."""
    try:
        project = load_active_project(local_appdata=local_appdata)
        project_id = project["project_id"]
        profile = require_confirmed_project_video_profile(
            project_id, local_appdata=local_appdata
        )
        store = project_selection_store_path(project_id, local_appdata)
        selection = SelectionStore(store).read(selection_id)
        catalog = load_source_video_profiles(project_id, local_appdata=local_appdata)
        source = resolve_source_video_profile(catalog, selection.get("video_clip"))
        media_path = resolve_source_media_path(
            active_media_root, source["source_media_ref"]
        )
        project_frame_duration = profile_frame_duration_text(profile)
        try:
            ndf_timecode_to_seconds_exact(
                source["source_timecode_start"], source["source_frame_rate"]
            )
        except ValueError as exc:
            raise SourceVideoProfileError(
                "CID_SOURCE_TIMECODE_RATE_UNSUPPORTED"
            ) from exc
    except (LocalProjectError, ProjectVideoProfileError, SourceVideoProfileError) as exc:
        raise EditorialDavinciError(exc.code) from exc

    return prepare_davinci_reference_for_selection(
        store=store,
        selection_id=selection_id,
        evidence_path=evidence_path,
        media_path=str(media_path),
        frame_duration=project_frame_duration,
        source_timecode_start=source["source_timecode_start"],
        source_duration=source["source_duration_raw"],
        source_frame_rate=source["source_frame_rate"],
        output_path=output_path,
    )


def _verify_canonical_selection(
    selection: dict[str, Any], package: dict[str, Any]
) -> None:
    """Verify the approved EDITORIAL_SELECTION matches the released handoff.

    The editorial selection is the canon. If evidence disagrees with it on the
    candidate / clip / source interval, refuse before generating anything.
    """
    markers = package.get("markers") or []
    if not markers:
        raise EditorialDavinciError(ERR_EVIDENCE_MISMATCH)
    marker = markers[0]

    if selection.get("candidate_id") != package.get("candidate_id"):
        raise EditorialDavinciError(ERR_EVIDENCE_MISMATCH)
    if selection.get("candidate_id") != marker.get("candidate_id"):
        raise EditorialDavinciError(ERR_EVIDENCE_MISMATCH)

    if selection.get("video_clip") != marker.get("video_clip"):
        raise EditorialDavinciError(ERR_EVIDENCE_MISMATCH)

    if not _decimal_equal(
        selection.get("source_in_seconds"), marker.get("source_in_seconds")
    ):
        raise EditorialDavinciError(ERR_EVIDENCE_MISMATCH)
    if not _decimal_equal(
        selection.get("source_out_seconds"), marker.get("source_out_seconds")
    ):
        raise EditorialDavinciError(ERR_EVIDENCE_MISMATCH)


def _materialize_output(output_path: str | Path, fcpxml_text: str) -> None:
    """Safely write the FCPXML artifact; never overwrite silently.

    Refuses if the target already exists (no --force in V1). Writes to a
    sibling temp file then atomically replaces the target so no partial
    .fcpxml survives a failure.
    """
    target = Path(output_path)
    if target.exists():
        raise EditorialDavinciError(ERR_OUTPUT_EXISTS)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.name}.tmp")
    try:
        tmp.write_text(fcpxml_text, encoding="utf-8")
        os.replace(tmp, target)
    except OSError:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        raise

def _cleanup_output(output_path: str | Path) -> None:
    """Remove a newly-created FCPXML output and its temp sibling on persistence failure."""
    target = Path(output_path)
    temp = target.with_name(f"{target.name}.tmp")

    for path in (target, temp):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
