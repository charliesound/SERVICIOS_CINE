from dataclasses import asdict, is_dataclass
import importlib.util
from pathlib import Path
import re
import sys


sys.dont_write_bytecode = True

MODULE_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture.py"
)
TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation.py"
)
PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_PASS_READY_FOR_QA_GATE"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.QA.GATE.V1"
)
PREVIOUS_ARTIFACTS = [
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate_closure_review_v1.md"),
    Path("tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"),
    Path("tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt"),
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py"),
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py"),
]
ALLOWED_RETURNED_PATHS = {
    "tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json",
    "tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt",
    "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py",
}


def load_module():
    spec = importlib.util.spec_from_file_location("cid_local_media_agent_smoke_fixture_impl", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def snapshot_files() -> set[str]:
    root = Path(".")
    return {
        str(path.as_posix())
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def snapshot_stats(paths: list[Path]) -> dict[Path, tuple[int, int]]:
    return {path: (path.stat().st_size, path.stat().st_mtime_ns) for path in paths}


def is_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


def test_module_and_test_exist() -> None:
    assert MODULE_PATH.exists()
    assert TEST_PATH.exists()


def test_previous_artifacts_exist() -> None:
    for artifact in PREVIOUS_ARTIFACTS:
        assert artifact.exists(), artifact


def test_module_declares_phase_previous_result_tag_and_next() -> None:
    module = load_module()
    assert module.PHASE == PHASE
    assert module.PREVIOUS_PHASE == PREVIOUS_PHASE
    assert module.FUNCTIONAL_RESULT == FUNCTIONAL_RESULT
    assert module.FUTURE_TARGET_TAG == TARGET_TAG
    assert module.NEXT_MICROPHASE == NEXT_PHASE


def test_import_has_no_side_effects() -> None:
    before = snapshot_files()
    module = load_module()
    after = snapshot_files()
    assert hasattr(module, "run_controlled_text_artifact_smoke_fixture")
    assert before == after


def test_public_functions_exist() -> None:
    module = load_module()
    assert callable(module.run_controlled_text_artifact_smoke_fixture)
    assert callable(module.compute_text_sha256)
    assert callable(module.normalize_text)


def test_run_returns_safe_structured_result() -> None:
    module = load_module()
    before_files = snapshot_files()
    watched = PREVIOUS_ARTIFACTS + [MODULE_PATH]
    before_stats = snapshot_stats(watched)
    result = module.run_controlled_text_artifact_smoke_fixture()
    after_files = snapshot_files()
    after_stats = snapshot_stats(watched)

    assert is_dataclass(result)
    data = asdict(result)
    assert result.phase == PHASE
    assert result.previous_phase == PREVIOUS_PHASE
    assert result.functional_result == FUNCTIONAL_RESULT
    assert result.text_matches is True
    assert result.actual_text_sha256 == result.expected_text_sha256
    assert is_sha256(result.actual_text_sha256)
    assert is_sha256(result.expected_text_sha256)
    assert result.checked_line_count > 0
    assert result.controlled_payload_fixture_path in ALLOWED_RETURNED_PATHS
    assert result.expected_visible_text_fixture_path in ALLOWED_RETURNED_PATHS
    assert result.renderer_module_path in ALLOWED_RETURNED_PATHS
    assert not Path(result.controlled_payload_fixture_path).is_absolute()
    assert not Path(result.expected_visible_text_fixture_path).is_absolute()
    assert not Path(result.renderer_module_path).is_absolute()
    assert result.real_media_used is False
    assert result.scanner_executed is False
    assert result.ffprobe_executed is False
    assert result.ffmpeg_executed is False
    assert result.subprocess_executed is False
    assert result.network_used is False
    assert result.database_used is False
    assert result.output_file_written is False
    assert result.export_packaging_performed is False
    assert result.artifact_generated is False
    assert result.cli_executed is False
    assert result.renderer_executed_as_process is False
    assert before_files == after_files
    assert before_stats == after_stats

    serialized = str(data)
    for token in ["/home", "/mnt", "C:", "cwd", "secret", "token"]:
        assert token not in serialized


def test_module_source_respects_safety_boundaries() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for token in [
        "import subprocess",
        "from subprocess",
        "subprocess.",
        "requests",
        "httpx",
        "socket",
        "urllib",
        "argparse",
        "print(",
        "logging",
        '__main__',
        "ffprobe -",
        "ffmpeg -",
    ]:
        assert token not in source


def test_module_source_does_not_touch_disallowed_areas() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for token in ["frontend", "backend", "alembic", "docker", "stripe", "credit", "ledger", "ai_jobs"]:
        assert token not in source


def test_hash_helper_is_deterministic() -> None:
    module = load_module()
    text = "alpha\nbeta\n"
    assert module.compute_text_sha256(text) == module.compute_text_sha256(text)
    assert is_sha256(module.compute_text_sha256(text))


def test_normalize_text_is_stable() -> None:
    module = load_module()
    assert module.normalize_text("a\r\nb\r\n") == "a\nb\n"
    assert module.normalize_text("a\nb") == "a\nb\n"
