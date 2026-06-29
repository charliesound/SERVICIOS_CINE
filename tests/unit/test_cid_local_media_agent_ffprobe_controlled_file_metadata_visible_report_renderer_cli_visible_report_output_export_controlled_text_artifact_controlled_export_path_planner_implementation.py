import ast
from pathlib import Path

import pytest


MODULE_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_export_path_planner.py"
)

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_v1.md"
)

PREVIOUS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate_closure_review_v1.md"
)

from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_export_path_planner import (
    CONTROLLED_PATH_BOUNDARY,
    CONTROLLED_VISIBLE_REPORT_TEXT_SUFFIX,
    ControlledTextArtifactExportPathPlannerError,
    plan_controlled_text_artifact_export_path,
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _descriptor(filename: str = "scene_001.controlled_visible_report.txt") -> dict:
    return {
        "suggested_filename": filename,
        "content_sha256": "abc123",
        "write_performed": False,
        "artifact_created_on_disk": False,
    }


def test_path_planner_implementation_files_exist():
    assert MODULE_PATH.exists()
    assert DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_DOC_PATH.exists()


def test_path_planner_implementation_doc_declares_phase_result_and_next_phase():
    text = _read(DOC_PATH)

    assert "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.V1" in text
    assert "PATH_PLANNER_IMPLEMENTATION_PASS_READY_FOR_QA_GATE" in text
    assert "PATH.PLANNER.IMPLEMENTATION.QA.GATE.V1" in text


def test_path_planner_returns_controlled_planned_descriptor_without_writing(tmp_path):
    before = sorted(tmp_path.iterdir())

    result = plan_controlled_text_artifact_export_path(
        controlled_export_root="/controlled/exports",
        controlled_descriptor=_descriptor(),
    )

    after = sorted(tmp_path.iterdir())

    assert before == after
    assert result["controlled_export_root"] == "/controlled/exports"
    assert result["suggested_filename"] == "scene_001.controlled_visible_report.txt"
    assert result["planned_artifact_path"] == "/controlled/exports/scene_001.controlled_visible_report.txt"
    assert result["artifact_format"] == "controlled_visible_report_text"
    assert result["content_sha256"] == "abc123"
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["path_boundary"] == CONTROLLED_PATH_BOUNDARY
    assert result["safety_flags"]["file_write_performed"] is False
    assert result["safety_flags"]["directory_creation_performed"] is False
    assert result["safety_flags"]["artifact_created_on_disk"] is False


@pytest.mark.parametrize(
    "root",
    [
        None,
        "",
        "   ",
        "../exports",
        "/controlled/../exports",
        ".hidden",
        "C:/exports",
        "\\\\server\\share",
    ],
)
def test_path_planner_rejects_unsafe_roots(root):
    with pytest.raises(ControlledTextArtifactExportPathPlannerError):
        plan_controlled_text_artifact_export_path(
            controlled_export_root=root,
            controlled_descriptor=_descriptor(),
        )


@pytest.mark.parametrize(
    "filename",
    [
        None,
        "",
        "   ",
        ".hidden.controlled_visible_report.txt",
        "../scene.controlled_visible_report.txt",
        "scene/001.controlled_visible_report.txt",
        "scene\\001.controlled_visible_report.txt",
        "C:scene.controlled_visible_report.txt",
        "\\\\server\\share\\scene.controlled_visible_report.txt",
        "scene_001.txt",
        "scene_001.controlled_visible_report.md",
    ],
)
def test_path_planner_rejects_unsafe_suggested_filenames(filename):
    with pytest.raises(ControlledTextArtifactExportPathPlannerError):
        plan_controlled_text_artifact_export_path(
            controlled_export_root="/controlled/exports",
            controlled_descriptor=_descriptor(filename),
        )


def test_path_planner_rejects_missing_descriptor_and_missing_suggested_filename():
    with pytest.raises(ControlledTextArtifactExportPathPlannerError):
        plan_controlled_text_artifact_export_path(
            controlled_export_root="/controlled/exports",
            controlled_descriptor=None,
        )

    with pytest.raises(ControlledTextArtifactExportPathPlannerError):
        plan_controlled_text_artifact_export_path(
            controlled_export_root="/controlled/exports",
            controlled_descriptor={},
        )


def test_path_planner_suffix_constant_matches_contract():
    assert CONTROLLED_VISIBLE_REPORT_TEXT_SUFFIX == ".controlled_visible_report.txt"


def test_path_planner_source_has_no_filesystem_write_or_runtime_execution_calls():
    source = _read(MODULE_PATH)

    forbidden_tokens = [
        "open(",
        ".write(",
        ".mkdir(",
        ".unlink(",
        ".rmdir(",
        "subprocess.run",
        "subprocess.Popen",
        "ffprobe ",
        "ffmpeg ",
        "requests.",
        "httpx.",
        "socket.",
        "os.environ",
        "argparse.",
        "click.",
        "typer.",
    ]

    for token in forbidden_tokens:
        assert token not in source

    required_false_safety_flags = [
        "\"ffprobe_execution_performed\": False",
        "\"ffmpeg_execution_performed\": False",
        "\"subprocess_execution_performed\": False",
        "\"file_write_performed\": False",
        "\"directory_creation_performed\": False",
        "\"artifact_created_on_disk\": False",
    ]

    for flag in required_false_safety_flags:
        assert flag in source


def test_path_planner_module_imports_are_safe():
    tree = ast.parse(_read(MODULE_PATH))

    forbidden_import_roots = {
        "os",
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "urllib",
        "ftplib",
        "smtplib",
        "argparse",
        "click",
        "typer",
        "shutil",
    }

    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert imported_roots.isdisjoint(forbidden_import_roots)


def test_path_planner_doc_preserves_non_authorization_boundary():
    text = _read(DOC_PATH).lower()

    required_phrases = [
        "it does not write files",
        "it does not create directories",
        "it does not create artifacts on disk",
        "it does not scan folders",
        "it does not execute ffprobe or ffmpeg",
        "it does not execute subprocesses or external processes",
        "it does not access the network",
        "it does not touch saas, database, backend, frontend, installer, or client-facing code",
    ]

    for phrase in required_phrases:
        assert phrase in text
