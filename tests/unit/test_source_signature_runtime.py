"""Focused B2B tests for the in-memory signature cache runtime orchestration.

Covers the ``SignatureCacheRuntime`` context, its counters, pure in-memory
lookup/upsert, and the project-scoped load/save helpers (including the corrupt
cache fallback policy). Uses ``tmp_path`` and synthetic
:class:`SourceSignature` objects only; no ffmpeg, no real media, no grouping.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from scripts.local_media_agent.audio_source_intelligence import (
    ENVELOPE_BLOCKS_PER_SECOND,
    SIGNATURE_SAMPLE_RATE,
    SOURCE_SIGNATURE_ALGORITHM_VERSION,
    WINDOW_SECONDS_DEFAULT,
    SourceSignature,
)
from scripts.local_media_agent.local_project import (
    create_project,
    project_path,
)
from scripts.local_media_agent.source_signature_cache import (
    CID_SOURCE_SIGNATURE_CACHE_INVALID,
    SOURCE_SIGNATURE_CACHE_FILENAME,
    save_signature_cache,
)
from scripts.local_media_agent.source_signature_runtime import (
    SignatureCacheRuntime,
    load_signature_cache_runtime,
    save_signature_cache_runtime,
)


def _make_project(tmp_path: Path) -> tuple[str, Path]:
    manifest = create_project("B2B Runtime Test", local_appdata=tmp_path)
    return manifest["project_id"], project_path(manifest["project_id"], local_appdata=tmp_path)


def _make_signature(
    relative_path: str = "audio/scene01/cam.wav",
    *,
    source_id: str | None = "SRC-1",
    media_ref: str | None = "SRC-1::audio/scene01/cam.wav",
    sha256: str | None = "a" * 64,
    windows: dict | None = None,
) -> SourceSignature:
    return SourceSignature(
        relative_path=relative_path,
        category="audio",
        file_size_bytes=4096,
        duration_seconds=25.0,
        sample_rate=48000,
        channel_count=2,
        codec="pcm_s16le",
        timecode="01:00:00:00",
        creation_time="2026-01-01T00:00:00Z",
        has_video=False,
        windows=windows
        or {
            "start": np.asarray([0.1, -0.2, 0.3, 1.0, -1.0], dtype=np.float32),
            "middle": np.asarray([0.5, 0.5, 0.5, 0.5, 0.5], dtype=np.float32),
        },
        quality={"window_seconds": 5.0, "rms_db": -20.0, "peak_db": None},
        role="EXTERNAL_MIX",
        sha256=sha256,
        analysis_seconds=1.25,
        source_id=source_id,
        media_ref=media_ref,
    )


def _fingerprints(*items) -> dict:
    fp = {}
    for media_ref, size, mtime_ns in items:
        fp[media_ref] = {"size": size, "mtime_ns": mtime_ns}
    return fp


# --- context construction / canonical config ---


def test_runtime_created_from_valid_empty_cache(tmp_path):
    project_id, _ = _make_project(tmp_path)
    runtime = load_signature_cache_runtime(
        project_id, fingerprints={}, local_appdata=tmp_path
    )
    assert runtime.cache["format"] == "CID_SOURCE_SIGNATURE_CACHE"
    assert runtime.cache["schema_version"] == 1
    assert runtime.cache["project_id"] == project_id
    assert runtime.cache["entries"] == {}
    assert runtime.cache_load_error_code is None


def test_runtime_canonical_algorithm_version(tmp_path):
    project_id, _ = _make_project(tmp_path)
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    assert runtime.signature_algorithm_version == SOURCE_SIGNATURE_ALGORITHM_VERSION


def test_runtime_canonical_config_exact_defaults(tmp_path):
    project_id, _ = _make_project(tmp_path)
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    assert runtime.signature_config == {
        "window_seconds": WINDOW_SECONDS_DEFAULT,
        "blocks_per_second": ENVELOPE_BLOCKS_PER_SECOND,
        "sample_rate": SIGNATURE_SAMPLE_RATE,
        "include_sha256": True,
        "decoder": None,
    }


def test_runtime_canonical_decoder_is_none(tmp_path):
    project_id, _ = _make_project(tmp_path)
    runtime = load_signature_cache_runtime(
        project_id, fingerprints={}, local_appdata=tmp_path
    )
    assert runtime.signature_config["decoder"] is None


# --- lookup counters and safety ---


def _hit_runtime(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    return runtime, sig


def test_runtime_lookup_hit_increments_hit(tmp_path):
    runtime, sig = _hit_runtime(tmp_path)
    hit = runtime.lookup(sig.media_ref)
    assert hit is not None
    assert runtime.cache_hits == 1
    assert runtime.cache_misses == 0


def test_runtime_lookup_miss_increments_miss(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints(
        (sig.media_ref, 4096, 1234567),
        ("SRC-1::other/missing.wav", 999, 555),
    )
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    assert runtime.lookup("SRC-1::other/missing.wav") is None
    assert runtime.cache_misses == 1
    assert runtime.cache_hits == 0


def test_runtime_lookup_absent_fingerprint_fails_safely(tmp_path):
    _, sig = _hit_runtime(tmp_path)
    runtime = SignatureCacheRuntime(fingerprints={})
    assert runtime.lookup(sig.media_ref) is None
    assert runtime.cache_hits == 0
    assert runtime.cache_misses == 0


def test_runtime_lookup_no_filesystem_access(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    cache_file = project_dir / SOURCE_SIGNATURE_CACHE_FILENAME
    assert not cache_file.exists()
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    hit = runtime.lookup(sig.media_ref)
    assert hit is not None
    assert not cache_file.exists()


def test_runtime_lookup_no_cache_mutation(tmp_path):
    runtime, sig = _hit_runtime(tmp_path)
    before = json.dumps(runtime.cache, sort_keys=True, default=list)
    runtime.lookup(sig.media_ref)
    after = json.dumps(runtime.cache, sort_keys=True, default=list)
    assert before == after


def test_runtime_note_build_increments_exact(tmp_path):
    runtime = SignatureCacheRuntime()
    runtime.note_signature_build()
    runtime.note_signature_build()
    assert runtime.signature_builds == 2


def test_runtime_successful_upsert_increments(tmp_path):
    _, sig = _hit_runtime(tmp_path)
    runtime = SignatureCacheRuntime(fingerprints=_fingerprints((sig.media_ref, 4096, 1234567)))
    ok = runtime.upsert(sig.media_ref, sig)
    assert ok is True
    assert runtime.cache_upserts == 1


def test_runtime_successful_upsert_sets_dirty(tmp_path):
    _, sig = _hit_runtime(tmp_path)
    runtime = SignatureCacheRuntime(fingerprints=_fingerprints((sig.media_ref, 4096, 1234567)))
    assert runtime.dirty is False
    runtime.upsert(sig.media_ref, sig)
    assert runtime.dirty is True


def test_runtime_upsert_without_fingerprint_rejected(tmp_path):
    _, sig = _hit_runtime(tmp_path)
    runtime = SignatureCacheRuntime(fingerprints={})
    ok = runtime.upsert(sig.media_ref, sig)
    assert ok is False
    assert runtime.cache_upserts == 0
    assert runtime.dirty is False
    assert sig.media_ref not in runtime.cache.get("entries", {})


# --- save semantics ---


def test_runtime_save_dirty_writes_once(tmp_path, monkeypatch):
    project_id, _ = _make_project(tmp_path)
    _, sig = _hit_runtime(tmp_path)
    runtime = SignatureCacheRuntime(
        cache=__import__("scripts.local_media_agent.source_signature_cache", fromlist=["empty_signature_cache"]).empty_signature_cache(project_id),
        fingerprints=_fingerprints((sig.media_ref, 4096, 1234567)),
    )
    runtime.upsert(sig.media_ref, sig)
    calls = []

    class Spy:
        @staticmethod
        def write(cache, pid, local_appdata=None):
            calls.append(pid)

    monkeypatch.setattr(
        "scripts.local_media_agent.source_signature_runtime.save_signature_cache",
        Spy.write,
    )
    assert runtime.dirty is True
    result = save_signature_cache_runtime(runtime, project_id, local_appdata=tmp_path)
    assert result is True
    assert len(calls) == 1


def test_runtime_save_dirty_resets_dirty(tmp_path):
    project_id, _ = _make_project(tmp_path)
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime.fingerprints = fp
    runtime.upsert(sig.media_ref, sig)
    assert runtime.dirty is True
    assert save_signature_cache_runtime(runtime, project_id, local_appdata=tmp_path) is True
    assert runtime.dirty is False


def test_runtime_save_clean_performs_zero_writes(tmp_path, monkeypatch):
    project_id, _ = _make_project(tmp_path)
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    calls = []

    monkeypatch.setattr(
        "scripts.local_media_agent.source_signature_runtime.save_signature_cache",
        lambda *a, **k: calls.append(1),
    )
    assert runtime.dirty is False
    assert save_signature_cache_runtime(runtime, project_id, local_appdata=tmp_path) is False
    assert calls == []


# --- load / corrupt cache policy ---


def test_runtime_load_valid_cache(tmp_path):
    project_id, _ = _make_project(tmp_path)
    _, sig = _hit_runtime(tmp_path)
    src_runtime = SignatureCacheRuntime(
        cache=__import__("scripts.local_media_agent.source_signature_cache", fromlist=["empty_signature_cache"]).empty_signature_cache(project_id),
        fingerprints=_fingerprints((sig.media_ref, 4096, 1234567)),
    )
    src_runtime.upsert(sig.media_ref, sig)
    save_signature_cache_runtime(src_runtime, project_id, local_appdata=tmp_path)
    loaded = load_signature_cache_runtime(
        project_id, fingerprints=_fingerprints((sig.media_ref, 4096, 1234567)), local_appdata=tmp_path
    )
    assert sig.media_ref in loaded.cache["entries"]
    assert loaded.cache_load_error_code is None


def test_runtime_load_missing_cache_yields_empty(tmp_path):
    project_id, _ = _make_project(tmp_path)
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    assert runtime.cache["entries"] == {}
    assert runtime.cache_load_error_code is None


def test_runtime_load_corrupt_cache_yields_empty_runtime(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    path = project_dir / SOURCE_SIGNATURE_CACHE_FILENAME
    path.write_text("{ not valid json", encoding="utf-8")
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    assert runtime.cache["entries"] == {}
    assert runtime.cache_load_error_code == CID_SOURCE_SIGNATURE_CACHE_INVALID


def test_runtime_corrupt_load_observable_error_code(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    path = project_dir / SOURCE_SIGNATURE_CACHE_FILENAME
    path.write_text("{ bad", encoding="utf-8")
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    assert runtime.cache_load_error_code is not None


def test_runtime_corrupt_load_not_dirty_immediately(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    path = project_dir / SOURCE_SIGNATURE_CACHE_FILENAME
    path.write_text("{ bad", encoding="utf-8")
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    assert runtime.dirty is False


def test_runtime_corrupt_cache_not_overwritten_without_upsert(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    path = project_dir / SOURCE_SIGNATURE_CACHE_FILENAME
    path.write_text("{ bad", encoding="utf-8")
    runtime = load_signature_cache_runtime(project_id, fingerprints={}, local_appdata=tmp_path)
    assert runtime.dirty is False
    save_signature_cache_runtime(runtime, project_id, local_appdata=tmp_path)
    assert path.read_text(encoding="utf-8") == "{ bad"


def test_runtime_corrupt_cache_replaced_after_upsert_and_save(tmp_path):
    project_id, project_dir = _make_project(tmp_path)
    path = project_dir / SOURCE_SIGNATURE_CACHE_FILENAME
    path.write_text("{ bad", encoding="utf-8")
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    assert runtime.dirty is True
    assert save_signature_cache_runtime(runtime, project_id, local_appdata=tmp_path) is True
    content = json.loads(path.read_text(encoding="utf-8"))
    assert sig.media_ref in content["entries"]


# --- identity / matching semantics ---


def test_runtime_same_relpath_two_sources_separate(tmp_path):
    project_id, _ = _make_project(tmp_path)
    a = _make_signature(relative_path="same.wav", source_id="SRC-A", media_ref="SRC-A::same.wav")
    b = _make_signature(relative_path="same.wav", source_id="SRC-B", media_ref="SRC-B::same.wav")
    fp = _fingerprints(
        ("SRC-A::same.wav", 100, 100),
        ("SRC-B::same.wav", 100, 100),
    )
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(a.media_ref, a)
    runtime.upsert(b.media_ref, b)
    assert set(runtime.cache["entries"]) == {"SRC-A::same.wav", "SRC-B::same.wav"}
    assert runtime.lookup("SRC-A::same.wav").media_ref == "SRC-A::same.wav"
    assert runtime.lookup("SRC-B::same.wav").media_ref == "SRC-B::same.wav"


def test_runtime_same_sha_two_sources_separate(tmp_path):
    project_id, _ = _make_project(tmp_path)
    a = _make_signature(source_id="SRC-A", media_ref="SRC-A::a.wav", sha256="SAME")
    b = _make_signature(source_id="SRC-B", media_ref="SRC-B::b.wav", sha256="SAME")
    fp = _fingerprints(("SRC-A::a.wav", 50, 50), ("SRC-B::b.wav", 50, 50))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(a.media_ref, a)
    runtime.upsert(b.media_ref, b)
    assert set(runtime.cache["entries"]) == {"SRC-A::a.wav", "SRC-B::b.wav"}


def test_runtime_reconnect_current_location_irrelevant(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    # A "reconnect" is just a new root mapping; fingerprint/identity unchanged.
    assert runtime.lookup(sig.media_ref) is not None


def test_runtime_config_mismatch_miss(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    runtime.signature_config = {"window_seconds": 30.0}
    assert runtime.lookup(sig.media_ref) is None
    assert runtime.cache_misses == 1


def test_runtime_algorithm_mismatch_miss(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    runtime.signature_algorithm_version = "cid.old.v0"
    assert runtime.lookup(sig.media_ref) is None
    assert runtime.cache_misses == 1


def test_runtime_size_mismatch_miss(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    runtime.fingerprints = _fingerprints((sig.media_ref, 9999, 1234567))
    assert runtime.lookup(sig.media_ref) is None
    assert runtime.cache_misses == 1


def test_runtime_mtime_mismatch_miss(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    runtime.fingerprints = _fingerprints((sig.media_ref, 4096, 999999))
    assert runtime.lookup(sig.media_ref) is None
    assert runtime.cache_misses == 1


def test_runtime_all_hit_remains_not_dirty(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    assert save_signature_cache_runtime(runtime, project_id, local_appdata=tmp_path) is True
    assert runtime.dirty is False
    runtime.lookup(sig.media_ref)
    assert runtime.dirty is False


def test_runtime_lookup_returns_independent_deserialized_object(tmp_path):
    runtime, sig = _hit_runtime(tmp_path)
    h1 = runtime.lookup(sig.media_ref)
    h2 = runtime.lookup(sig.media_ref)
    assert h1 is not None and h2 is not None
    assert h1 is not h2
    assert h1.windows["start"] is not h2.windows["start"]
    h1.windows["start"][0] = 123.0
    assert h2.windows["start"][0] != 123.0


def test_runtime_save_uses_b2a_save_api(tmp_path, monkeypatch):
    project_id, _ = _make_project(tmp_path)
    _, sig = _hit_runtime(tmp_path)
    runtime = SignatureCacheRuntime(
        cache=__import__("scripts.local_media_agent.source_signature_cache", fromlist=["empty_signature_cache"]).empty_signature_cache(project_id),
        fingerprints=_fingerprints((sig.media_ref, 4096, 1234567)),
    )
    runtime.upsert(sig.media_ref, sig)
    target = []

    def spy(cache, pid, local_appdata=None):
        target.append((pid, local_appdata))

    monkeypatch.setattr(
        "scripts.local_media_agent.source_signature_runtime.save_signature_cache", spy
    )
    save_signature_cache_runtime(runtime, project_id, local_appdata=tmp_path)
    assert target == [(project_id, tmp_path)]


def test_runtime_no_physical_path_in_identity(tmp_path):
    project_id, _ = _make_project(tmp_path)
    sig = _make_signature()
    fp = _fingerprints((sig.media_ref, 4096, 1234567))
    runtime = load_signature_cache_runtime(project_id, fingerprints=fp, local_appdata=tmp_path)
    runtime.upsert(sig.media_ref, sig)
    entry = runtime.cache["entries"][sig.media_ref]
    payload = json.dumps(runtime.cache, sort_keys=True, default=list)
    assert "D:" not in payload and "E:" not in payload
    assert "current_location" not in payload
    assert set(entry["signature"].keys()) >= {
        "relative_path",
        "windows",
        "sha256",
        "media_ref",
    }
