"""Unit tests for project_analysis_display_summary persistence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.local_media_agent.local_project import create_project
from scripts.local_media_agent.project_analysis_display_summary import (
    CID_DISPLAY_SUMMARY_INVALID,
    CID_DISPLAY_SUMMARY_PROJECT_MISMATCH,
    CID_DISPLAY_SUMMARY_UNSUPPORTED_VERSION,
    DISPLAY_SUMMARY_FILENAME,
    DISPLAY_SUMMARY_SCHEMA_VERSION,
    ProjectAnalysisDisplaySummaryError,
    build_project_analysis_display_summary,
    incident_count_from_summary,
    is_displayable_summary,
    load_project_analysis_display_summary,
    material_counts_from_summary,
    project_analysis_display_summary_path,
    save_project_analysis_display_summary,
)
from scripts.local_media_agent.project_sources import (
    STATE_OFFLINE,
    STATE_ONLINE,
    add_project_source,
    update_source_state,
)


def _scan_block(**overrides):
    base = {
        "total_files": 385,
        "media_files": 241,
        "video": 128,
        "audio": 1,
        "images": 112,
        "other": 144,
        "errors": 0,
        "warnings": 0,
    }
    base.update(overrides)
    return base


def _sources(source_id: str, location: str):
    return [{"source_id": source_id, "current_location": location}]


def test_roundtrip_persists_all_required_fields(tmp_path):
    project = create_project("Resumen", local_appdata=tmp_path)
    project_id = project["project_id"]
    source_id = "SRC-aaaaaaa1-1111-4111-8111-111111111111"
    summary = build_project_analysis_display_summary(
        project_id,
        analyzed_sources=_sources(source_id, "E:/Siruela 2"),
        scan=_scan_block(),
        incident_count=2,
        analysis_run_id="run-test-1",
    )
    path = save_project_analysis_display_summary(summary, local_appdata=tmp_path)
    assert path.name == DISPLAY_SUMMARY_FILENAME
    loaded = load_project_analysis_display_summary(project_id, local_appdata=tmp_path)
    assert loaded is not None
    assert loaded["schema_version"] == DISPLAY_SUMMARY_SCHEMA_VERSION
    assert loaded["project_id"] == project_id
    assert loaded["analysis_run_id"] == "run-test-1"
    assert loaded["analyzed_sources"] == [
        {"source_id": source_id, "current_location": "E:/Siruela 2"}
    ]
    assert loaded["scan"] == _scan_block()
    assert loaded["metadata"]["incident_count"] == 2
    assert material_counts_from_summary(loaded) == {
        "video": 128,
        "audio": 1,
        "images": 112,
        "other": 144,
    }
    assert incident_count_from_summary(loaded) == 2


def test_analyzed_sources_sorted_by_source_id(tmp_path):
    project = create_project("Orden", local_appdata=tmp_path)
    summary = build_project_analysis_display_summary(
        project["project_id"],
        analyzed_sources=[
            {"source_id": "SRC-bbbbbbb2-2222-4222-8222-222222222222", "current_location": "B:/x"},
            {"source_id": "SRC-aaaaaaa1-1111-4111-8111-111111111111", "current_location": "A:/x"},
        ],
        scan=_scan_block(total_files=10, media_files=10, video=10, audio=0, images=0, other=0),
        incident_count=0,
    )
    assert [item["source_id"] for item in summary["analyzed_sources"]] == [
        "SRC-aaaaaaa1-1111-4111-8111-111111111111",
        "SRC-bbbbbbb2-2222-4222-8222-222222222222",
    ]


def test_missing_artifact_returns_none(tmp_path):
    project = create_project("Sin resumen", local_appdata=tmp_path)
    assert (
        load_project_analysis_display_summary(
            project["project_id"], local_appdata=tmp_path
        )
        is None
    )


def test_malformed_json_fail_closed(tmp_path):
    project = create_project("Roto", local_appdata=tmp_path)
    path = project_analysis_display_summary_path(
        project["project_id"], local_appdata=tmp_path
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(ProjectAnalysisDisplaySummaryError) as exc_info:
        load_project_analysis_display_summary(
            project["project_id"], local_appdata=tmp_path
        )
    assert exc_info.value.code == CID_DISPLAY_SUMMARY_INVALID


def test_incomplete_schema_fail_closed(tmp_path):
    project = create_project("Incompleto", local_appdata=tmp_path)
    path = project_analysis_display_summary_path(
        project["project_id"], local_appdata=tmp_path
    )
    path.write_text(
        json.dumps({"schema_version": 1, "project_id": project["project_id"]}),
        encoding="utf-8",
    )
    with pytest.raises(ProjectAnalysisDisplaySummaryError) as exc_info:
        load_project_analysis_display_summary(
            project["project_id"], local_appdata=tmp_path
        )
    assert exc_info.value.code == CID_DISPLAY_SUMMARY_INVALID


def test_unsupported_schema_version_fail_closed(tmp_path):
    project = create_project("Version", local_appdata=tmp_path)
    summary = build_project_analysis_display_summary(
        project["project_id"],
        analyzed_sources=_sources("SRC-aaaaaaa1-1111-4111-8111-111111111111", "E:/x"),
        scan=_scan_block(total_files=1, media_files=1, video=1, audio=0, images=0, other=0),
        incident_count=0,
    )
    summary["schema_version"] = 99
    path = project_analysis_display_summary_path(
        project["project_id"], local_appdata=tmp_path
    )
    path.write_text(json.dumps(summary), encoding="utf-8")
    with pytest.raises(ProjectAnalysisDisplaySummaryError) as exc_info:
        load_project_analysis_display_summary(
            project["project_id"], local_appdata=tmp_path
        )
    assert exc_info.value.code == CID_DISPLAY_SUMMARY_UNSUPPORTED_VERSION


def test_invalid_counts_fail_closed():
    project_id = "PRJ-11111111-1111-4111-8111-111111111111"
    with pytest.raises(ProjectAnalysisDisplaySummaryError):
        build_project_analysis_display_summary(
            project_id,
            analyzed_sources=_sources("SRC-aaaaaaa1-1111-4111-8111-111111111111", "E:/x"),
            scan=_scan_block(total_files=10, media_files=5, video=1, audio=1, images=1, other=1),
            incident_count=0,
        )
    with pytest.raises(ProjectAnalysisDisplaySummaryError):
        build_project_analysis_display_summary(
            project_id,
            analyzed_sources=_sources("SRC-aaaaaaa1-1111-4111-8111-111111111111", "E:/x"),
            scan=_scan_block(video=-1),
            incident_count=0,
        )


def test_project_id_mismatch_on_load(tmp_path):
    first = create_project("Uno", local_appdata=tmp_path)
    second = create_project("Dos", local_appdata=tmp_path)
    summary = build_project_analysis_display_summary(
        first["project_id"],
        analyzed_sources=_sources("SRC-aaaaaaa1-1111-4111-8111-111111111111", "E:/x"),
        scan=_scan_block(total_files=1, media_files=1, video=1, audio=0, images=0, other=0),
        incident_count=0,
    )
    path = project_analysis_display_summary_path(
        second["project_id"], local_appdata=tmp_path
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary), encoding="utf-8")
    with pytest.raises(ProjectAnalysisDisplaySummaryError) as exc_info:
        load_project_analysis_display_summary(
            second["project_id"], local_appdata=tmp_path
        )
    assert exc_info.value.code == CID_DISPLAY_SUMMARY_PROJECT_MISMATCH


def test_atomic_write_replaces_prior_valid_file(tmp_path):
    project = create_project("Atomico", local_appdata=tmp_path)
    project_id = project["project_id"]
    source = _sources("SRC-aaaaaaa1-1111-4111-8111-111111111111", "E:/x")
    first = build_project_analysis_display_summary(
        project_id,
        analyzed_sources=source,
        scan=_scan_block(total_files=1, media_files=1, video=1, audio=0, images=0, other=0),
        incident_count=0,
        analysis_run_id="first",
    )
    save_project_analysis_display_summary(first, local_appdata=tmp_path)
    second = build_project_analysis_display_summary(
        project_id,
        analyzed_sources=source,
        scan=_scan_block(),
        incident_count=2,
        analysis_run_id="second",
    )
    save_project_analysis_display_summary(second, local_appdata=tmp_path)
    loaded = load_project_analysis_display_summary(project_id, local_appdata=tmp_path)
    assert loaded["analysis_run_id"] == "second"
    assert loaded["metadata"]["incident_count"] == 2
    leftovers = list(
        Path(project_analysis_display_summary_path(project_id, local_appdata=tmp_path).parent).glob(
            ".project_analysis_display_summary.json*.tmp"
        )
    )
    assert leftovers == []


def test_displayable_scope_rules(tmp_path):
    project = create_project("Alcance", local_appdata=tmp_path)
    project_id = project["project_id"]
    e_id = add_project_source(project_id, "E:/Siruela 2", "Siruela 2", local_appdata=tmp_path)[
        "source_id"
    ]
    f_id = add_project_source(project_id, "F:/SIRUELA", "SIRUELA", local_appdata=tmp_path)[
        "source_id"
    ]
    update_source_state(project_id, f_id, STATE_OFFLINE, local_appdata=tmp_path)
    summary = build_project_analysis_display_summary(
        project_id,
        analyzed_sources=_sources(e_id, "E:/Siruela 2"),
        scan=_scan_block(),
        incident_count=2,
    )
    sources = [
        {"source_id": e_id, "current_location": "E:/Siruela 2", "state": STATE_ONLINE},
        {"source_id": f_id, "current_location": "F:/SIRUELA", "state": STATE_OFFLINE},
    ]
    assert is_displayable_summary(
        summary,
        project_id=project_id,
        project_sources=sources,
        online_source_ids={e_id},
    )
    assert not is_displayable_summary(
        summary,
        project_id=project_id,
        project_sources=sources,
        online_source_ids={e_id, f_id},
    )
    relocated = [
        {"source_id": e_id, "current_location": "E:/Other", "state": STATE_ONLINE},
        {"source_id": f_id, "current_location": "F:/SIRUELA", "state": STATE_OFFLINE},
    ]
    assert not is_displayable_summary(
        summary,
        project_id=project_id,
        project_sources=relocated,
        online_source_ids={e_id},
    )
