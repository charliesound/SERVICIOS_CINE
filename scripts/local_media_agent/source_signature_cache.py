"""CID Local Media Agent — project-scoped SourceSignature persistence cache.

This module owns the *disposable* signature-content cache only. It stores
serialized :class:`SourceSignature` objects so that a later, unchanged scan can
reuse already-computed source signatures instead of re-decoding media.

Important architectural boundary
--------------------------------
The cache is a performance optimization, never project authority. Its format,
schema and algorithm versions are tracked separately:

- ``SOURCE_SIGNATURE_CACHE_FORMAT`` / ``SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION``
  describe the structure of the cache file itself.
- ``SOURCE_SIGNATURE_ALGORITHM_VERSION`` (owned by
  ``audio_source_intelligence``) describes the semantics of the stored
  signatures and invalidates stale entries when the analysis algorithm changes.

Cache identity is the canonical ``media_ref`` (produced by
``media_catalog.media_item_key(source_id, relative_path)``). No absolute path,
current location, drive letter, alias or display label participates in the key
or in eligibility. Reuse validation is limited to the cheap fingerprint
``(size, mtime_ns)`` plus algorithm/configuration version.

``analysis_seconds`` is stored verbatim but is diagnostic-only and never used
for eligibility. SHA-256 is persisted exactly as produced (``None`` is legal and
valid) and no separate SHA cache or content-duplicate index is maintained.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from scripts.local_media_agent.audio_source_intelligence import (
    ENVELOPE_BLOCKS_PER_SECOND,
    SIGNATURE_SAMPLE_RATE,
    SOURCE_SIGNATURE_ALGORITHM_VERSION,
    WINDOW_SECONDS_DEFAULT,
    SourceSignature,
)
from scripts.local_media_agent.local_project import (
    atomic_write_json,
    project_path,
    validate_project_id,
)

SOURCE_SIGNATURE_CACHE_FORMAT = "CID_SOURCE_SIGNATURE_CACHE"
SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION = 1
SOURCE_SIGNATURE_CACHE_FILENAME = "source_signature_cache.json"

CID_SOURCE_SIGNATURE_CACHE_INVALID = "CID_SOURCE_SIGNATURE_CACHE_INVALID"
CID_SOURCE_SIGNATURE_CACHE_PROJECT_MISMATCH = "CID_SOURCE_SIGNATURE_CACHE_PROJECT_MISMATCH"
CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID = "CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID"

# Canonical extraction options that affect SourceSignature output and therefore
# participate in cache validation. ``decoder`` is normalized to ``None`` (the
# canonical ffmpeg window-decoding path); a non-None callable is never
# representable as JSON and is therefore never part of a canonical cache entry.
_CANONICAL_SIGNATURE_CONFIG_KEYS = (
    "window_seconds",
    "blocks_per_second",
    "sample_rate",
    "include_sha256",
    "decoder",
)

_CANONICAL_SIGNATURE_CONFIG_DEFAULTS: dict[str, Any] = {
    "window_seconds": WINDOW_SECONDS_DEFAULT,
    "blocks_per_second": ENVELOPE_BLOCKS_PER_SECOND,
    "sample_rate": SIGNATURE_SAMPLE_RATE,
    "include_sha256": True,
    "decoder": None,
}

_ENTRY_KEYS = frozenset(
    {
        "size",
        "mtime_ns",
        "signature_algorithm_version",
        "signature_config",
        "signature",
    }
)


class SourceSignatureCacheError(ValueError):
    """Controlled refusal for a malformed/unusable signature cache.

    Normal cache misses are NOT errors; this type only reports invalid cache
    persistence (missing/wrong format, wrong schema, project mismatch,
    malformed entries, or a structurally invalid signature payload).
    """

    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


def signature_cache_path(
    project_id: str,
    *,
    local_appdata: str | Path | None = None,
) -> Path:
    """Return the project-scoped cache path without creating the file."""
    return project_path(project_id, local_appdata) / SOURCE_SIGNATURE_CACHE_FILENAME


def empty_signature_cache(project_id: str) -> dict[str, Any]:
    """Return a valid empty cache skeleton for a validated project id."""
    identifier = validate_project_id(project_id)
    return {
        "format": SOURCE_SIGNATURE_CACHE_FORMAT,
        "schema_version": SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION,
        "project_id": identifier,
        "entries": {},
    }


def normalize_signature_config(config: Mapping[str, Any] | None) -> dict[str, Any]:
    """Normalize extraction options to a deterministic canonical JSON mapping.

    Only canonical keys are retained. Absent keys take canonical defaults from
    the analysis module, and ``decoder`` is always normalized to ``None`` (the
    canonical ffmpeg path). The result is a plain-JSON-safe mapping used for
    cache validation.
    """
    result: dict[str, Any] = {}
    source = dict(config or {})
    for key in _CANONICAL_SIGNATURE_CONFIG_KEYS:
        if key == "decoder":
            result[key] = None
            continue
        value = source.get(key, _CANONICAL_SIGNATURE_CONFIG_DEFAULTS[key])
        result[key] = value
    return result


def serialize_source_signature(signature: SourceSignature) -> dict[str, Any]:
    """Serialize every SourceSignature field to a plain JSON-safe mapping.

    ``windows`` values are numpy float32 arrays and are serialized as
    ``list[float]``; no numpy-specific object is persisted. ``quality`` and all
    scalar fields are already JSON-native and stored verbatim.
    """
    return {
        "relative_path": signature.relative_path,
        "category": signature.category,
        "file_size_bytes": signature.file_size_bytes,
        "duration_seconds": signature.duration_seconds,
        "sample_rate": signature.sample_rate,
        "channel_count": signature.channel_count,
        "codec": signature.codec,
        "timecode": signature.timecode,
        "creation_time": signature.creation_time,
        "has_video": signature.has_video,
        "windows": _serialize_windows(signature.windows),
        "quality": signature.quality,
        "role": signature.role,
        "sha256": signature.sha256,
        "analysis_seconds": signature.analysis_seconds,
        "source_id": signature.source_id,
        "media_ref": signature.media_ref,
    }


def deserialize_source_signature(payload: Mapping[str, Any]) -> SourceSignature:
    """Restore a SourceSignature from a serialized payload.

    ``windows`` lists are converted back to ``np.float32`` arrays. The float32
    window values round-trip exactly (Python floats represent every float32
    value losslessly). No algorithm recomputation and no media access occur.
    """
    if not isinstance(payload, Mapping):
        raise SourceSignatureCacheError(CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID)
    raw_windows = payload.get("windows")
    if not isinstance(raw_windows, Mapping):
        raise SourceSignatureCacheError(CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID)
    try:
        windows = {key: _deserialize_window(value) for key, value in raw_windows.items()}
        return SourceSignature(
            relative_path=_non_empty_str(payload.get("relative_path")),
            category=payload.get("category", "audio"),
            file_size_bytes=payload.get("file_size_bytes"),
            duration_seconds=payload.get("duration_seconds"),
            sample_rate=payload.get("sample_rate"),
            channel_count=payload.get("channel_count"),
            codec=payload.get("codec"),
            timecode=payload.get("timecode"),
            creation_time=payload.get("creation_time"),
            has_video=bool(payload.get("has_video", False)),
            windows=windows,
            quality=payload.get("quality") or {},
            role=payload.get("role") or "UNKNOWN",
            sha256=payload.get("sha256"),
            analysis_seconds=payload.get("analysis_seconds", 0.0),
            source_id=payload.get("source_id"),
            media_ref=payload.get("media_ref"),
        )
    except SourceSignatureCacheError:
        raise
    except (TypeError, ValueError) as exc:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID, str(exc)
        ) from exc


def load_signature_cache(
    project_id: str,
    *,
    local_appdata: str | Path | None = None,
) -> dict[str, Any]:
    """Load and strictly validate a project cache, or return an empty cache.

    A missing file yields a valid empty cache. Any structural corruption
    (malformed JSON, wrong format, wrong schema, project id mismatch, malformed
    entry, invalid signature payload) raises a controlled
    :class:`SourceSignatureCacheError` rather than being silently reinterpreted
    as valid data.
    """
    import json

    identifier = validate_project_id(project_id)
    path = signature_cache_path(identifier, local_appdata=local_appdata)
    cache = empty_signature_cache(identifier)
    if not path.is_file():
        return cache
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "malformed signature cache JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "signature cache is not an object"
        )
    cache = _validate_cache_structure(payload, identifier)
    return cache


def save_signature_cache(
    cache: Mapping[str, Any],
    project_id: str,
    *,
    local_appdata: str | Path | None = None,
) -> None:
    """Validate then atomically persist a cache via ``local_project.atomic_write_json``.

    Validation happens before any write, so a malformed payload is never
    persisted. The payload written is the deterministic, schema-validated cache.
    """
    identifier = validate_project_id(project_id)
    validated = _validate_cache_structure(dict(cache), identifier)
    atomic_write_json(
        signature_cache_path(identifier, local_appdata=local_appdata), validated
    )


def lookup_cached_signature(
    cache: Mapping[str, Any],
    media_ref: str,
    *,
    size: int,
    mtime_ns: int,
    signature_algorithm_version: str,
    signature_config: Mapping[str, Any] | None = None,
) -> SourceSignature | None:
    """Return a cached signature on a valid hit, else ``None``.

    Pure read-only lookup: no persistence, no mutation, no filesystem and no
    media access. A normal miss (missing media_ref, size/mtime/algorithm/config
    mismatch, or a structurally invalid payload) returns ``None``.
    """
    entries = cache.get("entries") if isinstance(cache, Mapping) else None
    if not isinstance(entries, Mapping):
        return None
    entry = entries.get(media_ref)
    if not isinstance(entry, Mapping):
        return None
    if entry.get("size") != size:
        return None
    if entry.get("mtime_ns") != mtime_ns:
        return None
    if entry.get("signature_algorithm_version") != signature_algorithm_version:
        return None
    stored_config = entry.get("signature_config")
    if normalize_signature_config(stored_config) != normalize_signature_config(
        signature_config or {}
    ):
        return None
    try:
        return deserialize_source_signature(entry.get("signature"))
    except SourceSignatureCacheError:
        return None


def upsert_cached_signature(
    cache: dict[str, Any],
    media_ref: str,
    *,
    size: int,
    mtime_ns: int,
    signature_algorithm_version: str,
    signature_config: Mapping[str, Any] | None = None,
    signature: SourceSignature,
) -> None:
    """Insert or replace one canonical cache entry in-memory.

    This helper mutates ``cache`` in place (documented side effect) and does
    not persist anything. Only complete :class:`SourceSignature` objects are
    stored. ``media_ref`` must be a non-empty canonical string; two distinct
    ``media_ref`` values always yield two distinct entries, even with identical
    size/mtime/sha256.
    """
    if not isinstance(media_ref, str) or not media_ref:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID, "empty media_ref"
        )
    if not isinstance(cache, dict):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "cache must be a dict to upsert"
        )
    entries = cache.setdefault("entries", {})
    entries[media_ref] = {
        "size": size,
        "mtime_ns": mtime_ns,
        "signature_algorithm_version": signature_algorithm_version,
        "signature_config": normalize_signature_config(signature_config or {}),
        "signature": serialize_source_signature(signature),
    }


def _serialize_windows(windows: Mapping[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in windows.items():
        serialized[key] = _to_plain_list(value)
    return serialized


def _to_plain_list(value: Any) -> Any:
    if hasattr(value, "tolist"):
        result = value.tolist()
        if isinstance(result, list):
            return result
        return [float(result)] if result is not None else []
    if isinstance(value, list):
        return value
    return value


def _deserialize_window(value: Any) -> Any:
    import numpy as np

    if not isinstance(value, (list, tuple)):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID, "window is not a list"
        )
    try:
        return np.asarray(value, dtype=np.float32)
    except (TypeError, ValueError) as exc:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID, "window list is invalid"
        ) from exc


def _non_empty_str(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID, "relative_path required"
        )
    return value


def _validate_cache_structure(cache: dict[str, Any], project_id: str) -> dict[str, Any]:
    if cache.get("format") != SOURCE_SIGNATURE_CACHE_FORMAT:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "unexpected signature cache format"
        )
    if cache.get("schema_version") != SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "unexpected signature cache schema version"
        )
    if cache.get("project_id") != project_id:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_PROJECT_MISMATCH, "signature cache project mismatch"
        )
    entries = cache.get("entries")
    if not isinstance(entries, dict):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "signature cache entries missing"
        )
    validated_entries: dict[str, Any] = {}
    for media_ref, entry in entries.items():
        if not isinstance(media_ref, str) or not media_ref:
            raise SourceSignatureCacheError(
                CID_SOURCE_SIGNATURE_CACHE_INVALID, "invalid cache entry key"
            )
        validated_entries[media_ref] = _validate_entry(entry, media_ref)
    return {
        "format": SOURCE_SIGNATURE_CACHE_FORMAT,
        "schema_version": SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION,
        "project_id": project_id,
        "entries": validated_entries,
    }


def _validate_entry(entry: Any, media_ref: str) -> dict[str, Any]:
    if not isinstance(entry, Mapping):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "cache entry is not an object"
        )
    if not _ENTRY_KEYS.issubset(entry.keys()):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "cache entry missing required fields"
        )
    size = entry.get("size")
    mtime_ns = entry.get("mtime_ns")
    if isinstance(size, bool) or not isinstance(size, int):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "cache entry size invalid"
        )
    if isinstance(mtime_ns, bool) or not isinstance(mtime_ns, int):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "cache entry mtime_ns invalid"
        )
    algorithm_version = entry.get("signature_algorithm_version")
    if not isinstance(algorithm_version, str) or not algorithm_version:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "cache entry algorithm version invalid"
        )
    config = entry.get("signature_config")
    if not isinstance(config, Mapping):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "cache entry signature_config invalid"
        )
    signature = entry.get("signature")
    if not isinstance(signature, Mapping):
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_INVALID, "cache entry signature invalid"
        )
    try:
        deserialize_source_signature(signature)
    except SourceSignatureCacheError as exc:
        raise SourceSignatureCacheError(
            CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID, f"invalid payload for {media_ref}"
        ) from exc
    return {
        "size": size,
        "mtime_ns": mtime_ns,
        "signature_algorithm_version": algorithm_version,
        "signature_config": normalize_signature_config(config),
        "signature": dict(signature),
    }


__all__ = [
    "SOURCE_SIGNATURE_CACHE_FORMAT",
    "SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION",
    "SOURCE_SIGNATURE_CACHE_FILENAME",
    "CID_SOURCE_SIGNATURE_CACHE_INVALID",
    "CID_SOURCE_SIGNATURE_CACHE_PROJECT_MISMATCH",
    "CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID",
    "SourceSignatureCacheError",
    "signature_cache_path",
    "empty_signature_cache",
    "normalize_signature_config",
    "serialize_source_signature",
    "deserialize_source_signature",
    "load_signature_cache",
    "save_signature_cache",
    "lookup_cached_signature",
    "upsert_cached_signature",
]
