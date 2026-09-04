"""Focused B2A tests for the project-scoped source signature cache.

Covers cache schema/path, SourceSignature serialization (numpy window
normalization), atomic persistence, and pure in-memory lookup/upsert. Uses
``tmp_path`` and synthetic :class:`SourceSignature` objects only; no ffmpeg, no
real media, no grouping, no runtime cache wiring.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from scripts.local_media_agent.audio_source_intelligence import (
    SOURCE_SIGNATURE_ALGORITHM_VERSION,
    SourceSignature,
)
from scripts.local_media_agent.local_project import (
    create_project,
    project_path,
)
from scripts.local_media_agent.source_signature_cache import (
    CID_SOURCE_SIGNATURE_CACHE_INVALID,
    CID_SOURCE_SIGNATURE_CACHE_PROJECT_MISMATCH,
    CID_SOURCE_SIGNATURE_CACHE_SIGNATURE_INVALID,
    SOURCE_SIGNATURE_CACHE_FORMAT,
    SOURCE_SIGNATURE_CACHE_FILENAME,
    SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION,
    SourceSignatureCacheError,
    deserialize_source_signature,
    empty_signature_cache,
    load_signature_cache,
    lookup_cached_signature,
    normalize_signature_config,
    save_signature_cache,
    serialize_source_signature,
    signature_cache_path,
    upsert_cached_signature,
)


def _make_project(tmp_path: Path) -> tuple[str, Path]:
    manifest = create_project("B2A Cache Test", local_appdata=tmp_path)
    return manifest["project_id"], project_path(manifest["project_id"], local_appdata=tmp_path)


def _make_signature(
    relative_path: str = "audio/scene01/cam.wav",
    *,
    source_id: str | None = "SRC-1",
    media_ref: str | None = "SRC-1::audio/scene01/cam.wav",
    sha256: str | None = "a" * 64,
    analysis_seconds: float = 1.25,
    category: str = "audio",
    role: str = "EXTERNAL_MIX",
    file_size_bytes: int | None = 4096,
) -> SourceSignature:
    return SourceSignature(
        relative_path=relative_path,
        category=category,
        file_size_bytes=file_size_bytes,
        duration_seconds=25.0,
        sample_rate=48000,
        channel_count=2,
        codec="pcm_s16le",
        timecode="01:00:00:00",
        creation_time="2026-01-01T00:00:00Z",
        has_video=False,
        windows={
            "start": np.asarray([0.1, -0.2, 0.3, 1.0, -1.0], dtype=np.float32),
            "middle": np.asarray([0.5, 0.5, 0.5, 0.5, 0.5], dtype=np.float32),
        },
        quality={"window_seconds": 5.0, "rms_db": -20.0, "peak_db": None},
        role=role,
        sha256=sha256,
        analysis_seconds=analysis_seconds,
        source_id=source_id,
        media_ref=media_ref,
    )


def _sample_config() -> dict:
    return {
        "window_seconds": 20.0,
        "blocks_per_second": 10,
        "sample_rate": 8000,
        "include_sha256": True,
        "decoder": None,
    }


# --- path ---


def test_signature_cache_path_project_scoped(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    expected = project_dir / SOURCE_SIGNATURE_CACHE_FILENAME
    assert signature_cache_path(project_id, local_appdata=tmp_path) == expected


def test_signature_cache_path_does_not_create_file(tmp_path):
    project_id, _ = _make_project(tmp_path)
    path = signature_cache_path(project_id, local_appdata=tmp_path)
    assert not path.exists()


def test_empty_cache_schema(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    assert cache["format"] == SOURCE_SIGNATURE_CACHE_FORMAT
    assert cache["schema_version"] == SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION


def test_empty_cache_entries(tmp_path):
    project_id, _ = _make_project(tmp_path)
    assert empty_signature_cache(project_id)["entries"] == {}


def test_empty_cache_project_id_preserved(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    # v4 UUID string form after the PRJ- prefix
    assert cache["project_id"] == project_id
    assert cache["project_id"].startswith("PRJ-")


def test_load_missing_cache_returns_empty(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = load_signature_cache(project_id, local_appdata=tmp_path)
    assert cache["entries"] == {}
    assert cache["format"] == SOURCE_SIGNATURE_CACHE_FORMAT


# --- save / load ---


def test_save_then_load(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    upsert_cached_signature(
        cache,
        "SRC-1::audio/scene01/cam.wav",
        size=4096,
        mtime_ns=1234567,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
        signature=_make_signature(),
    )
    save_signature_cache(cache, project_id, local_appdata=tmp_path)
    loaded = load_signature_cache(project_id, local_appdata=tmp_path)
    assert "SRC-1::audio/scene01/cam.wav" in loaded["entries"]
    assert loaded["entries"]["SRC-1::audio/scene01/cam.wav"]["size"] == 4096


def test_deterministic_save_bytes(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    upsert_cached_signature(
        cache,
        "SRC-1::cam.wav",
        size=4096,
        mtime_ns=99,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
        signature=_make_signature(relative_path="cam.wav", media_ref="SRC-1::cam.wav"),
    )
    save_signature_cache(cache, project_id, local_appdata=tmp_path)
    first = signature_cache_path(project_id, local_appdata=tmp_path).read_bytes()
    save_signature_cache(cache, project_id, local_appdata=tmp_path)
    second = signature_cache_path(project_id, local_appdata=tmp_path).read_bytes()
    assert first == second


def test_empty_cache_save_load_roundtrip(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    save_signature_cache(cache, project_id, local_appdata=tmp_path)
    loaded = load_signature_cache(project_id, local_appdata=tmp_path)
    assert loaded["entries"] == {}
    assert loaded["format"] == SOURCE_SIGNATURE_CACHE_FORMAT


# --- strict load validation ---


def _write_raw(tmp_path, project_id, content: str) -> Path:
    path = signature_cache_path(project_id, local_appdata=tmp_path)
    path.write_text(content, encoding="utf-8")
    return path


def test_wrong_format_rejected(tmp_path):
    project_id, _ = _make_project(tmp_path)
    _write_raw(
        tmp_path,
        project_id,
        json.dumps(
            {
                "format": "WRONG",
                "schema_version": SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION,
                "project_id": project_id,
                "entries": {},
            }
        ),
    )
    with pytest.raises(SourceSignatureCacheError) as exc_info:
        load_signature_cache(project_id, local_appdata=tmp_path)
    assert exc_info.value.code == CID_SOURCE_SIGNATURE_CACHE_INVALID


def test_wrong_schema_version_rejected(tmp_path):
    project_id, _ = _make_project(tmp_path)
    _write_raw(
        tmp_path,
        project_id,
        json.dumps(
            {
                "format": SOURCE_SIGNATURE_CACHE_FORMAT,
                "schema_version": 999,
                "project_id": project_id,
                "entries": {},
            }
        ),
    )
    with pytest.raises(SourceSignatureCacheError) as exc_info:
        load_signature_cache(project_id, local_appdata=tmp_path)
    assert exc_info.value.code == CID_SOURCE_SIGNATURE_CACHE_INVALID


def test_project_mismatch_rejected(tmp_path):
    project_id, _ = _make_project(tmp_path)
    other_id, _ = _make_project(tmp_path)
    _write_raw(
        tmp_path,
        project_id,
        json.dumps(
            {
                "format": SOURCE_SIGNATURE_CACHE_FORMAT,
                "schema_version": SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION,
                "project_id": other_id,
                "entries": {},
            }
        ),
    )
    with pytest.raises(SourceSignatureCacheError) as exc_info:
        load_signature_cache(project_id, local_appdata=tmp_path)
    assert exc_info.value.code == CID_SOURCE_SIGNATURE_CACHE_PROJECT_MISMATCH


def test_malformed_json_rejected(tmp_path):
    project_id, _ = _make_project(tmp_path)
    _write_raw(tmp_path, project_id, "{ not valid json !!!")
    with pytest.raises(SourceSignatureCacheError):
        load_signature_cache(project_id, local_appdata=tmp_path)


def test_malformed_top_level_type_rejected(tmp_path):
    project_id, _ = _make_project(tmp_path)
    _write_raw(tmp_path, project_id, "[1, 2, 3]")
    with pytest.raises(SourceSignatureCacheError) as exc_info:
        load_signature_cache(project_id, local_appdata=tmp_path)
    assert exc_info.value.code == CID_SOURCE_SIGNATURE_CACHE_INVALID


def test_malformed_entries_rejected(tmp_path):
    project_id, _ = _make_project(tmp_path)
    _write_raw(
        tmp_path,
        project_id,
        json.dumps(
            {
                "format": SOURCE_SIGNATURE_CACHE_FORMAT,
                "schema_version": SOURCE_SIGNATURE_CACHE_SCHEMA_VERSION,
                "project_id": project_id,
                "entries": {"SRC-1::cam.wav": {"broken": True}},
            }
        ),
    )
    with pytest.raises(SourceSignatureCacheError) as exc_info:
        load_signature_cache(project_id, local_appdata=tmp_path)
    assert exc_info.value.code == CID_SOURCE_SIGNATURE_CACHE_INVALID


# --- serialization / deserialization ---


def test_serialize_simple_source_signature(tmp_path):
    sig = _make_signature()
    serialized = serialize_source_signature(sig)
    assert isinstance(serialized, dict)
    assert serialized["relative_path"] == sig.relative_path
    json.dumps(serialized)  # must be JSON-safe


def test_deserialize_simple_source_signature(tmp_path):
    sig = _make_signature()
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert isinstance(restored, SourceSignature)
    assert restored.relative_path == sig.relative_path


def test_windows_ndarray_serialized_as_list(tmp_path):
    sig = _make_signature()
    serialized = serialize_source_signature(sig)
    assert isinstance(serialized["windows"]["start"], list)
    assert not isinstance(serialized["windows"]["start"], np.ndarray)
    assert all(isinstance(v, float) for v in serialized["windows"]["start"])


def test_windows_restored_float32(tmp_path):
    sig = _make_signature()
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert isinstance(restored.windows["start"], np.ndarray)
    assert restored.windows["start"].dtype == np.float32


def test_float32_window_exact_roundtrip(tmp_path):
    sig = _make_signature()
    restored = deserialize_source_signature(serialize_source_signature(sig))
    for key in sig.windows:
        assert np.array_equal(restored.windows[key], sig.windows[key])
        assert restored.windows[key].dtype == np.float32


def test_quality_roundtrip(tmp_path):
    sig = _make_signature()
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert restored.quality == sig.quality


def test_sha_string_roundtrip(tmp_path):
    sig = _make_signature(sha256="deadbeef")
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert restored.sha256 == "deadbeef"


def test_sha_none_roundtrip(tmp_path):
    sig = _make_signature(sha256=None)
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert restored.sha256 is None


def test_source_id_roundtrip(tmp_path):
    sig = _make_signature(source_id="SRC-42")
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert restored.source_id == "SRC-42"


def test_media_ref_roundtrip(tmp_path):
    sig = _make_signature(media_ref="SRC-1::cam.wav")
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert restored.media_ref == "SRC-1::cam.wav"


def test_analysis_seconds_roundtrip_exact(tmp_path):
    sig = _make_signature(analysis_seconds=1.234567)
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert restored.analysis_seconds == pytest.approx(1.234567)


def test_role_roundtrip(tmp_path):
    sig = _make_signature(role="ISOLATED_MIC")
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert restored.role == "ISOLATED_MIC"


def test_file_size_roundtrip(tmp_path):
    sig = _make_signature(file_size_bytes=1048576)
    restored = deserialize_source_signature(serialize_source_signature(sig))
    assert restored.file_size_bytes == 1048576


# --- lookup ---


def _cached(tmp_path, project_id=None, *, sig=None, size=4096, mtime_ns=1234567):
    if project_id is None:
        project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    sig = sig or _make_signature()
    upsert_cached_signature(
        cache,
        sig.media_ref,
        size=size,
        mtime_ns=mtime_ns,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
        signature=sig,
    )
    return cache, sig, size, mtime_ns


def test_valid_lookup_hit(tmp_path):
    cache, sig, size, mtime_ns = _cached(tmp_path)
    hit = lookup_cached_signature(
        cache,
        sig.media_ref,
        size=size,
        mtime_ns=mtime_ns,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
    )
    assert hit is not None
    assert hit.media_ref == sig.media_ref
    assert np.array_equal(hit.windows["start"], sig.windows["start"])


def test_missing_media_ref_miss(tmp_path):
    cache, sig, size, mtime_ns = _cached(tmp_path)
    result = lookup_cached_signature(
        cache,
        "SRC-NO::missing.wav",
        size=size,
        mtime_ns=mtime_ns,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
    )
    assert result is None


def test_size_mismatch_miss(tmp_path):
    cache, sig, size, mtime_ns = _cached(tmp_path)
    result = lookup_cached_signature(
        cache,
        sig.media_ref,
        size=size + 1,
        mtime_ns=mtime_ns,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
    )
    assert result is None


def test_mtime_mismatch_miss(tmp_path):
    cache, sig, size, mtime_ns = _cached(tmp_path)
    result = lookup_cached_signature(
        cache,
        sig.media_ref,
        size=size,
        mtime_ns=mtime_ns + 1,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
    )
    assert result is None


def test_algorithm_mismatch_miss(tmp_path):
    cache, sig, size, mtime_ns = _cached(tmp_path)
    result = lookup_cached_signature(
        cache,
        sig.media_ref,
        size=size,
        mtime_ns=mtime_ns,
        signature_algorithm_version="cid.sig.other",
        signature_config=_sample_config(),
    )
    assert result is None


def test_config_mismatch_miss(tmp_path):
    cache, sig, size, mtime_ns = _cached(tmp_path)
    result = lookup_cached_signature(
        cache,
        sig.media_ref,
        size=size,
        mtime_ns=mtime_ns,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config={**_sample_config(), "sample_rate": 44100},
    )
    assert result is None


def test_lookup_does_not_mutate_cache(tmp_path):
    cache, sig, size, mtime_ns = _cached(tmp_path)
    before = json.dumps(cache, sort_keys=True, default=list)
    lookup_cached_signature(
        cache,
        sig.media_ref,
        size=size,
        mtime_ns=mtime_ns,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
    )
    after = json.dumps(cache, sort_keys=True, default=list)
    assert before == after


def test_lookup_no_filesystem_access(tmp_path):
    cache, sig, size, mtime_ns = _cached(tmp_path)
    # The lookup operates on the in-memory cache dict; no cache file was ever
    # written (upsert is pure), so persistence is not involved on a hit.
    assert "SRC-1::audio/scene01/cam.wav" in cache["entries"]
    hit = lookup_cached_signature(
        cache,
        sig.media_ref,
        size=size,
        mtime_ns=mtime_ns,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
    )
    assert hit is not None


def test_sha_none_remains_cache_hit_valid(tmp_path):
    sig = _make_signature(sha256=None)
    cache, _, size, mtime_ns = _cached(tmp_path, sig=sig)
    hit = lookup_cached_signature(
        cache,
        sig.media_ref,
        size=size,
        mtime_ns=mtime_ns,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
    )
    assert hit is not None and hit.sha256 is None


# --- upsert ---


def test_upsert_creates_entry(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    sig = _make_signature()
    upsert_cached_signature(
        cache,
        sig.media_ref,
        size=4096,
        mtime_ns=1,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(),
        signature=sig,
    )
    assert sig.media_ref in cache["entries"]
    entry = cache["entries"][sig.media_ref]
    assert entry["size"] == 4096
    assert entry["mtime_ns"] == 1


def test_upsert_replaces_same_media_ref(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    first = _make_signature(relative_path="cam.wav", media_ref="SRC-1::cam.wav", sha256="111")
    second = _make_signature(relative_path="cam.wav", media_ref="SRC-1::cam.wav", sha256="222")
    upsert_cached_signature(
        cache, first.media_ref, size=1, mtime_ns=1,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(), signature=first,
    )
    upsert_cached_signature(
        cache, second.media_ref, size=2, mtime_ns=2,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(), signature=second,
    )
    entry = cache["entries"]["SRC-1::cam.wav"]
    assert entry["size"] == 2
    assert entry["signature"]["sha256"] == "222"


def test_upsert_same_relpath_different_sources_separate(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    a = _make_signature(relative_path="same.wav", source_id="SRC-A", media_ref="SRC-A::same.wav")
    b = _make_signature(relative_path="same.wav", source_id="SRC-B", media_ref="SRC-B::same.wav")
    for sig in (a, b):
        upsert_cached_signature(
            cache, sig.media_ref, size=100, mtime_ns=100,
            signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
            signature_config=_sample_config(), signature=sig,
        )
    assert set(cache["entries"]) == {"SRC-A::same.wav", "SRC-B::same.wav"}


def test_same_sha_two_media_refs_remain_separate(tmp_path):
    project_id, _ = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    a = _make_signature(relative_path="a.wav", source_id="SRC-A", media_ref="SRC-A::a.wav", sha256="SAME")
    b = _make_signature(relative_path="b.wav", source_id="SRC-B", media_ref="SRC-B::b.wav", sha256="SAME")
    for sig in (a, b):
        upsert_cached_signature(
            cache, sig.media_ref, size=50, mtime_ns=50,
            signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
            signature_config=_sample_config(), signature=sig,
        )
    assert set(cache["entries"]) == {"SRC-A::a.wav", "SRC-B::b.wav"}


# --- payload hygiene ---


def test_payload_has_no_current_location(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    sig = _make_signature()
    upsert_cached_signature(
        cache, sig.media_ref, size=1, mtime_ns=1,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(), signature=sig,
    )
    save_signature_cache(cache, project_id, local_appdata=tmp_path)
    text = signature_cache_path(project_id, local_appdata=tmp_path).read_text()
    assert "current_location" not in text


def test_payload_has_no_absolute_media_path(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    sig = _make_signature()
    upsert_cached_signature(
        cache, sig.media_ref, size=1, mtime_ns=1,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(), signature=sig,
    )
    save_signature_cache(cache, project_id, local_appdata=tmp_path)
    text = signature_cache_path(project_id, local_appdata=tmp_path).read_text()
    assert str(tmp_path) not in text
    assert "media_path" not in text


def test_signature_config_deterministic(tmp_path):
    a = normalize_signature_config({"sample_rate": 8000})
    b = _sample_config()
    c = normalize_signature_config(b)
    assert a == c
    assert b == c
    for cfg in (a, c):
        assert set(cfg) == {
            "window_seconds", "blocks_per_second", "sample_rate", "include_sha256", "decoder"
        }
        assert cfg["decoder"] is None


def test_numpy_never_leaks_into_payload(tmp_path):
    sig = _make_signature()
    serialized = serialize_source_signature(sig)
    assert "windows" in serialized
    assert all(isinstance(v, list) for v in serialized["windows"].values())


# --- persistence guards ---


def test_atomic_write_leaves_no_temp_on_success(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    cache = empty_signature_cache(project_id)
    sig = _make_signature()
    upsert_cached_signature(
        cache, sig.media_ref, size=1, mtime_ns=1,
        signature_algorithm_version=SOURCE_SIGNATURE_ALGORITHM_VERSION,
        signature_config=_sample_config(), signature=sig,
    )
    save_signature_cache(cache, project_id, local_appdata=tmp_path)
    leftovers = [p for p in project_dir.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []


def test_validation_before_save_prevents_corrupt_write(tmp_path):
    project_id, _ = _make_project(tmp_path)
    bad = empty_signature_cache(project_id)
    bad["format"] = "WRONG_FORMAT"
    with pytest.raises(SourceSignatureCacheError):
        save_signature_cache(bad, project_id, local_appdata=tmp_path)
    assert not signature_cache_path(project_id, local_appdata=tmp_path).exists()
