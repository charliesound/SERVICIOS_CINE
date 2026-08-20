"""Tests for CID LMA producer-oriented results UX helpers."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from scripts.local_media_agent.batch_transcription import (
    _default_results_dir,
    _human_folder_stem,
    last_result_location,
    make_run_results_dir,
    remember_result_location,
)
from scripts.local_media_agent.audio_source_intelligence import (
    SourceCluster,
    SourceSignature,
)

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_human_folder_stem_sanitizes_windows_invalid_chars() -> None:
    assert _human_folder_stem("Grabación Kenia") == "Grabación_Kenia"
    assert _human_folder_stem('79 - 7 Jul 2026') == "79_-_7_Jul_2026"
    assert _human_folder_stem("a:b*?<>|") == "a_b"
    assert _human_folder_stem(None) == "CID"


def test_make_run_results_dir_uses_human_name_and_avoids_collisions(tmp_path: Path) -> None:
    now = datetime(2026, 8, 19, 23, 15)
    first = make_run_results_dir(tmp_path, "Grabación Kenia", now_local=now)
    assert first.name == "Grabación_Kenia_CID_2026-08-19_2315"
    assert first.is_dir()
    second = make_run_results_dir(tmp_path, "Grabación Kenia", now_local=now)
    assert second.name == "Grabación_Kenia_CID_2026-08-19_2315_2"
    assert second.is_dir()


def test_default_results_dir_is_visible_documents_folder(monkeypatch) -> None:
    monkeypatch.setenv("USERPROFILE", "C:\\Users\\Test")
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    result = _default_results_dir()
    assert "Documents" in result.parts
    assert result.parts[-1] == "Resultados"
    assert result.parts[-2] == "CID Local Media Agent"


def test_result_location_remembered(monkeypatch, tmp_path: Path) -> None:
    prefs = tmp_path / "prefs"
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(
        "scripts.local_media_agent.batch_transcription._prefs_path", lambda: prefs
    )
    assert last_result_location() is None
    remember_result_location("D:\\Resultados CID")
    assert last_result_location() == "D:\\Resultados CID"


def test_cluster_view_is_producer_facing() -> None:
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
        from scripts.local_media_agent import cid_gui

        cluster_view = cid_gui.cluster_view
    finally:
        for name in stubs:
            sys.modules.pop(name, None)
        sys.modules.pop("scripts.local_media_agent.cid_gui", None)

    cluster = SourceCluster(session_id="79 - 7 Jul 2026")
    mix = SourceSignature(
        relative_path="79 - 7 Jul 2026/Stereo Mix.wav",
        category="audio",
        duration_seconds=2616.0,
        has_video=False,
        role="EXTERNAL_MIX",
    )
    track = SourceSignature(
        relative_path="79 - 7 Jul 2026/Track1-Combo 1.wav",
        category="audio",
        duration_seconds=2616.0,
        has_video=False,
        role="ISOLATED_MIC",
    )
    cluster.sources = [mix, track]
    cluster.transcription_masters = ["79 - 7 Jul 2026/Stereo Mix.wav"]
    cluster.duplicate_sources = []
    cluster.alternate_sources = ["79 - 7 Jul 2026/Track1-Combo 1.wav"]
    cluster.relationships = [{"sync": {"status": "RESOLVED"}}]

    view = cluster_view(cluster)
    assert view["title"] == "Grabación 79 - 7 Jul 2026"
    assert view["master"] == "Stereo Mix.wav"
    assert view["audio_count"] == 2
    assert view["video_count"] == 0
    assert view["sync_ok"] is True
    assert view["alternate_count"] == 1