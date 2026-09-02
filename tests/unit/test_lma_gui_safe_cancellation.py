"""Tests for CID LMA safe cooperative cancellation and temp cleanup."""

from __future__ import annotations

import json
import sys
import threading
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_media_agent.batch_transcription import (
    run_batch_transcription,
    select_batch_candidates,
)
from scripts.local_media_agent.local_transcription import transcribe_media_file


def _metadata_entry(rel: str, category: str, duration: float) -> dict:
    return {
        "relative_path": rel,
        "category": category,
        "duration_seconds": duration,
    }


class _FakePayload:
    def to_dict(self) -> dict:
        return {
            "status": "TRANSCRIPTION_COMPLETED",
            "detected_language": "es",
            "language_probability": 0.9,
            "segments": [
                {"start_seconds": 0.0, "end_seconds": 1.2, "text": "hola"},
            ],
            "error": None,
            "warnings": [],
        }


class _FakeBackend:
    def __init__(self, *args, **kwargs) -> None:
        self.model_identifier_sanitized = "faster-whisper-small"


class _FakeRequest:
    def __init__(self, *args, **kwargs) -> None:
        pass


def _patch_transcription_paths(fake_transcribe):
    stack = ExitStack()
    stack.enter_context(
        patch(
            "scripts.editorial_intelligence.transcription.transcription.FasterWhisperTranscriptionBackend",
            _FakeBackend,
        )
    )
    stack.enter_context(
        patch(
            "scripts.editorial_intelligence.transcription.transcription.TranscriptionRequest",
            _FakeRequest,
        )
    )
    stack.enter_context(
        patch(
            "scripts.editorial_intelligence.transcription.transcription.transcribe",
            fake_transcribe,
        )
    )
    return stack


class TestSelectBatchCandidates:
    def test_filters_and_sorts(self) -> None:
        entries = [
            _metadata_entry("imagen/x.jpg", "image", 1.0),
            _metadata_entry("._AppleDouble.wav", "audio", 1.0),
            _metadata_entry("audio1.wav", "audio", 30.0),
            _metadata_entry("video1.mp4", "video", 10.0),
            _metadata_entry("no_dur.wav", "audio", None),
        ]
        candidates = select_batch_candidates(entries)
        assert [c["relative_path"] for c in candidates] == ["video1.mp4", "audio1.wav"]
        assert [c["duration_seconds"] for c in candidates] == [10.0, 30.0]


class TestTranscribeMediaFileCleanup:
    def test_cancellation_after_extraction_cleans_temp(self, tmp_path: Path) -> None:
        source = tmp_path / "clip.wav"
        source.write_bytes(b"dummy")
        wav = tmp_path / "cid_audio_fake.wav"
        cancel_event = threading.Event()

        def fake_extract(*args, **kwargs) -> Path:
            wav.write_bytes(b"fake wav")
            return wav

        def fake_transcribe(request, backend, **kwargs) -> _FakePayload:
            cancel_event.set()
            return _FakePayload()

        with patch(
            "scripts.local_media_agent.local_transcription.extract_audio_to_wav",
            side_effect=fake_extract,
        ), patch(
            "scripts.local_media_agent.local_transcription._get_audio_duration",
            return_value=5.0,
        ):
            with _patch_transcription_paths(fake_transcribe):
                result = transcribe_media_file(
                    source,
                    tmp_path / "model",
                    cancel_event=cancel_event,
                )

        assert result["status"] == "TRANSCRIPTION_CANCELLED"
        assert result.get("cancelled") is True
        assert not wav.exists(), "temp decode derivative must be removed on cancellation"

    def test_failure_cleans_temp(self, tmp_path: Path) -> None:
        source = tmp_path / "clip.wav"
        source.write_bytes(b"dummy")
        wav = tmp_path / "cid_audio_fake.wav"

        def fake_extract(*args, **kwargs) -> Path:
            wav.write_bytes(b"fake wav")
            return wav

        def fake_transcribe(request, backend, **kwargs) -> _FakePayload:
            raise RuntimeError("engine failure")

        with patch(
            "scripts.local_media_agent.local_transcription.extract_audio_to_wav",
            side_effect=fake_extract,
        ), patch(
            "scripts.local_media_agent.local_transcription._get_audio_duration",
            return_value=5.0,
        ):
            with _patch_transcription_paths(fake_transcribe):
                result = transcribe_media_file(source, tmp_path / "model")

        assert result["status"] == "TRANSCRIPTION_FAILED"
        assert not wav.exists(), "temp decode derivative must be removed on failure"

    def test_completed_publishes_and_cleans_temp(self, tmp_path: Path) -> None:
        source = tmp_path / "clip.wav"
        source.write_bytes(b"dummy")
        wav = tmp_path / "cid_audio_fake.wav"

        def fake_extract(*args, **kwargs) -> Path:
            wav.write_bytes(b"fake wav")
            return wav

        def fake_transcribe(request, backend, **kwargs) -> _FakePayload:
            return _FakePayload()

        with patch(
            "scripts.local_media_agent.local_transcription.extract_audio_to_wav",
            side_effect=fake_extract,
        ), patch(
            "scripts.local_media_agent.local_transcription._get_audio_duration",
            return_value=5.0,
        ):
            with _patch_transcription_paths(fake_transcribe):
                result = transcribe_media_file(source, tmp_path / "model")

        assert result["status"] == "TRANSCRIPTION_COMPLETED"
        assert len(result["segments"]) == 1
        assert not wav.exists(), "temp decode derivative must be removed on success"


class TestRunBatchTranscriptionCancellation:
    def test_cancelled_summary_counts(self, tmp_path: Path) -> None:
        metadata = [
            _metadata_entry("RODECaster/54 - 26 Jun 2026/Stereo Mix.wav", "audio", 5.0),
            _metadata_entry("RODECaster/78 - 7 Jul 2026/Stereo Mix.wav", "audio", 6.0),
            _metadata_entry("RODECaster/79 - 7 Jul 2026/Stereo Mix.wav", "audio", 7.0),
        ]
        cancel_event = threading.Event()
        call = {"count": 0}

        def fake_transcribe(abs_path, model_dir, **kwargs) -> dict:
            call["count"] += 1
            if call["count"] == 1:
                return {
                    "status": "TRANSCRIPTION_COMPLETED",
                    "segments": [{"start_seconds": 0.0, "end_seconds": 1.0, "text": "hola"}],
                    "detected_language": "es",
                    "language_probability": 0.9,
                    "model_identifier": "faster-whisper-small",
                    "error": None,
                }
            cancel_event.set()
            return {"status": "TRANSCRIPTION_CANCELLED", "cancelled": True, "segments": []}

        results_dir = tmp_path / "results"
        with patch(
            "scripts.local_media_agent.local_transcription.transcribe_media_file",
            side_effect=fake_transcribe,
        ):
            summary = run_batch_transcription(
                tmp_path,
                tmp_path / "model",
                metadata_results=metadata,
                results_dir=results_dir,
                cancel_event=cancel_event,
            )

        assert summary["status"] == "BATCH_CANCELLED"
        assert summary["cancelled_by_user"] is True
        assert summary["candidate_count"] == 3
        assert summary["completed_count"] == 1
        assert summary["cancelled_count"] == 1
        assert summary["unstarted_count"] == 1
        assert summary["error_count"] == 0

        summary_path = results_dir / "batch_summary.json"
        assert summary_path.is_file(), "cancelled run must still write batch_summary.json"
        written = json.loads(summary_path.read_text(encoding="utf-8"))
        assert written["status"] == "BATCH_CANCELLED"
        assert written["cancelled_by_user"] is True

        srt_files = list(results_dir.glob("*.srt"))
        assert len(srt_files) == 1, "only the completed item publishes an SRT"

    def test_cancel_before_start_writes_summary(self, tmp_path: Path) -> None:
        metadata = [
            _metadata_entry("a.wav", "audio", 5.0),
            _metadata_entry("b.wav", "audio", 6.0),
        ]
        cancel_event = threading.Event()
        cancel_event.set()
        results_dir = tmp_path / "results"

        with patch(
            "scripts.local_media_agent.local_transcription.transcribe_media_file",
            return_value={"status": "TRANSCRIPTION_COMPLETED", "segments": [], "error": None},
        ):
            summary = run_batch_transcription(
                tmp_path,
                tmp_path / "model",
                metadata_results=metadata,
                results_dir=results_dir,
                cancel_event=cancel_event,
            )

        assert summary["status"] == "BATCH_CANCELLED"
        assert summary["completed_count"] == 0
        assert summary["cancelled_count"] == 0
        assert summary["unstarted_count"] == 2
        assert (results_dir / "batch_summary.json").is_file()

    def test_normal_completion_summary(self, tmp_path: Path) -> None:
        metadata = [
            _metadata_entry("a.wav", "audio", 5.0),
            _metadata_entry("b.wav", "audio", 6.0),
        ]
        results_dir = tmp_path / "results"

        def fake_transcribe(abs_path, model_dir, **kwargs) -> dict:
            return {
                "status": "TRANSCRIPTION_COMPLETED",
                "segments": [{"start_seconds": 0.0, "end_seconds": 1.0, "text": "hola"}],
                "detected_language": "es",
                "language_probability": 0.9,
                "model_identifier": "faster-whisper-small",
                "error": None,
            }

        with patch(
            "scripts.local_media_agent.local_transcription.transcribe_media_file",
            side_effect=fake_transcribe,
        ):
            summary = run_batch_transcription(
                tmp_path,
                tmp_path / "model",
                metadata_results=metadata,
                results_dir=results_dir,
            )

        assert summary["status"] == "BATCH_COMPLETED"
        assert summary["cancelled_by_user"] is False
        assert summary["completed_count"] == 2
        assert summary["unstarted_count"] == 0
        assert len(list(results_dir.glob("*.srt"))) == 2
        written = json.loads((results_dir / "batch_summary.json").read_text(encoding="utf-8"))
        assert written["status"] == "BATCH_COMPLETED"


class TestRunBatchWorkerProcess:
    """Dedicated-worker mode: spawn, reap, sentinel cancel, forced termination."""

    def _write_worker_result(self, result_json: Path) -> None:
        result_json.write_text(
            json.dumps(
                {
                    "status": "TRANSCRIPTION_COMPLETED",
                    "segments": [
                        {"start_seconds": 0.0, "end_seconds": 1.0, "text": "hola"}
                    ],
                    "detected_language": "es",
                    "language_probability": 0.9,
                    "model_identifier": "faster-whisper-small",
                    "audio_duration_seconds": 5.0,
                    "error": None,
                }
            ),
            encoding="utf-8",
        )

    def test_worker_completion_publishes_srt(self, tmp_path: Path) -> None:
        metadata = [_metadata_entry("a.wav", "audio", 5.0)]
        results_dir = tmp_path / "results"
        wtmp = tmp_path / "wtmp"
        wtmp.mkdir(parents=True, exist_ok=True)

        class FakePopen:
            def __init__(self, cmd, **kwargs) -> None:
                self.task = json.loads(Path(cmd[-1]).read_text(encoding="utf-8"))
                self.calls = 0

            def poll(self) -> None | int:
                self.calls += 1
                if self.calls == 1:
                    return None
                Path(self.task["result_json"]).write_text(
                    json.dumps(
                        {
                            "status": "TRANSCRIPTION_COMPLETED",
                            "segments": [
                                {"start_seconds": 0.0, "end_seconds": 1.0, "text": "hola"}
                            ],
                            "detected_language": "es",
                            "language_probability": 0.9,
                            "model_identifier": "faster-whisper-small",
                            "audio_duration_seconds": 5.0,
                            "error": None,
                        }
                    ),
                    encoding="utf-8",
                )
                return 1

            def wait(self, timeout=None) -> int:
                return 0

            def kill(self) -> None:
                self.killed = True

        with patch(
            "scripts.local_media_agent.batch_transcription._worker_temp_dir",
            return_value=wtmp,
        ), patch(
            "scripts.local_media_agent.batch_transcription.subprocess.Popen",
            FakePopen,
        ):
            summary = run_batch_transcription(
                tmp_path,
                tmp_path / "model",
                metadata_results=metadata,
                results_dir=results_dir,
                worker_process=True,
            )

        assert summary["status"] == "BATCH_COMPLETED"
        assert summary["cancelled_by_user"] is False
        assert summary["completed_count"] == 1
        assert summary["cancel_latency_seconds"] is None
        assert len(list(results_dir.glob("*.srt"))) == 1
        assert not list(wtmp.glob("cid_*")), "controller-owned temp files must be cleaned"

    def test_worker_cancel_terminates_and_reports_latency(self, tmp_path: Path) -> None:
        metadata = [_metadata_entry("a.wav", "audio", 5.0)]
        cancel_event = threading.Event()
        results_dir = tmp_path / "results"
        wtmp = tmp_path / "wtmp"
        wtmp.mkdir(parents=True, exist_ok=True)

        class FakePopen:
            def __init__(self, cmd, **kwargs) -> None:
                self.task = json.loads(Path(cmd[-1]).read_text(encoding="utf-8"))
                self.calls = 0
                self.killed = False

            def poll(self) -> None | int:
                self.calls += 1
                if self.calls == 1:
                    cancel_event.set()
                if self.killed:
                    return 1
                return None

            def wait(self, timeout=None) -> int:
                return 0

            def kill(self) -> None:
                self.killed = True

        with patch(
            "scripts.local_media_agent.batch_transcription._worker_temp_dir",
            return_value=wtmp,
        ), patch(
            "scripts.local_media_agent.batch_transcription.subprocess.Popen",
            FakePopen,
        ):
            summary = run_batch_transcription(
                tmp_path,
                tmp_path / "model",
                metadata_results=metadata,
                results_dir=results_dir,
                cancel_event=cancel_event,
                worker_process=True,
                grace_period_seconds=0.01,
            )

        assert summary["status"] == "BATCH_CANCELLED"
        assert summary["cancelled_by_user"] is True
        assert summary["cancelled_count"] == 1
        assert summary["cancel_latency_seconds"] is not None
        assert summary["cancel_latency_seconds"] >= 0
        assert not list(wtmp.glob("cid_*")), "controller-owned temp files must be cleaned"
        assert not list(results_dir.glob("*.srt")), "no outputs for cancelled item"

    def test_worker_cancel_before_start_reports_latency(self, tmp_path: Path) -> None:
        metadata = [_metadata_entry("a.wav", "audio", 5.0)]
        cancel_event = threading.Event()
        cancel_event.set()
        results_dir = tmp_path / "results"

        with patch(
            "scripts.local_media_agent.batch_transcription.subprocess.Popen",
            side_effect=AssertionError("worker must not spawn when cancelled before start"),
        ):
            summary = run_batch_transcription(
                tmp_path,
                tmp_path / "model",
                metadata_results=metadata,
                results_dir=results_dir,
                cancel_event=cancel_event,
                worker_process=True,
            )

        assert summary["status"] == "BATCH_CANCELLED"
        assert summary["cancelled_count"] == 0
        assert summary["unstarted_count"] == 1
        assert summary["cancel_latency_seconds"] is not None


class TestWorkerProgressForwarding:
    def test_consume_worker_progress_forwards_jsonl(self, tmp_path: Path) -> None:
        from scripts.local_media_agent.batch_transcription import _consume_worker_progress

        log = tmp_path / "progress.jsonl"
        log.write_text(
            '{"source_end_seconds": 3.0}\n'
            '{"source_end_seconds": 7.5}\n',
            encoding="utf-8",
        )
        collected: list[dict] = []
        offset = _consume_worker_progress(log, 0, collected.append)
        assert [s["source_end_seconds"] for s in collected] == [3.0, 7.5]
        assert offset > 0
        log.write_text(
            log.read_text(encoding="utf-8") + '{"source_end_seconds": 12.0}\n',
            encoding="utf-8",
        )
        collected.clear()
        offset = _consume_worker_progress(log, offset, collected.append)
        assert [s["source_end_seconds"] for s in collected] == [12.0]

    def test_consume_worker_progress_ignores_garbage(self, tmp_path: Path) -> None:
        from scripts.local_media_agent.batch_transcription import _consume_worker_progress

        log = tmp_path / "progress.jsonl"
        log.write_text("not-json\n{\"source_end_seconds\": 5.0}\n", encoding="utf-8")
        collected: list[dict] = []
        _consume_worker_progress(log, 0, collected.append)
        assert [s["source_end_seconds"] for s in collected] == [5.0]


class TestDoneSrtHintWording:
    """Truthful done-screen wording: never claim an SRT unless one exists."""

    def _import_cid_gui(self):
        import importlib
        import types

        stubs = {}
        for name in ("filedialog", "messagebox", "ttk"):
            stubs[name] = types.ModuleType(f"tkinter.{name}")
        tkinter = types.ModuleType("tkinter")
        tkinter.filedialog = stubs["filedialog"]
        tkinter.messagebox = stubs["messagebox"]
        tkinter.ttk = stubs["ttk"]
        stubs["tkinter"] = tkinter
        for name, mod in stubs.items():
            sys.modules[name] = mod
        try:
            return importlib.import_module("scripts.local_media_agent.cid_gui")
        finally:
            for name in stubs:
                sys.modules.pop(name, None)
            sys.modules.pop("scripts.local_media_agent.cid_gui", None)

    def test_completed_srt_branch(self) -> None:
        gui = self._import_cid_gui()
        assert gui._done_srt_hint(2, 2) == "Los SRT completados están listos para DaVinci."
        assert gui._done_srt_hint(1, 1) == "Los SRT completados están listos para DaVinci."

    def test_no_srt_branch(self) -> None:
        gui = self._import_cid_gui()
        assert gui._done_srt_hint(0, 0) == "No se ha generado ningún SRT en esta ejecución."
        assert gui._done_srt_hint(0, 2) == "No se ha generado ningún SRT en esta ejecución."
        assert gui._done_srt_hint(2, 0) == "No se ha generado ningún SRT en esta ejecución."
        assert gui._done_srt_hint(0, 1) == "No se ha generado ningún SRT en esta ejecución."


class TestProjectVideoProfileGuiBoundary:
    def test_metadata_projection_never_auto_confirms_project(self, tmp_path, monkeypatch) -> None:
        from scripts.local_media_agent import cid_gui
        from scripts.local_media_agent.local_project import create_project
        from scripts.local_media_agent.project_video_profile import load_project_video_profile
        from scripts.local_media_agent.source_video_profile import load_source_video_profiles

        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        project = create_project("Proyecto")
        app = object.__new__(cid_gui.ProducerApp)
        app.active_project = project
        app.analysis_project_id = project["project_id"]
        app._refresh_project_ui = lambda: None
        metadata = {
            "results": [
                {
                    "category": "video",
                    "relative_path": "roll/clip.mov",
                    "duration_raw": "10.000000",
                    "duration_origin": "format",
                    "duration_seconds": 10.0,
                    "timecode": "01:00:00:00",
                    "video": {
                        "width": 1920,
                        "height": 1080,
                        "frame_rate": {
                            "raw_avg": "25/1",
                            "raw_frame": "25/1",
                            "variable": False,
                        },
                    },
                }
            ]
        }
        app._on_metadata_done(metadata)
        profile = load_project_video_profile(project["project_id"])
        catalog = load_source_video_profiles(project["project_id"])
        assert profile["confirmation_status"] == "NOT_CONFIRMED"
        assert catalog["entries"][0]["source_frame_rate"] == "25/1"

    def test_scanning_without_active_project_creates_nothing(self, tmp_path, monkeypatch) -> None:
        from scripts.local_media_agent import cid_gui
        from scripts.local_media_agent.local_project import list_projects

        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        app = object.__new__(cid_gui.ProducerApp)
        app.active_project = None
        app.analysis_project_id = None
        app._on_metadata_done({"results": []})
        assert list_projects() == []

    def test_metadata_stays_bound_to_project_active_when_analysis_started(
        self, tmp_path, monkeypatch
    ) -> None:
        from scripts.local_media_agent import cid_gui
        from scripts.local_media_agent.local_project import create_project
        from scripts.local_media_agent.source_video_profile import (
            load_source_video_profiles,
            SourceVideoProfileError,
        )

        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        first = create_project("Primero")
        second = create_project("Segundo")
        app = object.__new__(cid_gui.ProducerApp)
        app.active_project = second
        app.analysis_project_id = first["project_id"]
        app._refresh_project_ui = lambda: None
        app._on_metadata_done(
            {
                "results": [
                    {
                        "category": "video",
                        "relative_path": "clip.mov",
                        "duration_raw": "1.000",
                        "duration_origin": "format",
                        "timecode": "00:00:00:00",
                        "video": {
                            "width": 1920,
                            "height": 1080,
                            "frame_rate": {
                                "raw_avg": "25/1",
                                "raw_frame": "25/1",
                                "variable": False,
                            },
                        },
                    }
                ]
            }
        )
        assert load_source_video_profiles(first["project_id"])["entries"]
        with pytest.raises(SourceVideoProfileError):
            load_source_video_profiles(second["project_id"])

    def test_source_and_project_labels_are_distinct(self) -> None:
        source = Path(__file__).parents[2].joinpath(
            "scripts/local_media_agent/cid_gui.py"
        ).read_text(encoding="utf-8")
        assert "Material detectado por CID" in source
        assert "Configuración del proyecto" in source
        assert "frame_duration" not in source


class TestProjectImageProfileGuiBoundary:
    """Project image (aspect + framing) surfaces only via explicit operator action."""

    def _source(self) -> str:
        return Path(__file__).parents[2].joinpath(
            "scripts/local_media_agent/cid_gui.py"
        ).read_text(encoding="utf-8")

    def test_presets_surfaced_without_raw_fraction_syntax(self) -> None:
        source = self._source()
        for label in ("16:9", "1.66:1", "1.85 Flat", "2.00:1", "2.35:1",
                      "2.39 Scope", "2.40:1", "Academy 1.37"):
            assert label in source
        assert "Otro..." in source

    def test_custom_aspect_surfaces_explicit_operator_input(self) -> None:
        source = self._source()
        assert "Formato personalizado" in source
        assert "2.39:1" in source

    def test_no_auto_project_aspect_from_source_resolution(self, tmp_path, monkeypatch) -> None:
        from scripts.local_media_agent import cid_gui
        from scripts.local_media_agent.local_project import create_project
        from scripts.local_media_agent.project_video_profile import (
            image_configuration_missing,
            load_project_video_profile,
        )

        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
        project = create_project("Proyecto")
        app = object.__new__(cid_gui.ProducerApp)
        app.active_project = project
        app.analysis_project_id = project["project_id"]
        app._refresh_project_ui = lambda: None
        app._on_metadata_done(
            {
                "results": [
                    {
                        "category": "video",
                        "relative_path": "anamorphic.mov",
                        "duration_raw": "10.000000",
                        "duration_origin": "format",
                        "timecode": "01:00:00:00",
                        "video": {
                            "width": 1920,
                            "height": 1080,
                            "frame_rate": {
                                "raw_avg": "25/1",
                                "raw_frame": "25/1",
                                "variable": False,
                            },
                        },
                    }
                ]
            }
        )
        profile = load_project_video_profile(project["project_id"])
        assert profile["confirmation_status"] == "NOT_CONFIRMED"
        assert image_configuration_missing(profile) is True


class TestTranscriptionSegmentCallback:
    def test_segment_callback_receives_source_mapped_segments(self) -> None:
        from scripts.editorial_intelligence.transcription.transcription import (
            FakeTranscriptionBackend,
            TranscriptionRequest,
            transcribe,
        )

        backend = FakeTranscriptionBackend(
            segments=[
                {"segment_index": 0, "start_seconds": 0.0, "end_seconds": 1.5, "text": "hola"},
                {"segment_index": 1, "start_seconds": 1.5, "end_seconds": 3.0, "text": "mundo"},
            ]
        )
        request = TranscriptionRequest(
            asset_id="x",
            temporary_audio_path="/tmp/x.wav",
            audio_duration_seconds=10.0,
        )
        collected: list[dict] = []
        result = transcribe(request, backend, segment_callback=collected.append)
        assert result.state == "TRANSCRIPTION_COMPLETED"
        assert len(collected) == 2
        assert collected[0]["source_start_seconds"] == 0.0
        assert collected[1]["source_end_seconds"] == 3.0

    def test_segment_callback_not_invoked_without_arg(self) -> None:
        from scripts.editorial_intelligence.transcription.transcription import (
            FakeTranscriptionBackend,
            TranscriptionRequest,
            transcribe,
        )

        backend = FakeTranscriptionBackend(
            segments=[
                {"segment_index": 0, "start_seconds": 0.0, "end_seconds": 1.0, "text": "hola"},
            ]
        )
        request = TranscriptionRequest(
            asset_id="x",
            temporary_audio_path="/tmp/x.wav",
            audio_duration_seconds=10.0,
        )
        result = transcribe(request, backend)
        assert result.state == "TRANSCRIPTION_COMPLETED"


class _FakeTkWidget:
    def __init__(self) -> None:
        self.state = None
        self.text = None
        self.command = None

    def config(self, **kwargs) -> None:
        self.state = kwargs.get("state", self.state)
        self.text = kwargs.get("text", self.text)
        self.command = kwargs.get("command", self.command)


class TestAnalysisLifecycleGuiBoundary:
    def _make_app(self):
        from scripts.local_media_agent import cid_gui

        app = object.__new__(cid_gui.ProducerApp)
        app.analysis_active = False
        app.active = False
        app.folder = "/tmp"
        app.active_project = None
        app.cancel_event = threading.Event()
        app.analyze_btn = _FakeTkWidget()
        app.analyze_hint = _FakeTkWidget()
        return app

    def test_cancel_sets_cooperative_event_and_keeps_state(self) -> None:
        app = self._make_app()
        app.analysis_active = True
        assert not app.cancel_event.is_set()
        app._cancel_analysis_click()
        assert app.cancel_event.is_set()
        # does not mark completion: still active until the finisher runs
        assert app.analysis_active is True

    def test_analysis_state_resets_after_finish(self) -> None:
        app = self._make_app()
        app.analysis_active = True
        app._pick_folder = lambda: None
        app._on_analysis_finished("completed")
        assert app.analysis_active is False
        assert app.analyze_btn.text == "Seleccionar carpeta"
        assert app.analyze_btn.state == "normal"

    def test_cancel_finish_also_resets_state(self) -> None:
        app = self._make_app()
        app.analysis_active = True
        app._pick_folder = lambda: None
        app._on_analysis_finished("cancelled")
        assert app.analysis_active is False
        assert app.analyze_hint.text == "Análisis cancelado."

    def test_transcription_start_guarded_while_analysis_active(self) -> None:
        app = self._make_app()
        app.analysis_active = True
        app._start_transcription_click()
        # returns early without clobbering the shared cooperative cancel event
        assert not app.cancel_event.is_set()
