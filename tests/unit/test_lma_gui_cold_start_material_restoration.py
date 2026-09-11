"""Cold-start Material display summary restore / persist GUI tests."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.local_media_agent import cid_gui as gui
from scripts.local_media_agent.local_project import create_project
from scripts.local_media_agent.project_analysis_display_summary import (
    build_project_analysis_display_summary,
    load_project_analysis_display_summary,
    project_analysis_display_summary_path,
    save_project_analysis_display_summary,
)
from scripts.local_media_agent.project_sources import (
    STATE_OFFLINE,
    add_project_source,
    update_source_state,
)


class _Var:
    def __init__(self, value="0"):
        self.value = str(value)

    def set(self, value):
        self.value = str(value)

    def get(self):
        return self.value


def _material_app():
    app = object.__new__(gui.ProducerApp)
    app.analysis_active = False
    app.active_project = None
    app.count_labels = {
        "video": _Var(),
        "audio": _Var(),
        "images": _Var(),
        "other": _Var(),
        "incidents": _Var(),
    }
    return app


def _counts(app):
    return {key: int(var.get()) for key, var in app.count_labels.items()}


def _save_summary(tmp_path, project_id, source_id, location, **scan_overrides):
    scan = {
        "total_files": 385,
        "media_files": 241,
        "video": 128,
        "audio": 1,
        "images": 112,
        "other": 144,
        "errors": 0,
        "warnings": 0,
    }
    scan.update(scan_overrides)
    summary = build_project_analysis_display_summary(
        project_id,
        analyzed_sources=[{"source_id": source_id, "current_location": location}],
        scan=scan,
        incident_count=2,
        analysis_run_id="gate-run",
    )
    save_project_analysis_display_summary(summary, local_appdata=tmp_path)
    return summary


def test_restore_valid_summary_without_analysis_callbacks(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    project = create_project("Cold", local_appdata=tmp_path)
    record = add_project_source(
        project["project_id"], "E:/Siruela 2", "Siruela 2", local_appdata=tmp_path
    )
    _save_summary(
        tmp_path, project["project_id"], record["source_id"], record["current_location"]
    )
    app = _material_app()
    app.active_project = project
    called = {"scan": 0, "meta": 0, "group": 0}

    def boom(*args, **kwargs):
        raise AssertionError("must not call analysis backends")

    monkeypatch.setattr(gui, "scan_read_only_folder", boom)
    monkeypatch.setattr(gui, "extract_metadata", boom)
    monkeypatch.setattr(gui, "group_related_media", boom)

    app._restore_persisted_analysis_result(project["project_id"])
    assert _counts(app) == {
        "video": 128,
        "audio": 1,
        "images": 112,
        "other": 144,
        "incidents": 2,
    }
    assert called["scan"] == 0


def test_historical_offline_catalog_does_not_contaminate(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    project = create_project("Scope", local_appdata=tmp_path)
    e = add_project_source(
        project["project_id"], "E:/Siruela 2", "E", local_appdata=tmp_path
    )
    f = add_project_source(
        project["project_id"], "F:/SIRUELA", "F", local_appdata=tmp_path
    )
    update_source_state(
        project["project_id"], f["source_id"], STATE_OFFLINE, local_appdata=tmp_path
    )
    _save_summary(
        tmp_path, project["project_id"], e["source_id"], e["current_location"]
    )
    app = _material_app()
    app._restore_persisted_analysis_result(project["project_id"])
    assert _counts(app)["video"] == 128
    assert _counts(app)["other"] == 144


def test_online_scope_mismatch_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    project = create_project("Mismatch", local_appdata=tmp_path)
    e = add_project_source(
        project["project_id"], "E:/Siruela 2", "E", local_appdata=tmp_path
    )
    f = add_project_source(
        project["project_id"], "F:/SIRUELA", "F", local_appdata=tmp_path
    )
    _save_summary(
        tmp_path, project["project_id"], e["source_id"], e["current_location"]
    )
    # Both ONLINE now — persisted E-only scope must not display
    app = _material_app()
    app.count_labels["video"].set("99")
    app._restore_persisted_analysis_result(project["project_id"])
    assert _counts(app) == {
        "video": 0,
        "audio": 0,
        "images": 0,
        "other": 0,
        "incidents": 0,
    }
    assert f["source_id"]


def test_relocated_source_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    project = create_project("Move", local_appdata=tmp_path)
    e = add_project_source(
        project["project_id"], "E:/Siruela 2", "E", local_appdata=tmp_path
    )
    _save_summary(
        tmp_path, project["project_id"], e["source_id"], e["current_location"]
    )
    from scripts.local_media_agent.project_sources import reconnect_source

    reconnect_source(
        project["project_id"],
        e["source_id"],
        "E:/Other",
        confirmation=True,
        local_appdata=tmp_path,
    )
    app = _material_app()
    app._restore_persisted_analysis_result(project["project_id"])
    assert _counts(app)["video"] == 0


def test_missing_and_malformed_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    project = create_project("Missing", local_appdata=tmp_path)
    add_project_source(
        project["project_id"], "E:/Siruela 2", "E", local_appdata=tmp_path
    )
    app = _material_app()
    app.count_labels["video"].set("7")
    app._restore_persisted_analysis_result(project["project_id"])
    assert _counts(app)["video"] == 0

    path = project_analysis_display_summary_path(
        project["project_id"], local_appdata=tmp_path
    )
    path.write_text("{bad", encoding="utf-8")
    app.count_labels["video"].set("8")
    app._restore_persisted_analysis_result(project["project_id"])
    assert _counts(app)["video"] == 0


def test_project_switch_isolation(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    a = create_project("A", local_appdata=tmp_path)
    b = create_project("B", local_appdata=tmp_path)
    sa = add_project_source(a["project_id"], "E:/A", "A", local_appdata=tmp_path)
    sb = add_project_source(b["project_id"], "E:/B", "B", local_appdata=tmp_path)
    _save_summary(
        tmp_path,
        a["project_id"],
        sa["source_id"],
        sa["current_location"],
        total_files=10,
        media_files=10,
        video=10,
        audio=0,
        images=0,
        other=0,
    )
    # Override incident for A
    summary_a = load_project_analysis_display_summary(
        a["project_id"], local_appdata=tmp_path
    )
    summary_a["metadata"]["incident_count"] = 1
    save_project_analysis_display_summary(summary_a, local_appdata=tmp_path)

    summary_b = build_project_analysis_display_summary(
        b["project_id"],
        analyzed_sources=[
            {"source_id": sb["source_id"], "current_location": sb["current_location"]}
        ],
        scan={
            "total_files": 5,
            "media_files": 5,
            "video": 5,
            "audio": 0,
            "images": 0,
            "other": 0,
            "errors": 0,
            "warnings": 0,
        },
        incident_count=0,
    )
    save_project_analysis_display_summary(summary_b, local_appdata=tmp_path)

    app = _material_app()
    app._restore_persisted_analysis_result(a["project_id"])
    assert _counts(app)["video"] == 10
    app._restore_persisted_analysis_result(b["project_id"])
    assert _counts(app)["video"] == 5
    assert _counts(app)["incidents"] == 0


def test_persist_after_successful_material_stage(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    project = create_project("Persist", local_appdata=tmp_path)
    source = add_project_source(
        project["project_id"], "E:/Siruela 2", "E", local_appdata=tmp_path
    )
    project_id = project["project_id"]
    root = source["current_location"]
    roots = {source["source_id"]: root}

    app = object.__new__(gui.ProducerApp)
    app.analysis_project_id = project_id
    app.cancel_event = threading.Event()
    app.ui_q = SimpleNamespace(items=[], put=lambda item: app.ui_q.items.append(item))
    app._analysis_source_labels = {source["source_id"]: "E"}

    scan = {
        "extension_summary": {
            ".mp4": 128,
            ".wav": 1,
            ".jpg": 112,
            ".txt": 144,
        },
        "errors": [],
        "warnings": [],
    }

    monkeypatch.setattr(gui, "build_online_source_root_map", lambda pid: roots)
    monkeypatch.setattr(gui, "scan_read_only_folder", lambda path: scan)
    monkeypatch.setattr(
        gui.ProducerApp,
        "_build_snapshot",
        lambda self, source_id, folder, scanned: {
            "online_root_ids": [source_id],
            "files": [],
        },
    )
    monkeypatch.setattr(
        gui.ProducerApp,
        "_load_or_create_catalog",
        lambda self, *args: {"media_items": {}, "analysis_state": {}},
    )
    monkeypatch.setattr(gui.ProducerApp, "_reuse_map_from_catalog", lambda *args: {})
    monkeypatch.setattr(
        gui,
        "compare_catalogs",
        lambda *args: {"classification": {"NEW": [], "MODIFIED": []}},
    )
    monkeypatch.setattr(
        gui,
        "extract_metadata",
        lambda *args, **kwargs: {
            "results": [{"relative_path": "ok.mp4", "source_id": source["source_id"]}],
            "errors": [
                {
                    "source_id": source["source_id"],
                    "relative_path": "Mariano/Campo/a.MP4",
                },
                {
                    "source_id": source["source_id"],
                    "relative_path": "Mariano/Campo/b.MP4",
                },
            ],
        },
    )
    monkeypatch.setattr(
        gui.ProducerApp, "_apply_metadata_to_catalog", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(gui, "save_catalog", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        gui, "load_signature_cache_runtime", lambda *args, **kwargs: SimpleNamespace()
    )
    monkeypatch.setattr(gui, "select_batch_candidates", lambda *args, **kwargs: [])
    monkeypatch.setattr(gui, "group_related_media", lambda *args, **kwargs: [])
    monkeypatch.setattr(gui, "save_signature_cache_runtime", lambda *args, **kwargs: None)
    monkeypatch.setattr(gui.ProducerApp, "_enrich_project_source_metadata", lambda *a, **k: None)

    app._project_source_analysis(project_id)

    loaded = load_project_analysis_display_summary(project_id, local_appdata=tmp_path)
    assert loaded is not None
    assert loaded["analyzed_sources"] == [
        {"source_id": source["source_id"], "current_location": root}
    ]
    assert loaded["scan"]["video"] == 128
    assert loaded["scan"]["other"] == 144
    assert loaded["scan"]["total_files"] == 385
    assert loaded["scan"]["media_files"] == 241
    assert loaded["metadata"]["incident_count"] == 2
    assert "groups" not in loaded
    assert "clusters" not in loaded


def test_cancelled_run_preserves_prior_valid_summary(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    project = create_project("Cancel", local_appdata=tmp_path)
    source = add_project_source(
        project["project_id"], "E:/Siruela 2", "E", local_appdata=tmp_path
    )
    project_id = project["project_id"]
    _save_summary(
        tmp_path,
        project_id,
        source["source_id"],
        source["current_location"],
        total_files=3,
        media_files=3,
        video=3,
        audio=0,
        images=0,
        other=0,
    )
    prior = load_project_analysis_display_summary(project_id, local_appdata=tmp_path)
    assert prior["scan"]["video"] == 3

    roots = {source["source_id"]: source["current_location"]}
    app = object.__new__(gui.ProducerApp)
    app.analysis_project_id = project_id
    app.cancel_event = threading.Event()
    app.cancel_event.set()
    app.ui_q = SimpleNamespace(items=[], put=lambda item: app.ui_q.items.append(item))
    app._analysis_source_labels = {}

    monkeypatch.setattr(gui, "build_online_source_root_map", lambda pid: roots)
    monkeypatch.setattr(
        gui.ProducerApp,
        "_load_or_create_catalog",
        lambda self, *args: {"media_items": {}},
    )
    monkeypatch.setattr(
        gui.ProducerApp,
        "_finish_cancelled",
        lambda self, catalog, pid: app.ui_q.put(("analysis_finished", "cancelled")),
    )

    # Cancel before first scan iteration completes material result
    app._project_source_analysis(project_id)
    loaded = load_project_analysis_display_summary(project_id, local_appdata=tmp_path)
    assert loaded["scan"]["video"] == 3
    assert loaded["analysis_run_id"] == prior["analysis_run_id"]


def test_aggregate_scan_persistence_helper():
    scans = [
        {
            "extension_summary": {".mp4": 128, ".wav": 1, ".jpg": 112, ".txt": 144},
            "errors": [],
            "warnings": ["MAX_DEPTH_ENTRY_SKIPPED"],
        }
    ]
    block = gui._aggregate_project_scan_persistence(scans)
    assert block == {
        "total_files": 385,
        "media_files": 241,
        "video": 128,
        "audio": 1,
        "images": 112,
        "other": 144,
        "errors": 0,
        "warnings": 1,
    }
