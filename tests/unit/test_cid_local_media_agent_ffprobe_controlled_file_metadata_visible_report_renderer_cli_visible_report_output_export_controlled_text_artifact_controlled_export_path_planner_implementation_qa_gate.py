import ast
import inspect
from pathlib import Path

import pytest

from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_export_path_planner import (
    CONTROLLED_PATH_BOUNDARY,
    CONTROLLED_VISIBLE_REPORT_TEXT_SUFFIX,
    ControlledTextArtifactExportPathPlannerError,
    plan_controlled_text_artifact_export_path,
)


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_qa_gate_v1.md"
)

IMPLEMENTATION_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_v1.md"
)

IMPLEMENTATION_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation.py"
)

IMPLEMENTATION_MODULE_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_export_path_planner.py"
)

PREVIOUS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate_closure_review_v1.md"
)

PREVIOUS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate_closure_review.py"
)

PREVIOUS_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate_v1.md"
)

PREVIOUS_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate.py"
)

PLANNER_CONTRACT_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_v1.md"
)

PLANNER_CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract.py"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.QA.GATE.V1"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.V1"
PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_PASS_READY_FOR_QA_GATE"
RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_QA_GATE_PASS_CLOSED"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _descriptor(filename: str = "scene_001.controlled_visible_report.txt") -> dict:
    return {
        "suggested_filename": filename,
        "content_sha256": "abc123",
        "write_performed": False,
        "artifact_created_on_disk": False,
    }


def test_path_planner_implementation_qa_gate_files_exist():
    assert DOC_PATH.exists()
    assert IMPLEMENTATION_DOC_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()
    assert IMPLEMENTATION_MODULE_PATH.exists()
    assert PREVIOUS_CLOSURE_DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()
    assert PREVIOUS_QA_GATE_DOC_PATH.exists()
    assert PREVIOUS_QA_GATE_TEST_PATH.exists()
    assert PLANNER_CONTRACT_DOC_PATH.exists()
    assert PLANNER_CONTRACT_TEST_PATH.exists()


def test_path_planner_implementation_qa_gate_doc_declares_phase_result_and_next_phase():
    text = _read(DOC_PATH)

    assert PHASE in text
    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert RESULT in text
    assert NEXT_PHASE in text


def test_path_planner_implementation_qa_gate_references_implementation_chain():
    text = _read(DOC_PATH)

    required_paths = [
        IMPLEMENTATION_DOC_PATH,
        IMPLEMENTATION_MODULE_PATH,
        IMPLEMENTATION_TEST_PATH,
        PREVIOUS_CLOSURE_DOC_PATH,
        PREVIOUS_CLOSURE_TEST_PATH,
        PREVIOUS_QA_GATE_DOC_PATH,
        PREVIOUS_QA_GATE_TEST_PATH,
        PLANNER_CONTRACT_DOC_PATH,
        PLANNER_CONTRACT_TEST_PATH,
    ]

    for path in required_paths:
        assert str(path) in text


def test_path_planner_implementation_qa_gate_doc_is_doc_and_test_only():
    text = _read(DOC_PATH)

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not modify the planner implementation.",
        "It does not connect the planner to the exporter.",
        "It does not write files.",
        "It does not create directories.",
        "It does not create artifacts on disk.",
        "It does not scan folders.",
        "It does not execute ffprobe or FFmpeg.",
        "It does not execute subprocesses or external processes.",
        "It does not access the network.",
        "It does not touch SaaS, database, backend, frontend, installer, or client-facing code.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_path_planner_implementation_qa_gate_validates_function_signature():
    signature = inspect.signature(plan_controlled_text_artifact_export_path)

    assert list(signature.parameters) == [
        "controlled_export_root",
        "controlled_descriptor",
    ]

    for parameter in signature.parameters.values():
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_path_planner_implementation_qa_gate_validates_success_descriptor_without_writing(tmp_path):
    before = sorted(tmp_path.iterdir())

    result = plan_controlled_text_artifact_export_path(
        controlled_export_root=str(tmp_path),
        controlled_descriptor=_descriptor(),
    )

    after = sorted(tmp_path.iterdir())

    assert before == after
    assert result["controlled_export_root"] == str(tmp_path)
    assert result["suggested_filename"] == "scene_001.controlled_visible_report.txt"
    assert result["planned_artifact_path"] == str(tmp_path / "scene_001.controlled_visible_report.txt")
    assert result["artifact_format"] == "controlled_visible_report_text"
    assert result["content_sha256"] == "abc123"
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["path_boundary"] == CONTROLLED_PATH_BOUNDARY


def test_path_planner_implementation_qa_gate_validates_safety_flags_are_false():
    result = plan_controlled_text_artifact_export_path(
        controlled_export_root="/controlled/exports",
        controlled_descriptor=_descriptor(),
    )

    expected_flags = {
        "real_media_access_performed",
        "scanner_execution_performed",
        "ffprobe_execution_performed",
        "ffmpeg_execution_performed",
        "subprocess_execution_performed",
        "network_access_performed",
        "saas_or_database_access_performed",
        "file_write_performed",
        "directory_creation_performed",
        "artifact_created_on_disk",
    }

    assert set(result["safety_flags"]) == expected_flags

    for value in result["safety_flags"].values():
        assert value is False


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
def test_path_planner_implementation_qa_gate_rejects_unsafe_roots(root):
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
def test_path_planner_implementation_qa_gate_rejects_unsafe_filenames(filename):
    with pytest.raises(ControlledTextArtifactExportPathPlannerError):
        plan_controlled_text_artifact_export_path(
            controlled_export_root="/controlled/exports",
            controlled_descriptor=_descriptor(filename),
        )


def test_path_planner_implementation_qa_gate_rejects_missing_descriptor_and_missing_filename():
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


def test_path_planner_implementation_qa_gate_suffix_and_boundary_constants_match_contract():
    assert CONTROLLED_VISIBLE_REPORT_TEXT_SUFFIX == ".controlled_visible_report.txt"
    assert CONTROLLED_PATH_BOUNDARY == "controlled_export_root"


def test_path_planner_implementation_qa_gate_module_imports_are_safe():
    tree = ast.parse(_read(IMPLEMENTATION_MODULE_PATH))

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


def test_path_planner_implementation_qa_gate_module_has_no_runtime_calls():
    source = _read(IMPLEMENTATION_MODULE_PATH)

    forbidden_tokens = [
        "open(",
        ".write(",
        ".mkdir(",
        ".unlink(",
        ".rmdir(",
        "subprocess.run",
        "subprocess.Popen",
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


def test_path_planner_implementation_qa_gate_module_preserves_required_false_flags():
    source = _read(IMPLEMENTATION_MODULE_PATH)

    required_false_safety_flags = [
        "\"ffprobe_execution_performed\": False",
        "\"ffmpeg_execution_performed\": False",
        "\"subprocess_execution_performed\": False",
        "\"network_access_performed\": False",
        "\"saas_or_database_access_performed\": False",
        "\"file_write_performed\": False",
        "\"directory_creation_performed\": False",
        "\"artifact_created_on_disk\": False",
    ]

    for flag in required_false_safety_flags:
        assert flag in source


def test_path_planner_implementation_qa_gate_implementation_doc_supports_qa_gate():
    text = _read(IMPLEMENTATION_DOC_PATH)

    required_phrases = [
        "Implement the first controlled pure export path planner.",
        "It calculates a planned path descriptor only.",
        "It does not write files.",
        "It does not create directories.",
        "It does not create artifacts on disk.",
        "It does not scan folders.",
        "It does not execute ffprobe or FFmpeg.",
        "It does not execute subprocesses or external processes.",
        "It does not access the network.",
        "PATH_PLANNER_IMPLEMENTATION_PASS_READY_FOR_QA_GATE",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_path_planner_implementation_qa_gate_previous_closure_supports_transition():
    text = _read(PREVIOUS_CLOSURE_DOC_PATH)

    required_phrases = [
        "The controlled export path planner implementation readiness gate QA gate is closed.",
        "The chain is ready only for a future controlled path planner implementation phase.",
        "A future controlled implementation phase may add only a pure path planner.",
        "That future planner must not write files.",
        "That future planner must not create directories.",
        "That future planner must not create artifacts on disk.",
        "PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_PATH_PLANNER_IMPLEMENTATION_PHASE",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_path_planner_implementation_qa_gate_contract_supports_implementation_limits():
    text = _read(PLANNER_CONTRACT_DOC_PATH)

    required_phrases = [
        "A later controlled implementation phase may add only a pure path planner.",
        "That future planner must be deterministic.",
        "That future planner must be local-only.",
        "That future planner must be side-effect free.",
        "That future planner must only calculate and return a planned path descriptor.",
        "That future planner must not write files.",
        "That future planner must not create directories.",
        "That future planner must not create artifacts on disk.",
        "That future planner must not scan folders.",
        "That future planner must not execute ffprobe or FFmpeg.",
        "That future planner must not execute subprocesses or external processes.",
        "That future planner must not access the network.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_path_planner_implementation_qa_gate_non_authorization_is_complete():
    text = _read(DOC_PATH).lower()

    required_phrases = [
        "does not authorize connecting the planner to the exporter",
        "does not authorize path resolver expansion",
        "does not authorize file writing",
        "does not authorize directory creation",
        "does not authorize artifact generation on disk",
        "does not authorize real media",
        "does not authorize arbitrary folders",
        "does not authorize scanner execution",
        "does not authorize ffprobe or ffmpeg execution",
        "does not authorize subprocess or process execution",
        "does not authorize audio extraction",
        "does not authorize sync",
        "does not authorize transcription",
        "does not authorize subtitles",
        "does not authorize timeline export",
        "does not authorize network access",
        "does not authorize saas or database integration",
        "does not authorize installer work",
        "does not authorize public demo, client demo, sales demo, or production use",
    ]

    for phrase in required_phrases:
        assert phrase in text
