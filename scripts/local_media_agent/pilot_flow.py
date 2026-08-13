"""Thin Slice-1 orchestration for the local media pilot flow.

The flow intentionally requires an explicit selected media path after the
read-only root scan. It composes existing Editorial Intelligence contracts and
does not enumerate volumes, persist output, search, answer questions, or call a
provider.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from scripts.editorial_intelligence.audio_extraction.audio_extraction import (
    ExtractedAudioResult,
    extract_audio,
    resolve_ffmpeg_path,
)
from scripts.editorial_intelligence.media_probe.media_probe import probe_media
from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
    TranscriptSegment,
    transcription_result_to_transcript_segments,
)
from scripts.editorial_intelligence.transcription.transcription import (
    FasterWhisperTranscriptionBackend,
    TranscriptionBackend,
    TranscriptionRequest,
    transcribe,
)
from scripts.local_media_agent.host_path_adapter import resolve_input_root
from scripts.local_media_agent.read_only_folder_scanner import (
    MEDIA_EXTENSIONS,
    STATUS_COMPLETED,
    STATUS_COMPLETED_WITH_WARNINGS,
    scan_read_only_folder,
)


SCHEMA_VERSION = "CID.LOCAL_MEDIA_AGENT.SEPTEMBER_PILOT_FLOW.V1"
PHASE = "CID.LOCAL_MEDIA_AGENT.SEPTEMBER_PILOT.PRODUCTIZATION.SLICE_1.V1"

STATUS_COMPLETED_FLOW = "PILOT_FLOW_COMPLETED"
STATUS_PREFLIGHT_FAILED = "PILOT_FLOW_PREFLIGHT_FAILED"
STATUS_SCAN_FAILED = "PILOT_FLOW_SCAN_FAILED"
STATUS_METADATA_FAILED = "PILOT_FLOW_METADATA_FAILED"
STATUS_AUDIO_FAILED = "PILOT_FLOW_AUDIO_FAILED"
STATUS_TRANSCRIPTION_FAILED = "PILOT_FLOW_TRANSCRIPTION_FAILED"
STATUS_PROVENANCE_FAILED = "PILOT_FLOW_PROVENANCE_FAILED"

STAGE_PREFLIGHT = "preflight"
STAGE_SCAN = "scan"
STAGE_METADATA = "metadata"
STAGE_AUDIO = "audio_extraction"
STAGE_TRANSCRIPTION = "transcription"
STAGE_PROVENANCE = "provenance"

_TOOL_CHECKER = Callable[[str], str | None]
_SCANNER = Callable[[str | Path], dict[str, Any]]
_PROBER = Callable[[str, str | Path], dict[str, Any]]
_AUDIO_EXTRACTOR = Callable[..., ExtractedAudioResult]
_TRANSCRIBER = Callable[[TranscriptionRequest, TranscriptionBackend], Any]
_PROVENANCE_BUILDER = Callable[..., list[TranscriptSegment]]


@dataclass(frozen=True, slots=True)
class PilotFlowRequest:
    """Explicit user-selected inputs for one local pilot flow."""

    input_root: str | Path
    selected_media_path: str | Path
    asset_id: str
    model_local_path: str | Path
    language_hint: str | None = None
    device: str = "cpu"
    ffmpeg_path: str | None = None
    temp_dir: str | Path | None = None


@dataclass(frozen=True, slots=True)
class PilotFlowDependencies:
    """Optional seams for deterministic unit tests without real media."""

    scanner: _SCANNER = scan_read_only_folder
    prober: _PROBER = probe_media
    audio_extractor: _AUDIO_EXTRACTOR = extract_audio
    transcriber: _TRANSCRIBER = transcribe
    provenance_builder: _PROVENANCE_BUILDER = transcription_result_to_transcript_segments
    backend_factory: Callable[..., TranscriptionBackend] = FasterWhisperTranscriptionBackend
    tool_checker: _TOOL_CHECKER | None = None


def run_pilot_flow(
    request: PilotFlowRequest,
    *,
    dependencies: PilotFlowDependencies | None = None,
) -> dict[str, Any]:
    """Run the bounded scan-to-provenance flow and return a sanitized result."""

    deps = dependencies or PilotFlowDependencies()
    validation = _validate_request(request)
    if validation is not None:
        return _failure(STATUS_PREFLIGHT_FAILED, STAGE_PREFLIGHT, validation)

    root, selected, path_error = _resolve_selected_paths(request)
    if path_error is not None or root is None or selected is None:
        return _failure(STATUS_PREFLIGHT_FAILED, STAGE_PREFLIGHT, path_error or "INPUT_INVALID")

    preflight_error = _run_preflight(request, deps, selected)
    if preflight_error is not None:
        return _failure(STATUS_PREFLIGHT_FAILED, STAGE_PREFLIGHT, preflight_error)

    scanner_result = deps.scanner(root)
    scan_status = scanner_result.get("status")
    if scan_status not in {STATUS_COMPLETED, STATUS_COMPLETED_WITH_WARNINGS}:
        return _failure(
            STATUS_SCAN_FAILED,
            STAGE_SCAN,
            "SCAN_NOT_COMPLETED",
            scanner=scanner_result,
        )

    metadata_result = deps.prober(request.asset_id, selected)
    if metadata_result.get("media_probe_state") == "PROBE_FAILED":
        return _failure(
            STATUS_METADATA_FAILED,
            STAGE_METADATA,
            "MEDIA_PROBE_FAILED",
            scanner=scanner_result,
            metadata=_sanitize_metadata(metadata_result),
        )

    try:
        with deps.audio_extractor(
            metadata_result,
            ffmpeg_path=request.ffmpeg_path,
            temp_dir=request.temp_dir,
        ) as audio_result:
            audio_payload = audio_result.to_dict()
            if audio_result.state != "AUDIO_EXTRACTION_COMPLETED":
                return _failure(
                    STATUS_AUDIO_FAILED,
                    STAGE_AUDIO,
                    audio_result.state or "AUDIO_EXTRACTION_FAILED",
                    scanner=scanner_result,
                    metadata=_sanitize_metadata(metadata_result),
                    audio=_sanitize_audio(audio_payload),
                )

            transcription_request = TranscriptionRequest(
                asset_id=request.asset_id,
                temporary_audio_path=audio_result.path,
                source_audio_stream_index=audio_payload["audio"].get("source_audio_stream_index"),
                extracted_audio_start_seconds=audio_payload["audio"].get(
                    "extracted_audio_start_seconds"
                )
                or 0.0,
                audio_duration_seconds=audio_payload["audio"].get("duration_seconds"),
                language_hint=request.language_hint,
                model_local_path=request.model_local_path,
                device=request.device,
            )
            backend = deps.backend_factory(
                request.model_local_path,
                device=request.device,
            )
            transcription_result = deps.transcriber(transcription_request, backend)
            transcription_payload = transcription_result.to_dict()
            if transcription_result.state != "TRANSCRIPTION_COMPLETED":
                return _failure(
                    STATUS_TRANSCRIPTION_FAILED,
                    STAGE_TRANSCRIPTION,
                    transcription_result.state or "TRANSCRIPTION_FAILED",
                    scanner=scanner_result,
                    metadata=_sanitize_metadata(metadata_result),
                    audio=_sanitize_audio(audio_payload),
                    transcription=_sanitize_transcription(transcription_payload),
                )

            try:
                segments = deps.provenance_builder(
                    transcription_payload,
                    audio_extraction_payload=audio_payload,
                    media_probe_payload=metadata_result,
                )
            except Exception:
                return _failure(
                    STATUS_PROVENANCE_FAILED,
                    STAGE_PROVENANCE,
                    "PROVENANCE_CONSTRUCTION_FAILED",
                    scanner=scanner_result,
                    metadata=_sanitize_metadata(metadata_result),
                    audio=_sanitize_audio(audio_payload),
                    transcription=_sanitize_transcription(transcription_payload),
                )

            return {
                "schema_version": SCHEMA_VERSION,
                "phase": PHASE,
                "status": STATUS_COMPLETED_FLOW,
                "input": {
                    "selected_root_label": root.name,
                    "selected_media_label": selected.name,
                    "selected_media_relative_path": selected.relative_to(root).as_posix(),
                    "asset_id": request.asset_id,
                    "language_hint": request.language_hint,
                },
                "preflight": {"status": "PREFLIGHT_COMPLETED"},
                "scanner": scanner_result,
                "metadata": _sanitize_metadata(metadata_result),
                "audio": _sanitize_audio(audio_payload),
                "transcription": _sanitize_transcription(transcription_payload),
                "transcript_segments": [segment.to_dict() for segment in segments],
                "language": {
                    "detected_language": transcription_payload.get("detected_language"),
                    "language_probability": transcription_payload.get("language_probability"),
                    "interpretation": "document_level_metadata_only",
                },
                "privacy": {
                    "source_media_modified": False,
                    "network_used": False,
                    "database_used": False,
                    "search_or_qa_used": False,
                },
            }
    except Exception:
        return _failure(
            STATUS_AUDIO_FAILED,
            STAGE_AUDIO,
            "AUDIO_OR_TRANSCRIPTION_PIPELINE_FAILED",
            scanner=scanner_result,
            metadata=_sanitize_metadata(metadata_result),
        )


def _validate_request(request: PilotFlowRequest) -> str | None:
    if not isinstance(request, PilotFlowRequest):
        return "REQUEST_INVALID"
    if not str(request.asset_id).strip():
        return "ASSET_ID_REQUIRED"
    if not str(request.model_local_path).strip():
        return "LOCAL_MODEL_PATH_REQUIRED"
    if request.device not in {"cpu", "cuda"}:
        return "DEVICE_UNSUPPORTED"
    return None


def _resolve_selected_paths(
    request: PilotFlowRequest,
) -> tuple[Path | None, Path | None, str | None]:
    root, error = resolve_input_root(request.input_root)
    if error is not None or root is None:
        return None, None, error or "INPUT_ROOT_INVALID"
    if root.is_symlink():
        return None, None, "ROOT_SYMLINK_REJECTED"
    try:
        resolved_root = root.resolve(strict=False)
        selected_input = Path(request.selected_media_path).expanduser()
        lexical_root = root.absolute()
        lexical_selected = selected_input.absolute()
        selected_relative = lexical_selected.relative_to(lexical_root)
        symlink_error = _selected_path_symlink_error(
            lexical_root,
            selected_relative,
        )
        if symlink_error is not None:
            return None, None, symlink_error
        selected = selected_input.resolve(strict=False)
        selected.relative_to(resolved_root)
    except (OSError, TypeError, ValueError):
        return None, None, "SELECTED_MEDIA_OUTSIDE_INPUT_ROOT"
    if not selected.exists() or not selected.is_file():
        return None, None, "SELECTED_MEDIA_FILE_NOT_FOUND"
    if selected.suffix.lower() not in MEDIA_EXTENSIONS:
        return None, None, "SELECTED_MEDIA_UNSUPPORTED_EXTENSION"
    return resolved_root, selected, None


def _selected_path_symlink_error(
    lexical_root: Path,
    selected_relative: Path,
) -> str | None:
    """Reject symlink components under the caller-authorized root boundary."""
    parts = selected_relative.parts
    for index in range(1, len(parts) + 1):
        component = lexical_root.joinpath(*parts[:index])
        if component.is_symlink():
            if index == len(parts):
                return "SELECTED_MEDIA_SYMLINK_REJECTED"
            return "SELECTED_MEDIA_PARENT_SYMLINK_REJECTED"
    return None


def _run_preflight(
    request: PilotFlowRequest,
    dependencies: PilotFlowDependencies,
    selected: Path,
) -> str | None:
    checker = dependencies.tool_checker or shutil.which
    if checker("ffprobe") is None:
        return "FFPROBE_NOT_AVAILABLE"
    if checker(resolve_ffmpeg_path(request.ffmpeg_path)) is None:
        return "FFMPEG_NOT_AVAILABLE"
    model_path = Path(request.model_local_path).expanduser()
    if not model_path.is_dir():
        return "LOCAL_TRANSCRIPTION_MODEL_NOT_AVAILABLE"
    if not selected.is_file():
        return "SELECTED_MEDIA_NOT_AVAILABLE"
    return None


def _failure(
    status: str,
    stage: str,
    error_code: str,
    **payload: Any,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "status": status,
        "failed_stage": stage,
        "error": {"error_code": error_code, "message_sanitized": error_code},
        "privacy": {
            "source_media_modified": False,
            "network_used": False,
            "database_used": False,
            "search_or_qa_used": False,
        },
        **payload,
    }


def _sanitize_metadata(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    source_reference = dict(result.get("source_reference") or {})
    source_reference.pop("internal_local_source_reference", None)
    result["source_reference"] = source_reference
    return result


def _sanitize_audio(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    audio = dict(result.get("audio") or {})
    audio.pop("extracted_audio_temp_ref", None)
    result["audio"] = audio
    return result


def _sanitize_transcription(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result.pop("segments", None)
    return result


__all__ = [
    "PilotFlowDependencies",
    "PilotFlowRequest",
    "PHASE",
    "SCHEMA_VERSION",
    "STATUS_COMPLETED_FLOW",
    "STATUS_PREFLIGHT_FAILED",
    "run_pilot_flow",
]
