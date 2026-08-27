#!/usr/bin/env python3
"""CID Editorial Intelligence - Transcription V1.

Consumes an Audio Extraction V1 temporary PCM WAV mono 16 kHz s16le (while the
Audio Extraction context manager is open) and produces a structured,
timestamped transcript through a minimal backend abstraction. The faster-whisper
backend is imported lazily so this module works without the package installed;
tests use a deterministic fake backend.
"""

from __future__ import annotations

import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Iterator

PHASE = "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPTION.V1"

TRANSCRIPTION_ENGINE = "faster-whisper"
TRANSCRIPTION_TASK = "transcribe"
MODEL_REFERENCE_POLICY = "EXPLICIT_LOCAL_MODEL_DIRECTORY"

STATE_TRANSCRIPTION_COMPLETED = "TRANSCRIPTION_COMPLETED"
STATE_TRANSCRIPTION_FAILED = "TRANSCRIPTION_FAILED"
STATE_TRANSCRIPTION_MODEL_NOT_AVAILABLE = "MODEL_NOT_AVAILABLE"
STATE_TRANSCRIPTION_ENGINE_NOT_AVAILABLE = "ENGINE_NOT_AVAILABLE"
STATE_TRANSCRIPTION_INVALID_AUDIO_INPUT = "INVALID_AUDIO_INPUT"
STATE_TRANSCRIPTION_CANCELLED = "TRANSCRIPTION_CANCELLED"

CPU_COMPUTE_TYPE = "int8"
CUDA_COMPUTE_TYPE = "float16"

SEGMENT_DURATION_TOLERANCE_SECONDS = 2.0
WORD_TIMESTAMPS_DEFAULT = False
ENGINE_NATIVE_VAD_DEFAULT = True

_REMOTE_MODEL_NAME_PATTERN = re.compile(
    r"^(tiny|base|small|medium|large|large-v1|large-v2|large-v3|turbo)$"
)

ERROR_CODE_TRANSCRIPTION_FAILED = "transcription_failed"
ERROR_CODE_INVALID_BACKEND_OUTPUT = "invalid_backend_output"
ERROR_CODE_MODEL_NOT_AVAILABLE = "model_not_available"
ERROR_CODE_ENGINE_NOT_AVAILABLE = "engine_not_available"
ERROR_CODE_INVALID_AUDIO_INPUT = "invalid_audio_input"


class TranscriptionBackendError(Exception):
    """Structured backend failure with a sanitized message."""

    def __init__(self, error_code: str, message_sanitized: str) -> None:
        super().__init__(message_sanitized)
        self.error_code = error_code
        self.message_sanitized = message_sanitized


def _sanitize_model_identifier(model_local_path: str | Path | None) -> str | None:
    if model_local_path is None:
        return None
    text = str(model_local_path).strip()
    if not text:
        return None
    return Path(text).name or TRANSCRIPTION_ENGINE


@dataclass
class TranscriptionRequest:
    asset_id: str
    temporary_audio_path: str | Path
    source_audio_stream_index: int | None = None
    extracted_audio_start_seconds: float = 0.0
    audio_duration_seconds: float | None = None
    language_hint: str | None = None
    model_local_path: str | Path | None = None
    device: str = "cpu"
    timeout_seconds: float | None = None


def _validate_audio_input(request: TranscriptionRequest) -> str | None:
    if request.temporary_audio_path is None:
        return ERROR_CODE_INVALID_AUDIO_INPUT
    if not str(request.temporary_audio_path).strip():
        return ERROR_CODE_INVALID_AUDIO_INPUT
    return None


def map_segment_to_source(
    segment: dict[str, Any],
    extracted_audio_start_seconds: float,
) -> dict[str, Any]:
    """Map an STT-audio-relative segment to source-media-relative seconds."""
    anchor = float(extracted_audio_start_seconds or 0.0)
    return {
        **segment,
        "source_start_seconds": float(segment["start_seconds"]) + anchor,
        "source_end_seconds": float(segment["end_seconds"]) + anchor,
    }


class TranscriptionBackend(ABC):
    @property
    @abstractmethod
    def engine_name(self) -> str:
        raise NotImplementedError

    @property
    def model_identifier_sanitized(self) -> str | None:
        return None

    @abstractmethod
    def transcribe(
        self,
        wav_path: str | Path,
        *,
        language_hint: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


class FakeTranscriptionBackend(TranscriptionBackend):
    """Deterministic backend used exclusively by tests."""

    def __init__(
        self,
        segments: list[dict[str, Any]] | None = None,
        detected_language: str = "es",
        language_probability: float = 0.95,
    ) -> None:
        self._segments = list(segments or [])
        self.detected_language = detected_language
        self.language_probability = language_probability

    @property
    def engine_name(self) -> str:
        return "fake"

    def transcribe(
        self,
        wav_path: str | Path,
        *,
        language_hint: str | None = None,
    ) -> dict[str, Any]:
        return {
            "detected_language": self.detected_language,
            "language_probability": self.language_probability,
            "segments": iter(list(self._segments)),
        }


class FasterWhisperTranscriptionBackend(TranscriptionBackend):
    """Lazy productive backend for faster-whisper; never auto-downloads."""

    def __init__(
        self,
        model_local_path: str | Path,
        device: str = "cpu",
        compute_type: str | None = None,
        *,
        vad_filter: bool = ENGINE_NATIVE_VAD_DEFAULT,
        word_timestamps: bool = WORD_TIMESTAMPS_DEFAULT,
    ) -> None:
        self.model_local_path = model_local_path
        self.device = device
        if compute_type is None:
            compute_type = CUDA_COMPUTE_TYPE if device == "cuda" else CPU_COMPUTE_TYPE
        self.compute_type = compute_type
        self.vad_filter = vad_filter
        self.word_timestamps = word_timestamps

    @property
    def engine_name(self) -> str:
        return TRANSCRIPTION_ENGINE

    @property
    def model_identifier_sanitized(self) -> str | None:
        return _sanitize_model_identifier(self.model_local_path)

    @staticmethod
    def _segment_to_payload(segment: Any) -> dict[str, Any]:
        """Normalize an engine segment (dict or attribute object) to the contract."""
        if isinstance(segment, dict):
            words = segment.get("words") or []
            payload = {
                "segment_index": segment.get("segment_index") or segment.get("id"),
                "start_seconds": segment.get("start_seconds", segment.get("start")),
                "end_seconds": segment.get("end_seconds", segment.get("end")),
                "text": str(segment.get("text") or ""),
            }
            if words:
                payload["words"] = [
                    FasterWhisperTranscriptionBackend._word_to_payload(word)
                    for word in words
                ]
            return payload
        words = getattr(segment, "words", None) or []
        payload = {
            "segment_index": getattr(segment, "id", None),
            "start_seconds": float(segment.start),
            "end_seconds": float(segment.end),
            "text": str(getattr(segment, "text", "") or ""),
        }
        if words:
            payload["words"] = [
                FasterWhisperTranscriptionBackend._word_to_payload(word)
                for word in words
            ]
        return payload

    @staticmethod
    def _word_to_payload(word: Any) -> dict[str, Any]:
        if isinstance(word, dict):
            return {
                "word": str(word.get("word") or ""),
                "start_seconds": word.get("start_seconds", word.get("start")),
                "end_seconds": word.get("end_seconds", word.get("end")),
            }
        return {
            "word": str(getattr(word, "word", "") or ""),
            "start_seconds": float(getattr(word, "start", 0.0)),
            "end_seconds": float(getattr(word, "end", 0.0)),
        }

    def _validate_local_model_reference(self) -> None:
        reference = str(self.model_local_path or "").strip()
        if not reference:
            raise TranscriptionBackendError(
                ERROR_CODE_MODEL_NOT_AVAILABLE,
                "a local model directory is required",
            )
        if _REMOTE_MODEL_NAME_PATTERN.match(reference):
            raise TranscriptionBackendError(
                ERROR_CODE_MODEL_NOT_AVAILABLE,
                "remote model names are not allowed; provide a local model directory",
            )
        if not (
            Path(reference).is_absolute()
            or "/" in reference
            or "\\" in reference
        ):
            raise TranscriptionBackendError(
                ERROR_CODE_MODEL_NOT_AVAILABLE,
                "model reference must be an explicit local directory",
            )
        if not Path(reference).is_dir():
            raise TranscriptionBackendError(
                ERROR_CODE_MODEL_NOT_AVAILABLE,
                "local model directory does not exist",
            )

    def transcribe(
        self,
        wav_path: str | Path,
        *,
        language_hint: str | None = None,
    ) -> dict[str, Any]:
        self._validate_local_model_reference()
        try:
            from faster_whisper import WhisperModel  # lazy, only on real use
        except ImportError as exc:
            raise TranscriptionBackendError(
                ERROR_CODE_ENGINE_NOT_AVAILABLE,
                "faster-whisper engine is not installed",
            ) from exc
        model = WhisperModel(
            str(Path(str(self.model_local_path))),
            device=self.device,
            compute_type=self.compute_type,
        )
        segments, info = model.transcribe(
            str(wav_path),
            language=language_hint,
            task=TRANSCRIPTION_TASK,
            word_timestamps=self.word_timestamps,
            vad_filter=self.vad_filter,
        )
        return {
            "detected_language": getattr(info, "language", language_hint),
            "language_probability": getattr(info, "language_probability", None),
            "segments": iter(
                self._segment_to_payload(segment) for segment in segments
            ),
        }


def _validate_segment(
    segment: dict[str, Any],
    expected_index: int,
    audio_duration_seconds: float | None,
) -> tuple[int, float, float]:
    seg_index = segment.get("segment_index", expected_index)
    if seg_index is None:
        seg_index = expected_index
    if not isinstance(seg_index, int) or seg_index < 0:
        raise TranscriptionBackendError(
            ERROR_CODE_INVALID_BACKEND_OUTPUT,
            "invalid segment index",
        )
    start = segment.get("start_seconds")
    end = segment.get("end_seconds")
    text = segment.get("text")
    if isinstance(start, bool) or not isinstance(start, (int, float)) or start < 0:
        raise TranscriptionBackendError(
            ERROR_CODE_INVALID_BACKEND_OUTPUT,
            "invalid segment start",
        )
    if isinstance(end, bool) or not isinstance(end, (int, float)) or end < start:
        raise TranscriptionBackendError(
            ERROR_CODE_INVALID_BACKEND_OUTPUT,
            "invalid segment end",
        )
    if not isinstance(text, str):
        raise TranscriptionBackendError(
            ERROR_CODE_INVALID_BACKEND_OUTPUT,
            "invalid segment text",
        )
    if (
        audio_duration_seconds is not None
        and end > audio_duration_seconds + SEGMENT_DURATION_TOLERANCE_SECONDS
    ):
        raise TranscriptionBackendError(
            ERROR_CODE_INVALID_BACKEND_OUTPUT,
            "segment exceeds audio duration",
        )
    return seg_index, float(start), float(end)


def _status_for_error(error_code: str) -> str:
    if error_code == ERROR_CODE_ENGINE_NOT_AVAILABLE:
        return STATE_TRANSCRIPTION_ENGINE_NOT_AVAILABLE
    if error_code == ERROR_CODE_MODEL_NOT_AVAILABLE:
        return STATE_TRANSCRIPTION_MODEL_NOT_AVAILABLE
    if error_code == ERROR_CODE_INVALID_AUDIO_INPUT:
        return STATE_TRANSCRIPTION_INVALID_AUDIO_INPUT
    return STATE_TRANSCRIPTION_FAILED


class TranscriptionResult:
    def __init__(
        self,
        payload: dict[str, Any],
        segments: list[dict[str, Any]] | None = None,
    ) -> None:
        self._payload = payload
        self._segments = list(segments or [])

    @property
    def state(self) -> str | None:
        return self._payload.get("status")

    @property
    def segments(self) -> list[dict[str, Any]]:
        return list(self._segments)

    @property
    def error(self) -> dict[str, Any]:
        return dict(self._payload.get("error") or {})

    def to_dict(self) -> dict[str, Any]:
        return {**dict(self._payload), "segments": list(self._segments)}


def transcribe(
    request: TranscriptionRequest,
    backend: TranscriptionBackend,
    *,
    segment_callback: Any = None,
    cancel_event: Any = None,
) -> TranscriptionResult:
    """Run transcription and materialize validated segments.

    ``segment_callback`` (optional) is invoked for every accepted source-mapped
    segment as ``segment_callback(segment)`` with the normalized dict containing
    ``source_end_seconds``. Used by the producer GUI to show truthful progress.

    ``cancel_event`` (optional) exposes ``is_set()`` and is checked between
    segments (a threading.Event in-process, or a file-backed sentinel inside a
    dedicated worker process). When set, transcription stops early and returns
    ``STATE_TRANSCRIPTION_CANCELLED`` without publishing completed outputs.
    """
    payload: dict[str, Any] = {
        "phase": PHASE,
        "status": None,
        "asset_id": request.asset_id,
        "source_audio_stream_index": request.source_audio_stream_index,
        "detected_language": None,
        "language_probability": None,
        "audio_duration_seconds": request.audio_duration_seconds,
        "timeout_seconds": request.timeout_seconds,
        "error": {
            "error_code": None,
            "stage": None,
            "message_sanitized": None,
            "engine": backend.engine_name,
            "model_identifier_sanitized": None,
        },
        "warnings": [],
    }

    invalid_code = _validate_audio_input(request)
    if invalid_code is not None:
        payload["status"] = STATE_TRANSCRIPTION_INVALID_AUDIO_INPUT
        payload["error"] = {
            "error_code": invalid_code,
            "stage": "validation",
            "message_sanitized": "temporary audio path is missing",
            "engine": backend.engine_name,
            "model_identifier_sanitized": backend.model_identifier_sanitized,
        }
        return TranscriptionResult(payload)

    try:
        backend_output = backend.transcribe(
            request.temporary_audio_path,
            language_hint=request.language_hint,
        )
    except TranscriptionBackendError as exc:
        payload["status"] = _status_for_error(exc.error_code)
        payload["error"] = {
            "error_code": exc.error_code,
            "stage": "backend",
            "message_sanitized": exc.message_sanitized,
            "engine": backend.engine_name,
            "model_identifier_sanitized": backend.model_identifier_sanitized,
        }
        return TranscriptionResult(payload)
    except Exception:
        payload["status"] = STATE_TRANSCRIPTION_FAILED
        payload["error"] = {
            "error_code": ERROR_CODE_TRANSCRIPTION_FAILED,
            "stage": "backend",
            "message_sanitized": "backend failed unexpectedly",
            "engine": backend.engine_name,
            "model_identifier_sanitized": backend.model_identifier_sanitized,
        }
        return TranscriptionResult(payload)

    payload["error"]["model_identifier_sanitized"] = backend.model_identifier_sanitized

    detected_language = backend_output.get("detected_language")
    language_probability = backend_output.get("language_probability")
    payload["detected_language"] = (
        detected_language if detected_language is not None else request.language_hint
    )
    payload["language_probability"] = language_probability

    raw_segments: Iterator[dict[str, Any]] = backend_output.get("segments") or iter([])
    materialized: list[dict[str, Any]] = []
    previous_index: int | None = None
    previous_start: float | None = None
    for expected_index, raw in enumerate(raw_segments):
        if cancel_event is not None and cancel_event.is_set():
            payload["status"] = STATE_TRANSCRIPTION_CANCELLED
            payload["segments"] = []
            return TranscriptionResult(payload, segments=[])
        try:
            seg_index, start, end = _validate_segment(
                raw,
                expected_index,
                request.audio_duration_seconds,
            )
        except TranscriptionBackendError as exc:
            payload["status"] = STATE_TRANSCRIPTION_FAILED
            payload["error"] = {
                "error_code": exc.error_code,
                "stage": "backend",
                "message_sanitized": exc.message_sanitized,
                "engine": backend.engine_name,
                "model_identifier_sanitized": backend.model_identifier_sanitized,
            }
            return TranscriptionResult(payload)

        if previous_index is not None and seg_index < previous_index:
            payload["status"] = STATE_TRANSCRIPTION_FAILED
            payload["error"] = {
                "error_code": ERROR_CODE_INVALID_BACKEND_OUTPUT,
                "stage": "backend",
                "message_sanitized": "segments are not in ascending index order",
                "engine": backend.engine_name,
                "model_identifier_sanitized": backend.model_identifier_sanitized,
            }
            return TranscriptionResult(payload)
        if previous_start is not None and start < previous_start:
            payload["status"] = STATE_TRANSCRIPTION_FAILED
            payload["error"] = {
                "error_code": ERROR_CODE_INVALID_BACKEND_OUTPUT,
                "stage": "backend",
                "message_sanitized": "segment timestamps are not monotonic",
                "engine": backend.engine_name,
                "model_identifier_sanitized": backend.model_identifier_sanitized,
            }
            return TranscriptionResult(payload)

        normalized = {
            "segment_index": seg_index,
            "start_seconds": start,
            "end_seconds": end,
            "text": str(raw.get("text")),
        }
        if raw.get("words"):
            normalized["words"] = list(raw["words"])
        source_segment = map_segment_to_source(
            normalized, request.extracted_audio_start_seconds
        )
        materialized.append(source_segment)
        if segment_callback is not None:
            segment_callback(source_segment)
        previous_index = seg_index
        previous_start = start

    payload["status"] = STATE_TRANSCRIPTION_COMPLETED
    payload["segments"] = materialized
    return TranscriptionResult(payload, segments=materialized)
