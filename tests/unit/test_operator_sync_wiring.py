"""Minimal wiring tests for the operator `--sync` integration.

These test only that the existing operator CLI exposes opt-in read-only sync
and renders structured RESOLVED/UNRESOLVED results. They do NOT run the ASR
engine or any real media: `assemble_project_sessions` is patched (on the
automatic_media_sync module) with a controllable synthetic project so we
validate the wiring, not the algorithm.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from types import SimpleNamespace

import scripts.local_media_agent.automatic_media_sync as ams
import scripts.local_media_agent.cid_local_media_agent_operator as operator
from scripts.local_media_agent.automatic_media_sync import (
    CONFIDENCE_HIGH,
    SynchronizedClip,
)


def _sync_clip(video: str = "video/C001.mp4",
               audio: str = "audio/ref.wav",
               *, unresolved: bool = False) -> SynchronizedClip:
    return SynchronizedClip(
        video_path=video,
        audio_reference=audio,
        session_position_seconds=12.5,
        intercept_a=-1.234567,
        slope_b=1.0001,
        confidence=CONFIDENCE_HIGH,
        retime_recommended=False,
        audio_speed_percent=100.01,
        predicted_end_drift_frames=0.4,
        unresolved=unresolved,
    )


def _synthetic_project(resolved_clips=0, unresolved_media=None, unresolved_clips=0):
    sessions = []
    if resolved_clips:
        sessions.append(SimpleNamespace(
            synchronized_clips=[_sync_clip() for _ in range(resolved_clips)]
        ))
    if unresolved_clips:
        unresolved_clip = _sync_clip("video/C002.mp4", unresolved=True)
        unresolved_clip.root_cause = "CAMERA_AUDIO_SIGNAL_INSUFFICIENT"
        sessions.append(SimpleNamespace(synchronized_clips=[unresolved_clip]))
    unresolved = list(unresolved_media or [])
    return SimpleNamespace(
        sessions=sessions,
        unresolved_media=unresolved,
        to_dict=lambda: {"sessions": [], "unresolved_media": unresolved},
    )


def test_sync_menu_option_present_in_prompt_menu(monkeypatch, capsys):
    def fake_input(prompt=""):
        print(prompt, end="")
        return "1"

    monkeypatch.setattr("builtins.input", fake_input)
    choice = operator._prompt_menu()
    out = capsys.readouterr().out
    assert "Sync video to audio (informational, read-only)" in out
    assert "Choice [1-5]" in out
    assert choice == "1"


def test_sync_flag_requires_model_and_folder(monkeypatch, capsys):
    monkeypatch.setattr(operator.sys, "argv", ["cid_local_media_agent_operator.py", "--sync"])
    exit_code = operator.main()
    out = capsys.readouterr().out
    assert exit_code == 1
    assert "Sync requires a model directory" in out


def test_sync_flag_routes_to_scan_and_sync(monkeypatch, tmp_path):
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "model.bin").write_text("x")
    folder = tmp_path / "input"
    folder.mkdir()

    calls = {}

    def fake_scan_and_sync(folder_arg, model_arg):
        calls["folder"] = folder_arg
        calls["model"] = model_arg
        return 0

    monkeypatch.setattr(
        operator.sys, "argv",
        ["cid...py", "--sync", str(model_dir), str(folder)],
    )
    monkeypatch.setattr(operator, "_run_scan_and_sync", fake_scan_and_sync)

    exit_code = operator.main()
    assert exit_code == 0
    assert calls["model"] == str(model_dir)
    assert calls["folder"] == str(folder)


def test_run_sync_resolved_renders_and_writes_json(monkeypatch, capsys, tmp_path):
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "model.bin").write_text("x")

    captured = {}

    def fake_assemble(results, model_local_path=None):
        captured["meta_count"] = len(results)
        captured["model_local_path"] = model_local_path
        return _synthetic_project(resolved_clips=1)

    monkeypatch.setattr(ams, "assemble_project_sessions", fake_assemble)

    folder = tmp_path / "input"
    folder.mkdir()
    meta = {
        "results": [
            {"relative_path": "video/C001.mp4", "category": "video", "duration_seconds": 100.0},
            {"relative_path": "audio/ref.wav", "category": "audio", "duration_seconds": 120.0},
        ]
    }

    exit_code = operator._run_sync(str(folder), meta, str(model_dir))
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "RESOLVED" in out
    assert "offset:" in out
    assert captured["model_local_path"] == str(model_dir)
    assert captured["meta_count"] == 2
    assert all("abs_path" in item for item in meta["results"])


def test_run_sync_unresolved_is_not_destructive(monkeypatch, capsys, tmp_path):
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "model.bin").write_text("x")

    monkeypatch.setattr(
        ams, "assemble_project_sessions",
        lambda *a, **k: _synthetic_project(
            resolved_clips=0,
            unresolved_clips=1,
            unresolved_media=["video/B001.mp4"],
        ),
    )

    folder = tmp_path / "input"
    folder.mkdir()
    meta = {
        "results": [
            {"relative_path": "video/C001.mp4", "category": "video", "duration_seconds": 100.0},
            {"relative_path": "video/B001.mp4", "category": "video", "duration_seconds": 90.0},
            {"relative_path": "audio/ref.wav", "category": "audio", "duration_seconds": 120.0},
        ]
    }

    exit_code = operator._run_sync(str(folder), meta, str(model_dir))
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "UNRESOLVED" in out
    assert "No safe synchronization was established." in out
    assert "candidate_offset" in out
    assert "diagnostic_only" in out
    assert "CAMERA_AUDIO_SIGNAL_INSUFFICIENT" in out
    assert "      offset:" not in out
    assert "audio speed" not in out
    assert "retime" not in out
    assert "no media was modified" in out.lower()


def test_missing_model_dir_returns_error(tmp_path):
    folder = tmp_path / "input"
    folder.mkdir()
    with tempfile.TemporaryDirectory() as tmp:
        exit_code = operator._run_sync(folder, {"results": []}, str(Path(tmp) / "missing"))
        assert exit_code == 1
