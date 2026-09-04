"""CID Local Media Agent — Audio Source Intelligence.

Groups related media into recording/session clusters, performs quick audio
content comparison, estimates synchronization, classifies content
relationships, analyzes source quality, assigns source roles and recommends
the smallest useful set of transcription masters.

Everything is local and offline: only the already packaged FFmpeg and numpy
are used. Analysis decodes short bounded windows at a low sample rate and
keeps no derivatives (decode happens via piped stdout or in-memory reads).

The public entry points operate on metadata results produced by
``ffprobe_metadata_extraction`` plus the media root. Synthetic deterministic
tests exercise the pure signal functions through generated WAV files.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from scripts.local_media_agent.media_catalog import media_item_key
from scripts.local_media_agent.session_boundary import coarse_session_id

SYNC_MANIFEST_SCHEMA_VERSION = "cid.local_media_agent.sync_manifest.v1"

SOURCE_SIGNATURE_ALGORITHM_VERSION = "cid.local_media_agent.source_signature.v1"

WINDOW_SECONDS_DEFAULT = 20.0
SIGNATURE_SAMPLE_RATE = 8000
ENVELOPE_BLOCKS_PER_SECOND = 10
FINE_REFINE_SEARCH_SECONDS = 1.0
FINE_REFINE_WINDOW_SECONDS = 10.0
SYNC_OFFSET_TOLERANCE_SECONDS = 0.100
MIN_OVERLAP_ENVELOPE_SAMPLES = 50

RELATIONSHIP_IDENTICAL = "IDENTICAL_OR_NEAR_DUPLICATE"
RELATIONSHIP_SAME_EVENT = "SAME_EVENT_DIFFERENT_SOURCE"
RELATIONSHIP_COMPLEMENTARY = "COMPLEMENTARY_SOURCE"
RELATIONSHIP_UNRELATED = "UNRELATED"
RELATIONSHIP_UNCERTAIN = "UNCERTAIN"

DISPOSITION_DIALOGUE = "DIALOGUE"
DISPOSITION_DUPLICATE = "DUPLICATE"
DISPOSITION_ALTERNATE = "ALTERNATE"
DISPOSITION_TECHNICAL_OR_EMPTY = "TECHNICAL_OR_EMPTY"
DISPOSITION_UNIQUE_CONTENT = "UNIQUE_CONTENT"
DISPOSITION_UNCERTAIN = "UNCERTAIN"

SYNC_METHOD_TIMECODE = "timecode"
SYNC_METHOD_CORRELATION = "audio_correlation"
SYNC_STATUS_RESOLVED = "RESOLVED"
SYNC_STATUS_UNRESOLVED = "UNRESOLVED"

ROLE_CAMERA_REFERENCE = "CAMERA_REFERENCE"
ROLE_EXTERNAL_MIX = "EXTERNAL_MIX"
ROLE_ISOLATED_MIC = "ISOLATED_MIC"
ROLE_DUPLICATE = "DUPLICATE"
ROLE_UNKNOWN = "UNKNOWN"

# Internal preference applied when content evidence is comparable: the clean
# external mix is the natural transcription master, camera audio is a
# reference only, and isolated tracks remain alternates.
ROLE_MASTER_PREFERENCE = {
    ROLE_EXTERNAL_MIX: 0.06,
    ROLE_ISOLATED_MIC: 0.00,
    ROLE_UNKNOWN: -0.05,
    ROLE_DUPLICATE: -0.10,
    ROLE_CAMERA_REFERENCE: -0.20,
}

QUALITY_EXCELENTE = "Excelente"
QUALITY_BUENA = "Buena"
QUALITY_REFERENCIA = "Referencia"
QUALITY_DEFICIENTE = "Deficiente"

# Internal tier used only to rank sources (never shown verbatim). A genuine
# quality gap dominates the role tie-break, so a degraded mix cannot win over
# a usable source purely because it is labelled EXTERNAL_MIX.
QUALITY_TIER_BONUS = {
    QUALITY_EXCELENTE: 0.15,
    QUALITY_BUENA: 0.05,
    QUALITY_REFERENCIA: -0.05,
    QUALITY_DEFICIENTE: -0.15,
}

HIGH_CONFIDENCE_THRESHOLD = 0.70
RELATED_CONFIDENCE_THRESHOLD = 0.50
MASTER_EVENT_CONFIDENCE_THRESHOLD = 0.45

EXTERNAL_MIX_TOKENS = frozenset({"mix", "main", "master"})
ISOLATED_MIC_TOKENS = frozenset({"track", "combo", "mic", "usb", "1", "2", "3", "4", "5", "6", "7", "8", "9"})
CAMERA_TOKENS = frozenset({"camera", "canon", "sony", "img", "tarjeta", "m4root", "clip", "c0001", "c0011", "c0012", "c0009"})


def _windows_no_console_kwargs() -> dict[str, Any]:
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if os.name == "nt" and flags:
        return {"creationflags": flags}
    return {}


class GroupingError(ValueError):
    """Controlled grouping refusal (ambiguous identity, multi-source before MS2C2)."""

    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


def _resolve_ffmpeg_path(ffmpeg_path: str | None) -> str | None:
    if ffmpeg_path:
        return str(ffmpeg_path)
    configured = os.environ.get("CID_FFMPEG_PATH")
    if configured:
        return configured
    here = Path(__file__).resolve().parent
    for depth in (here, *here.parents):
        candidate = depth / "runtime" / "ffmpeg" / "bin" / "ffmpeg.exe"
        if candidate.is_file():
            return str(candidate)
        candidate = depth / "runtime" / "bin" / "ffmpeg.exe"
        if candidate.is_file():
            return str(candidate)
    return None


def _read_wav_window(
    media_path: str | Path,
    start_seconds: float,
    duration_seconds: float,
    sample_rate: int,
) -> tuple[float, Any] | None:
    """Read a mono WAV window natively (no ffmpeg) when the format matches.

    Returns (actual_sample_rate, mono float32 samples) or None if the file is
    not a plain matching-rate WAV (in which case ffmpeg decoding is used).
    """
    import wave

    try:
        with wave.open(str(media_path), "rb") as wav:
            channels = wav.getnchannels()
            rate = wav.getframerate()
            sampwidth = wav.getsampwidth()
            if sampwidth != 2 or rate != sample_rate:
                return None
            total_frames = wav.getnframes()
            start_frame = max(0, int(start_seconds * rate))
            if start_frame > total_frames:
                return None
            wav.setpos(start_frame)
            n = min(int(duration_seconds * rate), total_frames - start_frame)
            raw = wav.readframes(n)
    except Exception:
        return None
    if not raw:
        return None
    import numpy as np

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    return float(rate), samples


def decode_window(
    media_path: str | Path,
    *,
    start_seconds: float,
    duration_seconds: float,
    sample_rate: int = SIGNATURE_SAMPLE_RATE,
    ffmpeg_path: str | None = None,
) -> tuple[float, Any] | None:
    """Decode a bounded mono window from a media file.

    Returns (sample_rate, float32 mono samples) or None when the window is
    empty/unavailable. Tries a native WAV read first, then ffmpeg piping.
    No temp derivatives are created.
    """
    native = _read_wav_window(media_path, start_seconds, duration_seconds, sample_rate)
    if native is not None:
        return native
    tool = _resolve_ffmpeg_path(ffmpeg_path)
    if not tool:
        return None
    cmd = [
        tool,
        "-v", "error",
        "-ss", f"{start_seconds:.3f}",
        "-t", f"{duration_seconds:.3f}",
        "-i", str(media_path),
        "-vn",
        "-ac", "1",
        "-ar", str(sample_rate),
        "-f", "s16le",
        "-",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=60,
            **_windows_no_console_kwargs(),
        )
    except Exception:
        return None
    if proc.returncode != 0 or not proc.stdout:
        return None
    import numpy as np

    samples = np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    return float(sample_rate), samples


def envelope(
    samples: Any,
    sample_rate: int,
    blocks_per_second: int = ENVELOPE_BLOCKS_PER_SECOND,
) -> Any:
    """Reduce mono samples to a low-rate mean-abs envelope."""
    import numpy as np

    samples = np.asarray(samples, dtype=np.float32)
    if samples.size == 0:
        return np.zeros(0, dtype=np.float32)
    block = max(1, int(sample_rate / max(1, blocks_per_second)))
    n = samples.size
    usable = n - (n % block)
    if usable == 0:
        return np.zeros(0, dtype=np.float32)
    windowed = samples[:usable].reshape(-1, block)
    return np.abs(windowed).mean(axis=1).astype(np.float32)


def _normalized_correlation(a: Any, b: Any) -> float:
    import numpy as np

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size == 0 or b.size == 0:
        return 0.0
    a = a - a.mean()
    b = b - b.mean()
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    if denom <= 0.0:
        return 0.0
    coef = float(np.dot(a, b) / denom)
    return float(max(-1.0, min(1.0, coef)))


def find_sync_lag(
    env_a: Any,
    env_b: Any,
    blocks_per_second: int,
) -> tuple[int, float]:
    """Estimate the envelope lag aligning ``env_b`` onto ``env_a``.

    Returns (lag_samples, normalized_confidence). ``lag`` is the position of
    ``env_b[0]`` on the ``env_a`` timeline (negative means B starts before A).
    """
    import numpy as np

    env_a = np.asarray(env_a, dtype=np.float32)
    env_b = np.asarray(env_b, dtype=np.float32)
    if env_a.size < 2 or env_b.size < 2:
        return 0, 0.0
    corr = np.correlate(env_a, env_b, mode="full")
    if corr.size == 0:
        return 0, 0.0
    idx = int(np.argmax(corr))
    lag = idx - (env_b.size - 1)
    overlap = _overlap_segments(env_a, env_b, lag)
    if overlap is None:
        return lag, 0.0
    confidence = _normalized_correlation(overlap[0], overlap[1])
    return lag, confidence


def _overlap_segments(
    env_a: Any,
    env_b: Any,
    lag: int,
) -> tuple[Any, Any] | None:
    """Return the overlapping portions of A and B for a given lag."""
    import numpy as np

    env_a = np.asarray(env_a, dtype=np.float32)
    env_b = np.asarray(env_b, dtype=np.float32)
    la, lb = env_a.size, env_b.size
    if lag >= 0:
        a0, b0 = lag, 0
    else:
        a0, b0 = 0, -lag
    a_len = min(la - a0, lb - b0)
    if a_len <= 0:
        return None
    return env_a[a0 : a0 + a_len], env_b[b0 : b0 + a_len]


def refine_offset_with_samples(
    samples_a: Any,
    samples_b: Any,
    sample_rate: int,
    coarse_offset_seconds: float,
    search_seconds: float = FINE_REFINE_SEARCH_SECONDS,
) -> tuple[float, float]:
    """Refine a coarse offset using raw-sample correlation around it.

    ``coarse_offset_seconds`` is the offset of B relative to A. Returns the
    refined offset and the fine correlation confidence.
    """
    import numpy as np

    a = np.asarray(samples_a, dtype=np.float32)
    b = np.asarray(samples_b, dtype=np.float32)
    if a.size < 2 or b.size < 2:
        return coarse_offset_seconds, 0.0
    search = max(1, int(search_seconds * sample_rate))
    corr = np.correlate(a, b, mode="full")
    center = corr.size // 2
    lo = max(0, center - search)
    hi = min(corr.size, center + search + 1)
    if hi <= lo:
        return coarse_offset_seconds, 0.0
    region = corr[lo:hi]
    idx = int(np.argmax(region))
    raw_lag = (lo + idx) - center  # positive: B delayed relative to A
    refined = coarse_offset_seconds + raw_lag / sample_rate
    overlap = _overlap_segments(a, b, lo + idx - center)
    confidence = _normalized_correlation(*overlap) if overlap else 0.0
    return float(refined), confidence


def _window_offsets(duration_seconds: float, window_seconds: float) -> list[str]:
    """Return the ordered analysis window keys/anchors for a recording."""
    if duration_seconds is None or duration_seconds <= 0:
        return ["start"]
    if duration_seconds <= window_seconds:
        return ["start"]
    windows = ["start", "middle", "end"]
    return windows


def _window_anchor(key: str, duration_seconds: float, window_seconds: float) -> float:
    if duration_seconds is None or duration_seconds <= 0:
        return 0.0
    if key == "start":
        return 0.0
    if key == "end":
        return max(0.0, duration_seconds - window_seconds)
    return max(0.0, duration_seconds / 2.0 - window_seconds / 2.0)


def analyze_quality(samples: Any, sample_rate: int) -> dict[str, Any]:
    """Compute lightweight objective quality indicators from sampled audio."""
    import numpy as np

    x = np.asarray(samples, dtype=np.float32)
    result: dict[str, Any] = {
        "window_seconds": float(x.size) / float(sample_rate) if sample_rate else 0.0,
        "rms_db": None,
        "peak_db": None,
        "clipping_fraction": 0.0,
        "silence_fraction": 0.0,
        "dynamic_range_db": None,
        "snr_proxy_db": None,
    }
    if x.size == 0:
        return result
    rms = float(np.sqrt(np.mean(x * x)))
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    result["rms_db"] = 20.0 * np.log10(rms + 1e-12) if rms > 1e-9 else None
    result["peak_db"] = 20.0 * np.log10(peak + 1e-12) if peak > 1e-9 else None
    result["clipping_fraction"] = float(np.mean(np.abs(x) >= 0.999))
    block = max(1, int(sample_rate // 10))
    n = x.size
    usable = n - (n % block)
    if usable >= block:
        blocks = np.abs(x[:usable]).reshape(-1, block).mean(axis=1)
        silence_threshold = 10.0 ** (-60.0 / 20.0)
        result["silence_fraction"] = float(np.mean(blocks < silence_threshold))
        non_silent = blocks[blocks >= silence_threshold]
        if non_silent.size > 0:
            db = 20.0 * np.log10(non_silent + 1e-12)
            result["dynamic_range_db"] = float(np.max(db) - np.min(db))
        if non_silent.size > 4:
            floor = float(np.percentile(blocks, 10))
            noise_db = 20.0 * np.log10(floor + 1e-12)
            if result["peak_db"] is not None:
                result["snr_proxy_db"] = float(result["peak_db"] - noise_db)
    return result


def _label_quality(metrics: dict[str, Any]) -> str:
    if metrics.get("clipping_fraction", 0.0) > 0.02:
        return QUALITY_DEFICIENTE
    if metrics.get("silence_fraction", 1.0) > 0.8:
        return QUALITY_DEFICIENTE
    rms_db = metrics.get("rms_db")
    if rms_db is None:
        return QUALITY_REFERENCIA
    if -45.0 <= rms_db <= -12.0 and (metrics.get("dynamic_range_db") or 0.0) >= 8.0:
        return QUALITY_EXCELENTE
    if -55.0 <= rms_db <= -8.0:
        return QUALITY_BUENA
    return QUALITY_REFERENCIA


def assign_source_role(
    relative_path: str,
    category: str,
    has_video: bool,
    metrics: dict[str, Any],
) -> str:
    """Assign an internal source role from metadata/name/path evidence."""
    name = Path(relative_path).stem.lower()
    tokens = {tok for tok in name.replace("-", " ").replace("_", " ").split() if tok}
    if has_video:
        return ROLE_CAMERA_REFERENCE
    if tokens & EXTERNAL_MIX_TOKENS:
        return ROLE_EXTERNAL_MIX
    if tokens & ISOLATED_MIC_TOKENS:
        return ROLE_ISOLATED_MIC
    if any(tok in CAMERA_TOKENS for tok in name.split()):
        return ROLE_CAMERA_REFERENCE
    return ROLE_UNKNOWN


@dataclass
class SourceSignature:
    """Compact analysis signature for one media source."""

    relative_path: str
    category: str
    file_size_bytes: int | None = None
    duration_seconds: float | None = None
    sample_rate: int | None = None
    channel_count: int | None = None
    codec: str | None = None
    timecode: str | None = None
    creation_time: str | None = None
    has_video: bool = False
    windows: dict[str, Any] = field(default_factory=dict)
    quality: dict[str, Any] = field(default_factory=dict)
    role: str = ROLE_UNKNOWN
    sha256: str | None = None
    analysis_seconds: float = 0.0
    source_id: str | None = None
    media_ref: str | None = None


def _resolve_source_identity(item: dict[str, Any]) -> str | None:
    """Resolve the single canonical source identity from a metadata item.

    Accepts transitional ``ROOT-*`` and stable ``SRC-*`` identities. Never
    derives identity from a media root, absolute path, current location, drive
    or filename. If both ``source_id`` and ``source_root_id`` are present and
    differ, that is an ambiguous dual authority and fails closed.
    """
    source_id = item.get("source_id")
    source_root_id = item.get("source_root_id")
    if source_id is None and source_root_id is None:
        return None
    if source_id is not None and source_root_id is None:
        return str(source_id)
    if source_root_id is not None and source_id is None:
        return str(source_root_id)
    if str(source_id) == str(source_root_id):
        return str(source_id)
    raise GroupingError("SOURCE_IDENTITY_CONFLICT")


def member_identity(sig: SourceSignature) -> str:
    """Canonical collision-free member key.

    Source-aware signatures use ``media_ref``; legacy signatures (no source
    identity) keep the prior ``relative_path`` semantics.
    """
    if sig.media_ref is not None:
        return sig.media_ref
    return sig.relative_path


def _sha256_of_file(path: str | Path) -> str | None:
    import hashlib

    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def extract_source_signature(
    media_path: str | Path,
    metadata: dict[str, Any],
    *,
    ffmpeg_path: str | None = None,
    window_seconds: float = WINDOW_SECONDS_DEFAULT,
    blocks_per_second: int = ENVELOPE_BLOCKS_PER_SECOND,
    sample_rate: int = SIGNATURE_SAMPLE_RATE,
    include_sha256: bool = True,
    decoder: Callable[..., tuple[float, Any] | None] | None = None,
) -> SourceSignature:
    """Build a compact signature for one media source.

    ``decoder`` (optional) overrides window decoding for hermetic tests.
    """
    import numpy as np

    media_path = Path(media_path)
    rel = metadata.get("relative_path", media_path.name)
    source_id = _resolve_source_identity(metadata)
    media_ref = media_item_key(source_id, rel) if source_id is not None else None
    duration = metadata.get("duration_seconds")
    audio_info = metadata.get("audio") or {}
    video_info = metadata.get("video")

    decode = decoder or (lambda start, dur: decode_window(
        media_path,
        start_seconds=start,
        duration_seconds=dur,
        sample_rate=sample_rate,
        ffmpeg_path=ffmpeg_path,
    ))

    started = time.monotonic()
    windows: dict[str, Any] = {}
    quality: dict[str, Any] = {}
    for key in _window_offsets(duration, window_seconds):
        anchor = _window_anchor(key, duration, window_seconds)
        decoded = decode(anchor, window_seconds)
        if decoded is None:
            continue
        rate, samples = decoded
        windows[key] = envelope(samples, rate, blocks_per_second)
        quality[key] = analyze_quality(samples, rate)
    analysis_seconds = time.monotonic() - started

    sig = SourceSignature(
        relative_path=rel,
        category=metadata.get("category", "audio"),
        file_size_bytes=metadata.get("file_size_bytes"),
        duration_seconds=duration,
        sample_rate=(audio_info or {}).get("sample_rate"),
        channel_count=(audio_info or {}).get("channel_count"),
        codec=(audio_info or {}).get("codec"),
        timecode=metadata.get("timecode"),
        creation_time=metadata.get("creation_time"),
        has_video=bool(video_info),
        windows=windows,
        quality=quality,
        role=assign_source_role(rel, metadata.get("category", ""), bool(video_info), quality),
        analysis_seconds=analysis_seconds,
        source_id=source_id,
        media_ref=media_ref,
    )
    if include_sha256 and sig.file_size_bytes and sig.file_size_bytes <= (1 << 31):
        sig.sha256 = _sha256_of_file(media_path)
    return sig


def _best_window(sig: SourceSignature, preferred: str = "start") -> tuple[str, Any] | None:
    for key in (preferred, "middle", "end"):
        if key in sig.windows:
            return key, sig.windows[key]
    return None


def sync_sources(
    sig_a: SourceSignature,
    sig_b: SourceSignature,
    *,
    tolerance_seconds: float = SYNC_OFFSET_TOLERANCE_SECONDS,
) -> dict[str, Any]:
    """Estimate synchronization between two related sources.

    Returns a dict with ``offset_seconds`` (B relative to A), ``confidence``,
    ``method``, ``status``. Timecode evidence is preferred when genuinely
    available and internally consistent; otherwise audio correlation is used.
    """
    result: dict[str, Any] = {
        "offset_seconds": None,
        "confidence": None,
        "method": SYNC_METHOD_CORRELATION,
        "status": SYNC_STATUS_UNRESOLVED,
    }

    if sig_a.timecode and sig_b.timecode:
        tc_a = _timecode_to_seconds(sig_a.timecode)
        tc_b = _timecode_to_seconds(sig_b.timecode)
        if tc_a is not None and tc_b is not None:
            offset = tc_b - tc_a
            result["offset_seconds"] = round(offset, 3)
            result["method"] = SYNC_METHOD_TIMECODE
            result["confidence"] = 0.95
            result["status"] = SYNC_STATUS_RESOLVED
            return result

    if not sig_a.windows or not sig_b.windows:
        return result

    best: dict[str, Any] = {"confidence": -1.0}
    for key in ("start", "middle", "end"):
        env_a = sig_a.windows.get(key)
        env_b = sig_b.windows.get(key)
        if env_a is None or env_b is None or env_a.size < 2 or env_b.size < 2:
            continue
        lag, confidence = find_sync_lag(env_a, env_b, ENVELOPE_BLOCKS_PER_SECOND)
        if confidence > best["confidence"]:
            best = {
                "lag": lag,
                "confidence": confidence,
                "window": key,
                "offset_seconds": lag / ENVELOPE_BLOCKS_PER_SECOND,
            }

    if best["confidence"] < 0.0 or best["confidence"] < RELATED_CONFIDENCE_THRESHOLD:
        return result

    result["confidence"] = round(best["confidence"], 3)
    result["offset_seconds"] = round(best["offset_seconds"], 3)
    result["status"] = SYNC_STATUS_RESOLVED
    return result


def _timecode_to_seconds(timecode: str) -> float | None:
    parts = str(timecode).split(":")
    if len(parts) != 3:
        return None
    try:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    except ValueError:
        return None


def classify_relationship(
    sig_a: SourceSignature,
    sig_b: SourceSignature,
    sync: dict[str, Any],
) -> dict[str, Any]:
    """Classify the content relationship between two sources."""
    confidence = sync.get("confidence") or 0.0
    if sync.get("status") != SYNC_STATUS_RESOLVED or confidence < RELATED_CONFIDENCE_THRESHOLD:
        return {"relationship": RELATIONSHIP_UNRELATED, "confidence": round(confidence, 3)}

    dur_a = sig_a.duration_seconds or 0.0
    dur_b = sig_b.duration_seconds or 0.0
    same_length = max(dur_a, dur_b) > 0 and abs(dur_a - dur_b) / max(dur_a, dur_b) < 0.02

    duplicate_hint = False
    if sig_a.sha256 and sig_b.sha256 and sig_a.sha256 == sig_b.sha256:
        duplicate_hint = True

    if duplicate_hint or (same_length and confidence >= 0.90):
        return {
            "relationship": RELATIONSHIP_IDENTICAL,
            "confidence": round(confidence, 3),
            "duplicate": True,
        }

    if confidence >= RELATED_CONFIDENCE_THRESHOLD:
        complementary = _complementary_evidence(sig_a, sig_b)
        if complementary:
            return {
                "relationship": RELATIONSHIP_COMPLEMENTARY,
                "confidence": round(confidence, 3),
                "complementary": True,
            }
        return {
            "relationship": RELATIONSHIP_SAME_EVENT,
            "confidence": round(confidence, 3),
        }

    return {"relationship": RELATIONSHIP_UNCERTAIN, "confidence": round(confidence, 3)}


def _complementary_evidence(sig_a: SourceSignature, sig_b: SourceSignature) -> bool:
    """Weak evidence that sources cover different portions of an event."""
    roles = {sig_a.role, sig_b.role}
    if sig_a.has_video != sig_b.has_video and (sig_a.role != sig_b.role):
        return False
    return False


def source_quality_summary(sig: SourceSignature) -> dict[str, Any]:
    """Aggregate per-window quality metrics into one summary + label."""
    merged: dict[str, Any] = {}
    counts: dict[str, int] = {}
    for key, metrics in sig.quality.items():
        for name, value in metrics.items():
            if isinstance(value, (int, float)):
                merged[name] = merged.get(name, 0.0) + float(value)
                counts[name] = counts.get(name, 0) + 1
    summary: dict[str, Any] = {}
    for name in merged:
        if counts.get(name):
            summary[name] = round(merged[name] / counts[name], 4)
    return {"metrics": summary, "label": _label_quality(summary)}


def internal_rank_score(
    quality: dict[str, Any],
    duration_seconds: float | None,
    event_confidence: float | None,
) -> float:
    """Internal 0..1 ranking used to order sources (not shown verbatim)."""
    q = quality.get("metrics", {})
    score = 0.5
    score += QUALITY_TIER_BONUS.get(quality.get("label"), 0.0)
    rms_db = q.get("rms_db")
    if rms_db is not None:
        if -45.0 <= rms_db <= -12.0:
            score += 0.2
        elif -60.0 <= rms_db <= -8.0:
            score += 0.1
    score -= min(0.3, (q.get("clipping_fraction") or 0.0) * 3.0)
    score -= min(0.25, (q.get("silence_fraction") or 0.0) * 0.5)
    if q.get("dynamic_range_db") is not None and q["dynamic_range_db"] >= 8.0:
        score += 0.1
    coverage = 0.0
    if duration_seconds:
        coverage = min(1.0, duration_seconds / 3600.0)
    score += 0.1 * coverage
    if event_confidence is not None:
        score += 0.15 * event_confidence
    return round(max(0.0, min(1.0, score)), 3)


@dataclass
class SourceCluster:
    """A recording/session cluster of related sources."""

    session_id: str
    sources: list[SourceSignature] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    transcription_masters: list[str] = field(default_factory=list)
    duplicate_sources: list[str] = field(default_factory=list)
    alternate_sources: list[str] = field(default_factory=list)
    reference_source: str | None = None
    excluded_sources: list[str] = field(default_factory=list)
    unique_candidate_sources: list[str] = field(default_factory=list)
    uncertain_sources: list[str] = field(default_factory=list)
    dispositions: dict[str, str] = field(default_factory=dict)


def _session_id_for(relative_path: str) -> str:
    """Return the coarse recording/session bucket identity for a relative path.

    Delegates to :func:`session_boundary.coarse_session_id`, which derives a
    deterministic, portable identity from the meaningful upper lineage of the
    path and deliberately ignores generic card/container components (``CLIP``,
    ``M4ROOT``, ``Tarjeta 1``, ...). This replaces the former immediate-parent
    key that allowed unrelated trees to collide on generic folder names.
    """
    return coarse_session_id(relative_path)


def _classify_source_mode(candidates: list[dict[str, Any]]) -> list[str]:
    """Classify the candidate provenance mode.

    Returns a mode label and splits candidates into pre-guard identity
    evaluation before any physical path resolution. Never derives identity
    from a media root, absolute path or filename.
    """
    identities: set[str] = set()
    sees_legacy = False
    for item in candidates:
        source_id = _resolve_source_identity(item)
        if source_id is None:
            sees_legacy = True
        else:
            identities.add(source_id)
    if sees_legacy and identities:
        return ["MIXED"]
    if not identities:
        return ["LEGACY"]
    if len(identities) == 1:
        return ["SOURCE_AWARE_SINGLE_SOURCE"]
    return ["SOURCE_AWARE_MULTI_SOURCE"]


def _candidate_source_identities(candidates: list[dict[str, Any]]) -> set[str]:
    """Distinct canonical source identities present across the candidate set."""
    identities: set[str] = set()
    for item in candidates:
        ident = _resolve_source_identity(item)
        if ident is not None:
            identities.add(ident)
    return identities


def _normalize_source_root_map(
    media_root_by_source_id: Mapping[str, str | Path] | None,
) -> dict[str, Path] | None:
    """Validate and copy the transient source-root mapping.

    Structural validation is deterministic and filesystem-free: keys must be
    non-empty strings and values must be non-empty ``str`` or ``Path``. The
    caller mapping is never mutated; a normalized copy is returned.
    """
    if media_root_by_source_id is None:
        return None
    if not isinstance(media_root_by_source_id, Mapping):
        raise GroupingError(
            "INVALID_SOURCE_ROOT_MAP",
            "media_root_by_source_id must be a mapping",
        )
    normalized: dict[str, Path] = {}
    for key, value in media_root_by_source_id.items():
        if not isinstance(key, str) or not key.strip():
            raise GroupingError(
                "INVALID_SOURCE_ROOT_MAP",
                "source root map keys must be non-empty strings",
            )
        if isinstance(value, Path):
            root = value
        elif isinstance(value, str) and value.strip():
            root = Path(value)
        else:
            raise GroupingError(
                "INVALID_SOURCE_ROOT_MAP",
                "source root map values must be non-empty str or Path",
            )
        normalized[key] = root
    return normalized


def _resolve_grouping_media_path(
    item: dict[str, Any],
    *,
    source_identity: str | None,
    media_root: str | Path | None,
    media_root_by_source_id: dict[str, Path] | None,
    mode: str,
) -> Path:
    """Resolve the transient physical Path for a candidate item.

    In source-aware mapped mode the explicit source-root mapping is the strict
    physical authority and ``item["abs_path"]`` never overrides it. Legacy mode
    (and source-aware single-source without a map) preserve their existing
    ``abs_path``-preferred behavior.
    """
    if mode != "LEGACY" and media_root_by_source_id is not None:
        return media_root_by_source_id[source_identity] / item.get("relative_path", "")
    return Path(item.get("abs_path") or (Path(media_root) / item.get("relative_path", "")))


def group_related_media(
    metadata_results: list[dict[str, Any]],
    *,
    ffmpeg_path: str | None = None,
    media_root: str | Path | None = None,
    analyze_content: bool = True,
    signature_builder: Callable[..., SourceSignature] | None = None,
    max_sources_per_cluster: int = 16,
    media_root_by_source_id: Mapping[str, str | Path] | None = None,
) -> list[SourceCluster]:
    """Group related media into recording/session clusters.

    Tentative groups come from session directory context; content correlation
    then confirms relationships and enables duplicate/master decisions. When
    ``analyze_content`` is False no decoding is performed (metadata-only).
    """
    import numpy as np

    candidates = [
        r for r in metadata_results
        if r.get("category") in ("audio", "video")
        and (r.get("duration_seconds") or 0) > 0
    ]
    [mode] = _classify_source_mode(candidates)
    if mode == "MIXED":
        raise GroupingError(
            "MIXED_SOURCE_IDENTITY",
            "cannot mix legacy and source-aware candidates in one grouping call",
        )
    root_map = _normalize_source_root_map(media_root_by_source_id)
    if mode == "LEGACY":
        if root_map is not None:
            raise GroupingError(
                "LEGACY_MODE_WITH_SOURCE_ROOT_MAP",
                "legacy candidates carry no source identity to select a root map entry",
            )
    elif root_map is not None:
        missing = sorted(_candidate_source_identities(candidates) - set(root_map))
        if missing:
            raise GroupingError(
                "MISSING_SOURCE_ROOT_MAP",
                "root map missing source identities: " + ", ".join(missing),
            )
    elif mode == "SOURCE_AWARE_MULTI_SOURCE":
        raise GroupingError(
            "MULTI_SOURCE_REQUIRES_SOURCE_ROOT_MAP",
            "multiple source identities require media_root_by_source_id (MS2C2)",
        )

    by_session: dict[str, list[dict[str, Any]]] = {}
    for item in candidates:
        sid = _session_id_for(item.get("relative_path", ""))
        by_session.setdefault(sid, []).append(item)

    build = signature_builder or (lambda path, meta, i: _default_signature_builder(
        path, meta, ffmpeg_path=ffmpeg_path
    ))

    clusters: list[SourceCluster] = []
    for sid, items in sorted(by_session.items()):
        items = sorted(items, key=lambda x: x.get("file_size_bytes") or 0)
        signatures: list[SourceSignature] = []
        for i, item in enumerate(items):
            if len(signatures) >= max_sources_per_cluster:
                break
            source_identity = _resolve_source_identity(item) if mode != "LEGACY" else None
            path = _resolve_grouping_media_path(
                item,
                source_identity=source_identity,
                media_root=media_root,
                media_root_by_source_id=root_map,
                mode=mode,
            )
            sig = build(path, item, i)
            sig = _canonicalize_signature_identity(sig, item)
            if sig is None or not sig.windows:
                continue
            signatures.append(sig)
        if not signatures:
            continue
        cluster = _finalize_cluster(signatures, sid)
        clusters.append(cluster)
    return clusters


def _canonicalize_signature_identity(
    sig: SourceSignature, item: dict[str, Any]
) -> SourceSignature:
    """Enforce metadata as the single identity authority over a built signature.

    For source-aware items the canonical ``source_id``/``media_ref`` are copied
    in when absent, accepted when equal, and any conflict fails closed. An
    injected signature builder is never an identity authority.
    """
    source_id = _resolve_source_identity(item)
    if source_id is None:
        if sig.source_id is not None or sig.media_ref is not None:
            raise GroupingError(
                "SOURCE_IDENTITY_CONFLICT",
                "legacy metadata must not fabricate a source identity",
            )
        return sig
    expected_media_ref = media_item_key(source_id, item.get("relative_path", ""))
    if sig.media_ref is not None:
        if sig.media_ref != expected_media_ref:
            raise GroupingError(
                "SOURCE_IDENTITY_CONFLICT",
                "built signature media_ref conflicts with metadata authority",
            )
    else:
        sig.media_ref = expected_media_ref
    if sig.source_id is not None:
        if sig.source_id != source_id:
            raise GroupingError("SOURCE_IDENTITY_CONFLICT")
    else:
        sig.source_id = source_id
    return sig


def _default_signature_builder(
    path: str | Path,
    metadata: dict[str, Any],
    ffmpeg_path: str | None,
) -> SourceSignature:
    return extract_source_signature(path, metadata, ffmpeg_path=ffmpeg_path)


def _finalize_cluster(
    signatures: list[SourceSignature],
    session_id: str,
) -> SourceCluster:
    if not signatures:
        raise GroupingError("EMPTY_CLUSTER")
    _assert_consistent_mode(signatures)
    legacy = signatures[0].source_id is None
    cluster = SourceCluster(session_id=session_id, sources=signatures)

    relations: list[dict[str, Any]] = []
    duplicate_ids: set[str] = set()

    for i, sig_b in enumerate(signatures):
        for sig_a in signatures[:i]:
            sync = sync_sources(sig_a, sig_b)
            rel = classify_relationship(sig_a, sig_b, sync)
            relation = {
                "a": sig_a.relative_path,
                "b": sig_b.relative_path,
                "relationship": rel["relationship"],
                "confidence": rel["confidence"],
                "sync": sync,
            }
            if not legacy:
                relation["a_media_ref"] = member_identity(sig_a)
                relation["b_media_ref"] = member_identity(sig_b)
            relations.append(relation)
            if rel.get("duplicate"):
                if sig_b.sha256 and sig_a.sha256 and sig_b.sha256 == sig_a.sha256:
                    duplicate_ids.add(member_identity(sig_b))

    cluster.relationships = relations

    # Affirmative dialogue evidence: a source belongs to the same event when it
    # has at least one resolved, above-threshold relationship (identical, same
    # event, or complementary) with any other source in the session.
    with_a = "a_media_ref" if not legacy else "a"
    with_b = "b_media_ref" if not legacy else "b"
    dialogue_related: set[str] = set()
    for relation in relations:
        if relation["sync"].get("status") != SYNC_STATUS_RESOLVED:
            continue
        if relation["confidence"] < RELATED_CONFIDENCE_THRESHOLD:
            continue
        if relation["relationship"] in (RELATIONSHIP_IDENTICAL, RELATIONSHIP_SAME_EVENT, RELATIONSHIP_COMPLEMENTARY):
            dialogue_related.add(relation[with_a])
            dialogue_related.add(relation[with_b])

    dialogue_masters: dict[str, float] = {}
    unique_masters: dict[str, float] = {}
    dispositions: dict[str, str] = {}

    for sig in signatures:
        key = member_identity(sig)
        if key in duplicate_ids:
            dispositions[key] = DISPOSITION_DUPLICATE
            continue
        q = source_quality_summary(sig)
        if key in dialogue_related:
            dispositions[key] = DISPOSITION_DIALOGUE
            event_conf = _best_event_confidence(sig, relations)
            score = internal_rank_score(q, sig.duration_seconds, event_conf)
            score += ROLE_MASTER_PREFERENCE.get(sig.role, 0.0)
            dialogue_masters[key] = score
            continue
        # Not dialogue-related. A source may be skipped only with affirmative
        # evidence it needs no independent transcription: effectively silent or
        # technical feed. Otherwise it must remain a candidate, never silently
        # discarded merely for being UNRELATED/UNRESOLVED.
        if _is_effectively_silent(sig):
            dispositions[key] = DISPOSITION_TECHNICAL_OR_EMPTY
            continue
        if sig.windows and _has_content_evidence(sig):
            dispositions[key] = DISPOSITION_UNIQUE_CONTENT
            event_conf = _best_event_confidence(sig, relations)
            score = internal_rank_score(q, sig.duration_seconds, event_conf)
            score += ROLE_MASTER_PREFERENCE.get(sig.role, 0.0)
            unique_masters[key] = score
            continue
        dispositions[key] = DISPOSITION_UNCERTAIN

    dialogue_ordered = sorted(dialogue_masters.items(), key=lambda kv: kv[1], reverse=True)
    unique_ordered = sorted(unique_masters.items(), key=lambda kv: kv[1], reverse=True)
    selected = [p for p, _ in dialogue_ordered[:1]] + [p for p, _ in unique_ordered]
    cluster.transcription_masters = selected
    cluster.reference_source = (dialogue_ordered or unique_ordered or [("", 0.0)])[0][0] or None
    cluster.duplicate_sources = sorted(duplicate_ids)
    cluster.alternate_sources = sorted(
        key for key, disp in dispositions.items()
        if disp in (DISPOSITION_DIALOGUE,) and key not in cluster.transcription_masters
    )
    cluster.excluded_sources = sorted(
        key for key, disp in dispositions.items()
        if disp == DISPOSITION_TECHNICAL_OR_EMPTY
    )
    cluster.unique_candidate_sources = sorted(
        key for key, disp in dispositions.items()
        if disp == DISPOSITION_UNIQUE_CONTENT
    )
    cluster.uncertain_sources = sorted(
        key for key, disp in dispositions.items()
        if disp == DISPOSITION_UNCERTAIN
    )
    cluster.dispositions = dict(dispositions)
    return cluster


def _assert_consistent_mode(signatures: list[SourceSignature]) -> None:
    """Mixed legacy/source-aware members inside one cluster fail closed."""
    legacy_any = any(sig.source_id is None for sig in signatures)
    aware_any = any(sig.source_id is not None for sig in signatures)
    if legacy_any and aware_any:
        raise GroupingError(
            "MIXED_SOURCE_IDENTITY",
            "cannot mix legacy and source-aware signatures in one cluster",
        )


def _is_effectively_silent(sig: SourceSignature) -> bool:
    """Affirmative evidence that a source carries no meaningful dialogue."""
    q = source_quality_summary(sig)
    metrics = q.get("metrics", {})
    silence = metrics.get("silence_fraction")
    rms_db = metrics.get("rms_db")
    if silence is not None and silence >= 0.95:
        return True
    if silence is not None and silence >= 0.85 and (rms_db is None or rms_db < -60.0):
        return True
    return False


def _has_content_evidence(sig: SourceSignature) -> bool:
    """Whether sampled windows contain any measurable audio activity."""
    for key, env in sig.windows.items():
        import numpy as np

        arr = np.asarray(env, dtype=np.float32)
        if arr.size and float(np.max(arr)) > 1e-6:
            return True
    return False


def _best_event_confidence(
    sig: SourceSignature,
    relationships: list[dict[str, Any]],
) -> float | None:
    key = member_identity(sig)
    legacy = sig.source_id is None
    left = "a_media_ref" if not legacy else "a"
    right = "b_media_ref" if not legacy else "b"
    confidences = [
        rel["confidence"]
        for rel in relationships
        if rel[left] == key or rel[right] == key
    ]
    return max(confidences) if confidences else None


def build_sync_manifest(
    cluster: SourceCluster,
    *,
    media_root: str | Path,
) -> dict[str, Any]:
    """Build a producer/sync manifest for a session cluster."""
    reference = cluster.reference_source or (cluster.transcription_masters or [None])[0]
    rel_by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    for rel in cluster.relationships:
        rel_by_pair[(rel["a"], rel["b"])] = rel

    sources: list[dict[str, Any]] = []
    for sig in cluster.sources:
        path = sig.relative_path
        if path == reference:
            continue
        pair = (reference, path) if (reference, path) in rel_by_pair else (path, reference)
        rel = rel_by_pair.get(pair)
        sources.append({
            "source": path,
            "relationship": rel["relationship"] if rel else RELATIONSHIP_UNRELATED,
            "sync_method": rel["sync"].get("method") if rel else SYNC_METHOD_CORRELATION,
            "offset_seconds": rel["sync"].get("offset_seconds") if rel else None,
            "confidence": rel["sync"].get("confidence") if rel else None,
            "sync_status": rel["sync"].get("status") if rel else SYNC_STATUS_UNRESOLVED,
            "quality": source_quality_summary(sig)["label"],
            "role": sig.role,
            "timecode": sig.timecode,
        })

    return {
        "schema_version": SYNC_MANIFEST_SCHEMA_VERSION,
        "session_id": cluster.session_id,
        "reference": reference,
        "transcription_masters": list(cluster.transcription_masters),
        "duplicate_sources": list(cluster.duplicate_sources),
        "alternate_sources": list(cluster.alternate_sources),
        "excluded_sources": list(cluster.excluded_sources),
        "unique_candidate_sources": list(cluster.unique_candidate_sources),
        "uncertain_sources": list(cluster.uncertain_sources),
        "sources": sources,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "privacy": {
            "source_media_modified": False,
            "network_used": False,
            "database_used": False,
        },
    }


def recommend_transcription_sources(
    clusters: list[SourceCluster],
) -> list[str]:
    """Return the full transcription source set (masters only, non-duplicative)."""
    masters: list[str] = []
    for cluster in clusters:
        masters.extend(cluster.transcription_masters)
    return masters


def all_related_source_paths(clusters: list[SourceCluster]) -> list[str]:
    paths: list[str] = []
    for cluster in clusters:
        paths.extend(sig.relative_path for sig in cluster.sources)
    return sorted(set(paths))


def format_cluster_summary(cluster: SourceCluster) -> dict[str, Any]:
    """Producer-facing summary of a session cluster."""
    source_rows = []
    for sig in cluster.sources:
        q = source_quality_summary(sig)
        is_master = sig.relative_path in cluster.transcription_masters
        is_duplicate = sig.relative_path in cluster.duplicate_sources
        source_rows.append({
            "source": sig.relative_path,
            "role": sig.role,
            "quality": q["label"],
            "disposition": cluster.dispositions.get(
                sig.relative_path,
                "UNCERTAIN" if sig.relative_path in cluster.uncertain_sources else "DIALOGUE",
            ),
            "transcription_master": is_master,
            "duplicate": is_duplicate,
            "alternate": sig.relative_path in cluster.alternate_sources,
            "excluded": sig.relative_path in cluster.excluded_sources,
            "unique_candidate": sig.relative_path in cluster.unique_candidate_sources,
        })
    return {
        "session_id": cluster.session_id,
        "source_count": len(cluster.sources),
        "masters": list(cluster.transcription_masters),
        "duplicates": list(cluster.duplicate_sources),
        "alternates": list(cluster.alternate_sources),
        "excluded": list(cluster.excluded_sources),
        "unique_candidates": list(cluster.unique_candidate_sources),
        "uncertain": list(cluster.uncertain_sources),
        "sources": source_rows,
    }


__all__ = [
    "SOURCE_SIGNATURE_ALGORITHM_VERSION",
    "SYNC_MANIFEST_SCHEMA_VERSION",
    "WINDOW_SECONDS_DEFAULT",
    "SIGNATURE_SAMPLE_RATE",
    "ENVELOPE_BLOCKS_PER_SECOND",
    "FINE_REFINE_SEARCH_SECONDS",
    "FINE_REFINE_WINDOW_SECONDS",
    "SYNC_OFFSET_TOLERANCE_SECONDS",
    "MIN_OVERLAP_ENVELOPE_SAMPLES",
    "HIGH_CONFIDENCE_THRESHOLD",
    "RELATED_CONFIDENCE_THRESHOLD",
    "MASTER_EVENT_CONFIDENCE_THRESHOLD",
    "RELATIONSHIP_IDENTICAL",
    "RELATIONSHIP_SAME_EVENT",
    "RELATIONSHIP_COMPLEMENTARY",
    "RELATIONSHIP_UNRELATED",
    "RELATIONSHIP_UNCERTAIN",
    "DISPOSITION_DIALOGUE",
    "DISPOSITION_DUPLICATE",
    "DISPOSITION_ALTERNATE",
    "DISPOSITION_TECHNICAL_OR_EMPTY",
    "DISPOSITION_UNIQUE_CONTENT",
    "DISPOSITION_UNCERTAIN",
    "SYNC_METHOD_TIMECODE",
    "SYNC_METHOD_CORRELATION",
    "SYNC_STATUS_RESOLVED",
    "SYNC_STATUS_UNRESOLVED",
    "ROLE_CAMERA_REFERENCE",
    "ROLE_EXTERNAL_MIX",
    "ROLE_ISOLATED_MIC",
    "ROLE_DUPLICATE",
    "ROLE_UNKNOWN",
    "QUALITY_EXCELENTE",
    "QUALITY_BUENA",
    "QUALITY_REFERENCIA",
    "QUALITY_DEFICIENTE",
    "GroupingError",
    "SourceCluster",
    "SourceSignature",
    "analyze_quality",
    "assign_source_role",
    "build_sync_manifest",
    "classify_relationship",
    "extract_source_signature",
    "find_sync_lag",
    "format_cluster_summary",
    "group_related_media",
    "internal_rank_score",
    "member_identity",
    "recommend_transcription_sources",
    "refine_offset_with_samples",
    "source_quality_summary",
    "sync_sources",
]