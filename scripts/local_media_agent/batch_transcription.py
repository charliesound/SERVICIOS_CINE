"""CID Local Media Agent — Batch transcription and SRT generation.

Runs multi-file local transcription with structured JSON output and
standards-compatible SRT subtitle generation. No backend, no database, no network.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BATCH_SCHEMA_VERSION = "cid.local_media_agent.batch_transcription.v1"
BATCH_SUMMARY_SCHEMA_VERSION = "cid.local_media_agent.batch_summary.v1"

VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".mxf", ".mkv", ".avi", ".mts", ".m2ts", ".webm"})
AUDIO_EXTENSIONS = frozenset({".wav", ".bwf", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg"})
TRANSCRIBABLE_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

APPLEDOUBLE_PREFIX = "._"

_SRT_TIMESTAMP_RE = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})$"
)
_SRT_CUE_NUMBER_RE = re.compile(r"^\d+$")


def select_batch_candidates(
    metadata_results: list[dict[str, Any]],
    *,
    max_files: int | None = None,
    filter_pattern: str | None = None,
) -> list[dict[str, Any]]:
    """Select eligible transcription candidates from metadata results.

    Skips AppleDouble files, images, and metadata failures.
    Optionally filters by substring and limits count.
    """
    candidates = []
    for r in metadata_results:
        rel = r.get("relative_path", "")
        if rel.startswith(APPLEDOUBLE_PREFIX):
            continue
        cat = r.get("category", "")
        if cat not in ("audio", "video"):
            continue
        dur = r.get("duration_seconds")
        if dur is None or dur <= 0:
            continue
        if filter_pattern and filter_pattern.lower() not in rel.lower():
            continue
        candidates.append(r)

    candidates.sort(key=lambda x: x.get("duration_seconds") or 99999)

    if max_files is not None and max_files > 0:
        candidates = candidates[:max_files]

    return candidates


def _sanitize_name(relative_path: str) -> str:
    """Create a filesystem-safe name from a relative path."""
    stem = Path(relative_path).stem
    sanitized = re.sub(r"[^\w\-.]", "_", stem)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return sanitized or "untitled"


def _format_srt_timestamp(seconds: float) -> str:
    """Convert seconds to SRT HH:MM:SS,mmm format."""
    if seconds < 0:
        seconds = 0.0
    total_ms = int(math.floor(seconds * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(segments: list[dict[str, Any]], duration_seconds: float | None = None) -> str:
    """Generate standards-compatible SRT text from transcription segments.

    Segments must have 'start_seconds', 'end_seconds', 'text' keys.
    """
    cues: list[str] = []
    for idx, seg in enumerate(segments):
        start = float(seg.get("start_seconds", seg.get("source_start_seconds", 0)))
        end = float(seg.get("end_seconds", seg.get("source_end_seconds", 0)))
        text = str(seg.get("text", "")).strip()
        if not text:
            continue
        if start < 0:
            start = 0.0
        if end < start:
            end = start
        if duration_seconds is not None and end > duration_seconds + 0.5:
            end = min(end, duration_seconds)
        cue_num = len(cues) + 1
        cues.append(
            f"{cue_num}\n"
            f"{_format_srt_timestamp(start)} --> {_format_srt_timestamp(end)}\n"
            f"{text}"
        )
    return "\n\n".join(cues) + ("\n" if cues else "")


def generate_transcript_txt(segments: list[dict[str, Any]]) -> str:
    """Generate a human-readable timestamped plain-text transcript."""
    blocks: list[str] = []
    for seg in segments:
        start = float(seg.get("start_seconds", seg.get("source_start_seconds", 0)))
        text = str(seg.get("text", "")).strip()
        if not text:
            continue
        blocks.append(f"{_format_srt_timestamp(start)}\n{text}")
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def generate_davinci_manifest(
    asset_name: str,
    source_rel_path: str,
    source_duration: float | None,
    detected_language: str | None,
    language_probability: float | None,
    model_identifier: str | None,
    compute_type: str,
    segments: list[dict[str, Any]],
    source_timecode: str | None = None,
) -> dict[str, Any]:
    """Build a DaVinci handoff manifest dict."""
    first_ts = None
    last_ts = None
    if segments:
        first_ts = _format_srt_timestamp(
            float(segments[0].get("start_seconds", segments[0].get("source_start_seconds", 0)))
        )
        last_ts = _format_srt_timestamp(
            float(segments[-1].get("end_seconds", segments[-1].get("source_end_seconds", 0)))
        )
    return {
        "format": "CID_DAVINCI_HANDOFF",
        "version": 1,
        "source": {
            "relative_path": source_rel_path,
            "duration_seconds": source_duration,
            "media_type": "audio",
            "source_timecode": source_timecode,
        },
        "transcription": {
            "language": detected_language,
            "language_probability": language_probability,
            "compute_type": compute_type,
            "model": model_identifier,
            "segment_count": len(segments),
            "first_segment_timestamp": first_ts,
            "last_segment_timestamp": last_ts,
        },
        "assets": {
            "srt": f"{asset_name}.srt",
            "transcript_json": f"{asset_name}.transcript.json",
            "transcript_txt": f"{asset_name}.transcript.txt",
        },
        "subtitle_timing": "source-relative",
    }


def validate_srt(srt_text: str, duration_seconds: float | None = None) -> dict[str, Any]:
    """Validate SRT text programmatically. Returns validation result dict."""
    warnings: list[str] = []
    errors: list[str] = []

    if not srt_text or not srt_text.strip():
        return {"valid": False, "errors": ["EMPTY_SRT"], "warnings": [], "cue_count": 0}

    lines = srt_text.strip().split("\n")
    cue_count = 0
    prev_end_ms = 0
    idx = 0

    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue

        if not _SRT_CUE_NUMBER_RE.match(line):
            errors.append(f"Line {idx + 1}: invalid cue number '{line}'")
            idx += 1
            continue

        cue_count += 1
        expected_num = cue_count
        actual_num = int(line)
        if actual_num != expected_num:
            errors.append(f"Cue {cue_count}: expected {expected_num}, got {actual_num}")

        idx += 1
        if idx >= len(lines):
            errors.append(f"Cue {cue_count}: missing timestamp line")
            break

        ts_line = lines[idx].strip()
        m = _SRT_TIMESTAMP_RE.match(ts_line)
        if not m:
            errors.append(f"Cue {cue_count}: invalid timestamp '{ts_line}'")
            idx += 1
            continue

        start_ms = (
            int(m.group(1)) * 3600000
            + int(m.group(2)) * 60000
            + int(m.group(3)) * 1000
            + int(m.group(4))
        )
        end_ms = (
            int(m.group(5)) * 3600000
            + int(m.group(6)) * 60000
            + int(m.group(7)) * 1000
            + int(m.group(8))
        )

        if end_ms < start_ms:
            errors.append(f"Cue {cue_count}: end < start")
        if start_ms < 0:
            errors.append(f"Cue {cue_count}: negative start timestamp")
        if prev_end_ms > 0 and start_ms < prev_end_ms:
            warnings.append(f"Cue {cue_count}: start before previous end")
        prev_end_ms = end_ms

        if duration_seconds is not None:
            max_ms = int(math.ceil(duration_seconds * 1000)) + 500
            if start_ms > max_ms:
                errors.append(f"Cue {cue_count}: start exceeds media duration")

        idx += 1
        if idx < len(lines):
            next_idx = idx + 1
            if next_idx < len(lines) and lines[next_idx].strip():
                warnings.append(f"Cue {cue_count}: missing blank separator after cue text")
        idx += 1

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "cue_count": cue_count,
    }


def run_batch_transcription(
    input_root: str | Path,
    model_dir: str | Path,
    *,
    metadata_results: list[dict[str, Any]] | None = None,
    compute_type: str = "int8",
    max_files: int | None = None,
    filter_pattern: str | None = None,
    language_hint: str | None = None,
    results_dir: str | Path | None = None,
    ffmpeg_path: str | None = None,
    device: str = "cpu",
    cancel_event: Any = None,
    progress_callback: Any = None,
    segment_callback: Any = None,
    worker_process: bool = False,
    grace_period_seconds: float = 3.0,
    worker_log_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Run batch transcription on selected media items.

    Produces per-file transcript JSON, SRT files, and a batch summary JSON.

    Supports cooperative cancellation: ``cancel_event`` (an object exposing
    ``is_set()``) is checked before each item and after each transcription.
    On cancellation the batch writes a ``BATCH_CANCELLED`` summary with actual
    completed/cancelled/unstarted counts. ``progress_callback`` is invoked as
    ``progress_callback(index, total, relative_path)`` before each item.
    ``segment_callback`` (optional) is forwarded to each per-file transcription
    and invoked as ``segment_callback(segment)`` per produced segment, enabling
    truthful producer-facing progress.

    ``worker_process=True`` runs each active media item in a dedicated owned
    worker subprocess (``cid_transcription_worker``). On cancellation the
    controller signals cooperatively via a sentinel file, waits
    ``grace_period_seconds``, then force-terminates only that owned worker
    tree. ``worker_log_dir`` (optional) stores per-worker stderr logs. The
    summary then reports a truthful ``cancel_latency_seconds`` measurement.
    """
    from scripts.local_media_agent.local_transcription import transcribe_media_file

    input_root = Path(input_root)
    model_dir = Path(model_dir)

    if metadata_results is not None:
        candidates = select_batch_candidates(
            metadata_results, max_files=max_files, filter_pattern=filter_pattern
        )
    else:
        candidates = _scan_for_candidates(input_root, max_files=max_files, filter_pattern=filter_pattern)

    if not candidates:
        return {
            "schema_version": BATCH_SCHEMA_VERSION,
            "status": "NO_CANDIDATES",
            "input_root": str(input_root),
            "candidates_found": 0,
            "files_attempted": 0,
            "files_transcribed": 0,
            "files_no_speech": 0,
            "files_error": 0,
            "total_source_duration_seconds": 0,
            "total_processing_seconds": 0,
            "results": [],
        }

    resolved_results_dir = Path(results_dir) if results_dir else _default_results_dir()
    resolved_results_dir.mkdir(parents=True, exist_ok=True)

    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    batch_results: list[dict[str, Any]] = []
    files_transcribed = 0
    files_no_speech = 0
    files_error = 0
    total_source_duration = 0.0
    total_processing = 0.0
    all_languages: list[str] = []
    srt_files_created = 0
    txt_files_created = 0
    davinci_handoff_files_created = 0

    batch_start = time.monotonic()

    files_cancelled = 0
    cancelled = False
    cancel_requested_at: float | None = None

    try:
        for i, candidate in enumerate(candidates):
            if cancel_event is not None and cancel_event.is_set():
                if cancel_requested_at is None:
                    cancel_requested_at = time.monotonic()
                cancelled = True
                break

            rel = candidate.get("relative_path", "")
            abs_path = input_root / rel
            cat = candidate.get("category", "")
            dur = candidate.get("duration_seconds")
            asset_name = _sanitize_name(rel)

            if progress_callback is not None:
                progress_callback(i + 1, len(candidates), rel)

            print(f"  [{i + 1}/{len(candidates)}] {rel} ({cat}, {dur:.1f}s)" if dur else f"  [{i + 1}/{len(candidates)}] {rel} ({cat})", flush=True)

            try:
                t0 = time.monotonic()
                if worker_process:
                    result, cancel_detected_at = _transcribe_item_via_worker(
                        abs_path,
                        model_dir,
                        asset_id=asset_name,
                        language_hint=language_hint,
                        device=device,
                        compute_type=compute_type,
                        ffmpeg_path=ffmpeg_path,
                        cancel_event=cancel_event,
                        grace_period_seconds=grace_period_seconds,
                        worker_log_dir=worker_log_dir,
                        progress_callback=segment_callback,
                    )
                    if cancel_detected_at is not None:
                        if cancel_requested_at is None:
                            cancel_requested_at = cancel_detected_at
                        cancelled = True
                else:
                    result = transcribe_media_file(
                        abs_path,
                        model_dir,
                        asset_id=asset_name,
                        language_hint=language_hint,
                        device=device,
                        compute_type=compute_type,
                        ffmpeg_path=ffmpeg_path,
                        cancel_event=cancel_event,
                        segment_callback=segment_callback,
                    )
                elapsed = time.monotonic() - t0

                status = result.get("status", "UNKNOWN")

                if status == "TRANSCRIPTION_CANCELLED":
                    cancelled = True
                    files_cancelled += 1
                    cancelled_result = {
                        "relative_path": rel,
                        "category": cat,
                        "source_duration_seconds": dur,
                        "transcription_status": "TRANSCRIPTION_CANCELLED",
                        "cancelled": True,
                        "srt_file": None,
                    }
                    batch_results.append(cancelled_result)
                    print("    CANCELLED | user requested stop", flush=True)
                    break

                segments = result.get("segments", [])
                detected_lang = result.get("detected_language")
                lang_prob = result.get("language_probability")
                source_dur = result.get("audio_duration_seconds") or dur

                if source_dur:
                    total_source_duration += float(source_dur)
                total_processing += elapsed

                if detected_lang:
                    all_languages.append(str(detected_lang))

                file_result = {
                    "relative_path": rel,
                    "category": cat,
                    "source_duration_seconds": source_dur,
                    "source_timecode": candidate.get("timecode"),
                    "detected_language": detected_lang,
                    "language_probability": lang_prob,
                    "engine": "faster-whisper",
                    "model_identifier": result.get("model_identifier"),
                    "compute_type": compute_type,
                    "device": device,
                    "segments": segments,
                    "processing_seconds": round(elapsed, 2),
                    "rtf": round(elapsed / float(source_dur), 4) if source_dur and float(source_dur) > 0 else None,
                    "transcription_status": status,
                    "error": result.get("error"),
                }

                has_speech = status == "TRANSCRIPTION_COMPLETED" and len(segments) > 0

                if has_speech:
                    files_transcribed += 1
                    srt_text = generate_srt(segments, source_dur)
                    srt_path = resolved_results_dir / f"{asset_name}.srt"
                    srt_path.write_text(srt_text, encoding="utf-8")
                    file_result["srt_file"] = str(srt_path.name)
                    srt_files_created += 1

                    srt_validation = validate_srt(srt_text, source_dur)
                    file_result["srt_validation"] = srt_validation

                    txt_text = generate_transcript_txt(segments)
                    txt_path = resolved_results_dir / f"{asset_name}.transcript.txt"
                    txt_path.write_text(txt_text, encoding="utf-8")
                    file_result["transcript_txt_file"] = txt_path.name

                    manifest = generate_davinci_manifest(
                        asset_name=asset_name,
                        source_rel_path=rel,
                        source_duration=source_dur,
                        detected_language=detected_lang,
                        language_probability=lang_prob,
                        model_identifier=result.get("model_identifier"),
                        compute_type=compute_type,
                        segments=segments,
                        source_timecode=candidate.get("timecode"),
                    )
                    manifest_path = resolved_results_dir / f"{asset_name}.davinci_handoff.json"
                    manifest_path.write_text(
                        json.dumps(manifest, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    file_result["davinci_handoff_file"] = manifest_path.name
                    txt_files_created += 1
                    davinci_handoff_files_created += 1
                elif status == "TRANSCRIPTION_COMPLETED":
                    files_no_speech += 1
                    file_result["srt_file"] = None
                    file_result["transcript_txt_file"] = None
                    file_result["davinci_handoff_file"] = None
                else:
                    files_error += 1
                    file_result["srt_file"] = None
                    file_result["transcript_txt_file"] = None
                    file_result["davinci_handoff_file"] = None

                json_path = resolved_results_dir / f"{asset_name}.transcript.json"
                json_path.write_text(
                    json.dumps(file_result, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                file_result["transcript_json_file"] = json_path.name

                seg_count = len(segments)
                rtf_str = f"{file_result['rtf']:.4f}" if file_result["rtf"] else "?"
                print(f"    {status} | {detected_lang} | {seg_count} segments | RTF {rtf_str}", flush=True)

                batch_results.append(file_result)

            except KeyboardInterrupt:
                cancelled = True
                break

            except Exception as exc:
                elapsed = time.monotonic() - t0
                total_processing += elapsed
                files_error += 1
                error_result = {
                    "relative_path": rel,
                    "category": cat,
                    "source_duration_seconds": dur,
                    "processing_seconds": round(elapsed, 2),
                    "transcription_status": "BATCH_ERROR",
                    "error": {"message": str(exc)[:300]},
                    "srt_file": None,
                }
                batch_results.append(error_result)
                print(f"    ERROR: {str(exc)[:80]}", flush=True)
    except KeyboardInterrupt:
        cancelled = True

    batch_elapsed = time.monotonic() - batch_start

    primary_language = _most_common(all_languages) if all_languages else None

    unstarted_count = max(0, len(candidates) - len(batch_results))

    cancel_latency_seconds: float | None = None
    if cancelled and cancel_requested_at is not None:
        cancel_latency_seconds = round(time.monotonic() - cancel_requested_at, 2)

    batch_summary = {
        "schema_version": BATCH_SUMMARY_SCHEMA_VERSION,
        "batch_id": batch_id,
        "status": "BATCH_CANCELLED" if cancelled else "BATCH_COMPLETED",
        "cancelled_by_user": cancelled,
        "cancel_latency_seconds": cancel_latency_seconds,
        "input_root": str(input_root),
        "compute_type": compute_type,
        "device": device,
        "model_directory": str(model_dir.name),
        "language_hint": language_hint,
        "files_attempted": len(candidates),
        "candidate_count": len(candidates),
        "completed_count": files_transcribed,
        "cancelled_count": files_cancelled,
        "error_count": files_error,
        "unstarted_count": unstarted_count,
        "files_transcribed": files_transcribed,
        "files_no_speech": files_no_speech,
        "files_errors": files_error,
        "primary_language": primary_language,
        "srt_files_created": srt_files_created,
        "txt_files_created": txt_files_created,
        "davinci_handoff_files_created": davinci_handoff_files_created,
        "total_source_duration_seconds": round(total_source_duration, 2),
        "total_processing_seconds": round(batch_elapsed, 2),
        "overall_rtf": round(batch_elapsed / total_source_duration, 4) if total_source_duration > 0 else None,
        "results_directory": str(resolved_results_dir),
        "results": batch_results,
        "privacy": {
            "source_media_modified": False,
            "network_used": False,
            "database_used": False,
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    summary_path = resolved_results_dir / "batch_summary.json"
    summary_path.write_text(
        json.dumps(batch_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return batch_summary


def _worker_temp_dir() -> Path:
    """Return a controller-owned temp dir for worker task/result files."""
    base = Path(tempfile.gettempdir()) / "cid_lma_worker"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _consume_worker_progress(
    progress_path: Path,
    offset: int,
    callback: Any,
) -> int:
    """Forward new JSONL progress lines to ``callback``; return new byte offset."""
    if callback is None:
        return offset
    try:
        with progress_path.open("r", encoding="utf-8") as fh:
            fh.seek(offset)
            lines = fh.readlines()
        new_offset = offset + sum(len(line.encode("utf-8")) for line in lines)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                seg = json.loads(line)
            except ValueError:
                continue
            callback(seg)
        return new_offset
    except OSError:
        return offset


def _terminate_worker_tree(proc: subprocess.Popen) -> None:
    """Force-terminate a dedicated worker and its child ffmpeg process."""
    from scripts.local_media_agent.local_transcription import _windows_no_console_kwargs

    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                timeout=10,
                **_windows_no_console_kwargs(),
            )
        except Exception:
            pass
    else:
        proc.kill()


def _transcribe_item_via_worker(
    media_path: Path,
    model_dir: Path,
    *,
    asset_id: str,
    language_hint: str | None,
    device: str,
    compute_type: str,
    ffmpeg_path: str | None,
    cancel_event: Any,
    grace_period_seconds: float,
    worker_log_dir: str | Path | None,
    progress_callback: Any,
) -> tuple[dict[str, Any], float | None]:
    """Transcribe one media item in a dedicated, owned worker subprocess.

    Returns ``(result_payload, cancel_detected_at_monotonic)``. On cancellation
    the worker is signalled cooperatively through a sentinel file, given
    ``grace_period_seconds`` to stop, then its owned process tree is
    terminated. All controller-owned temp files (task, result, sentinel,
    progress log, output WAV) are removed here.
    """
    from scripts.local_media_agent.local_transcription import _windows_no_console_kwargs

    token = uuid.uuid4().hex[:12]
    temp_dir = _worker_temp_dir()
    task_path = temp_dir / f"cid_task_{token}.json"
    result_path = temp_dir / f"cid_result_{token}.json"
    sentinel_path = temp_dir / f"cid_cancel_{token}.flag"
    progress_path = temp_dir / f"cid_progress_{token}.jsonl"
    output_wav = temp_dir / f"cid_audio_{token}.wav"

    cancel_detected_at: float | None = None

    task = {
        "media_path": str(media_path),
        "model_dir": str(model_dir),
        "asset_id": asset_id,
        "language_hint": language_hint,
        "device": device,
        "compute_type": compute_type,
        "ffmpeg_path": ffmpeg_path,
        "temp_dir": str(temp_dir),
        "output_wav": str(output_wav),
        "result_json": str(result_path),
        "progress_log": str(progress_path),
        "cancel_sentinel": str(sentinel_path),
    }
    task_path.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")

    stderr_target: Any = subprocess.DEVNULL
    log_fh: Any = None
    if worker_log_dir is not None:
        log_root = Path(worker_log_dir)
        log_root.mkdir(parents=True, exist_ok=True)
        log_fh = open(log_root / f"worker_{token}.log", "w", encoding="utf-8")
        stderr_target = log_fh

    try:
        cmd = [
            sys.executable,
            "-m",
            "scripts.local_media_agent.cid_transcription_worker",
            str(task_path),
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=stderr_target,
            **_windows_no_console_kwargs(),
        )

        progress_offset = 0
        while proc.poll() is None:
            progress_offset = _consume_worker_progress(
                progress_path, progress_offset, progress_callback
            )
            if cancel_event is not None and cancel_event.is_set():
                if cancel_detected_at is None:
                    cancel_detected_at = time.monotonic()
                sentinel_path.write_text("cancel\n", encoding="utf-8")
                grace_end = time.monotonic() + max(0.0, grace_period_seconds)
                while time.monotonic() < grace_end and proc.poll() is None:
                    progress_offset = _consume_worker_progress(
                        progress_path, progress_offset, progress_callback
                    )
                    time.sleep(0.05)
                if proc.poll() is None:
                    _terminate_worker_tree(proc)
                break
            time.sleep(0.05)

        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            _terminate_worker_tree(proc)
            proc.wait()

        progress_offset = _consume_worker_progress(
            progress_path, progress_offset, progress_callback
        )

        if result_path.is_file():
            result = json.loads(result_path.read_text(encoding="utf-8"))
        elif cancel_detected_at is not None:
            result = {
                "schema_version": "cid.local_media_agent.local_transcription.v1",
                "status": "TRANSCRIPTION_CANCELLED",
                "relative_path": str(media_path),
                "asset_id": asset_id,
                "cancelled": True,
                "segments": [],
                "error": None,
            }
        else:
            result = {
                "schema_version": "cid.local_media_agent.local_transcription.v1",
                "status": "TRANSCRIPTION_FAILED",
                "relative_path": str(media_path),
                "asset_id": asset_id,
                "segments": [],
                "error": {"message": "worker process terminated unexpectedly"},
            }
        return result, cancel_detected_at
    finally:
        if log_fh is not None:
            try:
                log_fh.close()
            except Exception:
                pass
        for path in (task_path, result_path, sentinel_path, progress_path, output_wav):
            try:
                path.unlink()
            except OSError:
                pass


def _scan_for_candidates(
    input_root: Path,
    *,
    max_files: int | None = None,
    filter_pattern: str | None = None,
) -> list[dict[str, Any]]:
    """Lightweight file scan for transcription candidates when metadata is unavailable."""
    candidates: list[dict[str, Any]] = []
    for path in input_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith(APPLEDOUBLE_PREFIX):
            continue
        if path.suffix.lower() not in TRANSCRIBABLE_EXTENSIONS:
            continue
        rel = str(path.relative_to(input_root))
        if filter_pattern and filter_pattern.lower() not in rel.lower():
            continue
        candidates.append({
            "relative_path": rel,
            "category": "audio" if path.suffix.lower() in AUDIO_EXTENSIONS else "video",
            "duration_seconds": None,
            "file_size_bytes": path.stat().st_size,
        })

    candidates.sort(key=lambda x: x.get("duration_seconds") or 99999)
    if max_files and max_files > 0:
        candidates = candidates[:max_files]
    return candidates


def _default_results_dir() -> Path:
    """Return the default persistent results directory."""
    local_appdata = os.environ.get("LOCALAPPDATA", os.environ.get("HOME", "/tmp"))
    return Path(local_appdata) / "CID" / "LocalMediaAgent" / "results"


def _most_common(items: list[str]) -> str | None:
    if not items:
        return None
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return max(counts, key=counts.get)  # type: ignore[arg-type]
