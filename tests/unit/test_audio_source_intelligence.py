"""Synthetic deterministic tests for CID Audio Source Intelligence.

No repository media fixtures. Signals are generated in-memory and written as
temporary 8 kHz mono WAV files so the native WAV reader is exercised (no
ffmpeg required for these tests).
"""

import tempfile
import wave
from pathlib import Path

import numpy as np
import pytest

from scripts.local_media_agent.audio_source_intelligence import (
    ENVELOPE_BLOCKS_PER_SECOND,
    ROLE_CAMERA_REFERENCE,
    ROLE_EXTERNAL_MIX,
    ROLE_ISOLATED_MIC,
    ROLE_UNKNOWN,
    SYNC_OFFSET_TOLERANCE_SECONDS,
    SYNC_STATUS_RESOLVED,
    SYNC_STATUS_UNRESOLVED,
    QUALITY_DEFICIENTE,
    QUALITY_EXCELENTE,
    RELATIONSHIP_IDENTICAL,
    RELATIONSHIP_SAME_EVENT,
    RELATIONSHIP_UNRELATED,
    analyze_quality,
    assign_source_role,
    build_sync_manifest,
    classify_relationship,
    decode_window,
    extract_source_signature,
    find_sync_lag,
    group_related_media,
    internal_rank_score,
    source_quality_summary,
    sync_sources,
    _label_quality,
    _timecode_to_seconds,
)

RATE = 8000


def _event(duration: float, seed: int, freq: float = 0.5) -> np.ndarray:
    rng = np.random.RandomState(seed)
    n = int(duration * RATE)
    t = np.arange(n) / RATE
    mod = 0.5 + 0.5 * np.sin(2.0 * np.pi * freq * t)
    x = (mod * rng.randn(n)).astype(np.float32)
    peak = float(np.max(np.abs(x)))
    if peak > 0:
        x = x * (0.5 / peak)
    return x.astype(np.float32)


def _white_noise(duration: float, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.randn(int(duration * RATE)).astype(np.float32)


def _write_wav(path: Path, samples: np.ndarray) -> None:
    samples = np.clip(samples, -1.0, 1.0)
    data = (samples * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(data.tobytes())


def _metadata(rel_path: str, duration: float, category: str = "audio") -> dict:
    return {
        "relative_path": rel_path,
        "category": category,
        "file_size_bytes": int(duration * RATE * 2),
        "duration_seconds": duration,
        "audio": {"codec": "pcm_s16le", "sample_rate": RATE, "channel_count": 1},
    }


def _signature(path: Path, rel_path: str, duration: float, category: str = "audio"):
    return extract_source_signature(
        path, _metadata(rel_path, duration, category), window_seconds=duration
    )


def _session_dir(base: Path, name: str) -> Path:
    d = base / name
    d.mkdir(parents=True, exist_ok=True)
    return d


class TestSyncLagAndOffset:
    def test_find_sync_lag_recovers_known_offset(self):
        a = _event(5.0, seed=1)
        offset = 0.5
        b = a[int(offset * RATE):]
        env_a = np.abs(a).reshape(-1, RATE // ENVELOPE_BLOCKS_PER_SECOND).mean(axis=1)
        env_b = np.abs(b).reshape(-1, RATE // ENVELOPE_BLOCKS_PER_SECOND).mean(axis=1)
        lag, confidence = find_sync_lag(env_a, env_b, ENVELOPE_BLOCKS_PER_SECOND)
        assert abs(lag - offset * ENVELOPE_BLOCKS_PER_SECOND) <= 1
        assert confidence > 0.9

    def test_sync_sources_recovers_offset_within_tolerance(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            a = _event(6.0, seed=2)
            offset = 0.625
            path_a = sess / "camera_reference.wav"
            path_b = sess / "Stereo Mix.wav"
            _write_wav(path_a, a)
            _write_wav(path_b, a[int(offset * RATE):])
            sig_a = _signature(path_a, "Sesion 1/camera_reference.wav", 6.0)
            sig_b = _signature(path_b, "Sesion 1/Stereo Mix.wav", 6.0 - offset)
            sync = sync_sources(sig_a, sig_b)
            assert sync["status"] == SYNC_STATUS_RESOLVED
            assert sync["offset_seconds"] is not None
            assert abs(sync["offset_seconds"] - offset) <= SYNC_OFFSET_TOLERANCE_SECONDS


class TestRelationship:
    def test_same_event_different_source(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            a = _event(5.0, seed=3)
            b = _event(5.0, seed=3)
            path_a = sess / "cam_a.wav"
            path_b = sess / "mix_b.wav"
            _write_wav(path_a, a)
            _write_wav(path_b, b)
            sig_a = _signature(path_a, "Sesion 1/cam_a.wav", 5.0)
            sig_b = _signature(path_b, "Sesion 1/mix_b.wav", 5.0)
            sync = sync_sources(sig_a, sig_b)
            rel = classify_relationship(sig_a, sig_b, sync)
            assert rel["relationship"] in (RELATIONSHIP_IDENTICAL, RELATIONSHIP_SAME_EVENT)
            assert rel["confidence"] > 0.8

    def test_same_signal_plus_noise_stays_related(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            a = _event(5.0, seed=4)
            rng = np.random.RandomState(99)
            b = a + 0.15 * rng.randn(a.size).astype(np.float32)
            path_a = sess / "ref.wav"
            path_b = sess / "noisy.wav"
            _write_wav(path_a, a)
            _write_wav(path_b, b)
            sig_a = _signature(path_a, "Sesion 1/ref.wav", 5.0)
            sig_b = _signature(path_b, "Sesion 1/noisy.wav", 5.0)
            sync = sync_sources(sig_a, sig_b)
            rel = classify_relationship(sig_a, sig_b, sync)
            assert rel["relationship"] in (RELATIONSHIP_IDENTICAL, RELATIONSHIP_SAME_EVENT)

    def test_duplicate_copy_detected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            samples = _event(5.0, seed=5)
            path_a = sess / "copy_a.wav"
            path_b = sess / "copy_b.wav"
            _write_wav(path_a, samples)
            _write_wav(path_b, samples)
            sig_a = _signature(path_a, "Sesion 1/copy_a.wav", 5.0)
            sig_b = _signature(path_b, "Sesion 1/copy_b.wav", 5.0)
            sync = sync_sources(sig_a, sig_b)
            rel = classify_relationship(sig_a, sig_b, sync)
            assert rel["relationship"] == RELATIONSHIP_IDENTICAL
            assert rel.get("duplicate") is True

    def test_unrelated_signals_not_related(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            a = _event(5.0, seed=11)
            b = _white_noise(5.0, seed=22)
            path_a = sess / "audio_a.wav"
            path_b = sess / "audio_b.wav"
            _write_wav(path_a, a)
            _write_wav(path_b, b)
            sig_a = _signature(path_a, "Sesion 1/audio_a.wav", 5.0)
            sig_b = _signature(path_b, "Sesion 1/audio_b.wav", 5.0)
            sync = sync_sources(sig_a, sig_b)
            rel = classify_relationship(sig_a, sig_b, sync)
            assert rel["relationship"] == RELATIONSHIP_UNRELATED


class TestQualityAndMasterSelection:
    def test_label_quality_mapping(self):
        assert _label_quality({"clipping_fraction": 0.05, "silence_fraction": 0.1}) == QUALITY_DEFICIENTE
        assert _label_quality({"silence_fraction": 0.95}) == QUALITY_DEFICIENTE
        assert _label_quality(
            {"rms_db": -30.0, "dynamic_range_db": 12.0, "clipping_fraction": 0.0, "silence_fraction": 0.1}
        ) == QUALITY_EXCELENTE

    def test_cleaner_external_recommended_over_degraded_camera(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            clean = _event(6.0, seed=7)
            rng = np.random.RandomState(77)
            degraded = np.clip(clean * 2.0 + 0.25 * rng.randn(clean.size).astype(np.float32), -1.0, 1.0)
            path_cam = sess / "camera_reference.wav"
            path_mix = sess / "Stereo Mix.wav"
            _write_wav(path_cam, degraded)
            _write_wav(path_mix, clean)
            meta_cam = _metadata("Sesion 1/camera_reference.wav", 6.0)
            meta_mix = _metadata("Sesion 1/Stereo Mix.wav", 6.0)
            sig_cam = extract_source_signature(path_cam, meta_cam, window_seconds=6.0)
            sig_mix = extract_source_signature(path_mix, meta_mix, window_seconds=6.0)
            q_cam = source_quality_summary(sig_cam)
            q_mix = source_quality_summary(sig_mix)
            score_cam = internal_rank_score(q_cam, sig_cam.duration_seconds, 0.9)
            score_mix = internal_rank_score(q_mix, sig_mix.duration_seconds, 0.9)
            assert score_mix > score_cam
            clusters = group_related_media(
                [meta_cam, meta_mix], media_root=base
            )
            assert clusters
            assert clusters[0].transcription_masters == ["Sesion 1/Stereo Mix.wav"]


class TestRolesAndManifest:
    def test_source_roles(self):
        assert assign_source_role("C0011.MP4", "video", True, {}) == ROLE_CAMERA_REFERENCE
        assert assign_source_role("Stereo Mix.wav", "audio", False, {}) == ROLE_EXTERNAL_MIX
        assert assign_source_role("Track1-Combo 1.wav", "audio", False, {}) == ROLE_ISOLATED_MIC
        assert assign_source_role("file_123.wav", "audio", False, {}) == ROLE_UNKNOWN

    def test_manifest_shape_and_privacy(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            samples = _event(5.0, seed=8)
            path_a = sess / "cam.wav"
            path_b = sess / "mix.wav"
            _write_wav(path_a, samples)
            _write_wav(path_b, samples[int(0.4 * RATE):])
            meta_a = _metadata("Sesion 1/cam.wav", 5.0)
            meta_b = _metadata("Sesion 1/mix.wav", 4.6)
            clusters = group_related_media([meta_a, meta_b], media_root=base)
            assert clusters
            manifest = build_sync_manifest(clusters[0], media_root=base)
            assert manifest["schema_version"] == "cid.local_media_agent.sync_manifest.v1"
            assert manifest["reference"] in ("Sesion 1/cam.wav", "Sesion 1/mix.wav")
            assert manifest["privacy"]["source_media_modified"] is False
            assert manifest["privacy"]["network_used"] is False
            assert manifest["sources"], "expected at least one related source entry"

    def test_timecode_parsing(self):
        assert _timecode_to_seconds("01:02:03") == 3723.0
        assert _timecode_to_seconds("not-a-tc") is None


class TestNoTempDerivatives:
    def test_decode_window_native_wav_no_temp_files(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            path = base / "sig.wav"
            _write_wav(path, _event(3.0, seed=9))
            before = set(base.iterdir())
            rate, samples = decode_window(
                path, start_seconds=0.0, duration_seconds=2.0, sample_rate=RATE
            )
            after = set(base.iterdir())
            assert rate == RATE
            assert samples.size > 0
            assert before == after, "decode must not create temp derivatives"


class TestCancellationUnaffected:
    def test_quality_analysis_empty_input_safe(self):
        metrics = analyze_quality(np.zeros(0, dtype=np.float32), RATE)
        assert metrics["rms_db"] is None
        assert metrics["clipping_fraction"] == 0.0


class TestSemanticSafetyDispositions:
    def test_unrelated_with_content_remains_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            dialogue_a = _event(6.0, seed=31)
            dialogue_b = _event(6.0, seed=31)
            other = _white_noise(6.0, seed=44)
            path_a = sess / "entrevista_a.wav"
            path_b = sess / "entrevista_b.wav"
            path_c = sess / "voz_extra.wav"
            _write_wav(path_a, dialogue_a)
            _write_wav(path_b, dialogue_b)
            _write_wav(path_c, other)
            meta_a = _metadata("Sesion 1/entrevista_a.wav", 6.0)
            meta_b = _metadata("Sesion 1/entrevista_b.wav", 6.0)
            meta_c = _metadata("Sesion 1/voz_extra.wav", 6.0)
            clusters = group_related_media([meta_a, meta_b, meta_c], media_root=base)
            assert clusters
            cluster = clusters[0]
            assert cluster.dispositions["Sesion 1/voz_extra.wav"] == "UNIQUE_CONTENT"
            assert cluster.dispositions["Sesion 1/entrevista_a.wav"] == "DIALOGUE"
            assert "Sesion 1/voz_extra.wav" in cluster.transcription_masters
            assert "Sesion 1/voz_extra.wav" not in cluster.excluded_sources
            assert "Sesion 1/voz_extra.wav" not in cluster.uncertain_sources

    def test_effectively_silent_unrelated_source_excluded_with_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            dialogue = _event(6.0, seed=41)
            silence = np.zeros(int(6.0 * RATE), dtype=np.float32)
            path_a = sess / "entrevista.wav"
            path_b = sess / "pista_tecnica.wav"
            _write_wav(path_a, dialogue)
            _write_wav(path_b, silence)
            meta_a = _metadata("Sesion 1/entrevista.wav", 6.0)
            meta_b = _metadata("Sesion 1/pista_tecnica.wav", 6.0)
            clusters = group_related_media([meta_a, meta_b], media_root=base)
            assert clusters
            cluster = clusters[0]
            assert cluster.dispositions["Sesion 1/pista_tecnica.wav"] == "TECHNICAL_OR_EMPTY"
            assert "Sesion 1/pista_tecnica.wav" in cluster.excluded_sources
            assert "Sesion 1/pista_tecnica.wav" not in cluster.transcription_masters

    def test_multiple_masters_preserve_independent_content(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            a = _event(6.0, seed=51)
            b = _event(6.0, seed=51)
            c = _white_noise(6.0, seed=53)
            path_a = sess / "entrevista_a.wav"
            path_b = sess / "entrevista_b.wav"
            path_c = sess / "voz_extra.wav"
            _write_wav(path_a, a)
            _write_wav(path_b, b)
            _write_wav(path_c, c)
            meta_a = _metadata("Sesion 1/entrevista_a.wav", 6.0)
            meta_b = _metadata("Sesion 1/entrevista_b.wav", 6.0)
            meta_c = _metadata("Sesion 1/voz_extra.wav", 6.0)
            clusters = group_related_media([meta_a, meta_b, meta_c], media_root=base)
            assert clusters
            cluster = clusters[0]
            assert len(cluster.transcription_masters) >= 2
            assert "Sesion 1/voz_extra.wav" in cluster.transcription_masters
            assert cluster.dispositions["Sesion 1/voz_extra.wav"] == "UNIQUE_CONTENT"

    def test_manifest_lists_dispositions(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sess = _session_dir(base, "Sesion 1")
            dialogue = _event(6.0, seed=61)
            silence = np.zeros(int(6.0 * RATE), dtype=np.float32)
            path_a = sess / "entrevista.wav"
            path_b = sess / "pista_tecnica.wav"
            _write_wav(path_a, dialogue)
            _write_wav(path_b, silence)
            meta_a = _metadata("Sesion 1/entrevista.wav", 6.0)
            meta_b = _metadata("Sesion 1/pista_tecnica.wav", 6.0)
            clusters = group_related_media([meta_a, meta_b], media_root=base)
            manifest = build_sync_manifest(clusters[0], media_root=base)
            assert "Sesion 1/pista_tecnica.wav" in manifest["excluded_sources"]
            assert manifest["uncertain_sources"] == []
            assert manifest["sources"] and manifest["sources"][0]["source"] == "Sesion 1/pista_tecnica.wav"
            assert manifest["sources"][0]["relationship"] == "UNRELATED"
            assert manifest["sources"][0]["quality"]