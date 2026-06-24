from dataclasses import asdict, is_dataclass
import importlib.util
from pathlib import Path
import re
import sys


sys.dont_write_bytecode = True

QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate_v1.md"
)
MODULE_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture.py"
)
IMPLEMENTATION_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation.py"
)
PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_QA_GATE_PASS_CLOSED"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-qa-gate-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)
IMPLEMENTATION_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.V1"
)
IMPLEMENTATION_PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)
IMPLEMENTATION_FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_PASS_READY_FOR_QA_GATE"
)
IMPLEMENTATION_TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-v1-20260622"
)
IMPLEMENTATION_NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.QA.GATE.V1"
)
REQUIRED_ARTIFACTS = [
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture.py"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate_closure_review_v1.md"),
    Path("tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"),
    Path("tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt"),
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py"),
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py"),
]
PROHIBITED_TOKENS = [
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
    "__main__",
    "ffprobe -",
    "ffmpeg -",
    "os.environ",
    "expanduser",
    "home()",
    "mkdir",
    "write_text",
    "open(",
    "Path.cwd",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def is_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


def load_module():
    spec = importlib.util.spec_from_file_location("cid_local_media_agent_smoke_fixture_impl_for_qa", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def snapshot_files() -> set[str]:
    return {
        str(path.as_posix())
        for path in Path(".").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def snapshot_stats(paths: list[Path]) -> dict[Path, tuple[int, int]]:
    return {path: (path.stat().st_size, path.stat().st_mtime_ns) for path in paths}


def test_qa_gate_doc_exists_and_exact_phase_is_declared() -> None:
    assert QA_DOC.exists()
    assert PHASE in read(QA_DOC)


def test_exact_previous_phase_functional_result_target_tag_and_next_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        NEXT_PHASE,
    ])


def test_qa_gate_declares_required_sections_and_scope() -> None:
    assert_all_present(read(QA_DOC), [
        "QA gate documentation",
        "document-only QA gate",
        "validates the previous implementation contract",
        "previous implementation is closed conceptually",
        "ready only for future closure review or a later explicit phase",
        "## Phase",
        "## Objective",
        "## Previous Closed Phase",
        "## QA Gate Scope",
        "## Required Existing Artifacts",
        "## Validated Implementation Surface",
        "## Validated Deterministic Result Contract",
        "## Validated Safety Flags",
        "## Validated Privacy Boundaries",
        "## Non-Authorization Boundaries",
        "## QA Gate Decision",
        "## Functional Result",
        "## Future Target Tag",
        "## Next Microphase",
    ])


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = read(QA_DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact
        assert str(artifact) in text
    assert IMPLEMENTATION_TEST_PATH.exists()


def test_module_constants_and_surface_are_declared() -> None:
    source = read(MODULE_PATH)
    assert_all_present(source, [
        'PHASE = (',
        'PREVIOUS_PHASE = (',
        'FUNCTIONAL_RESULT = (',
        'FUTURE_TARGET_TAG = (',
        'NEXT_MICROPHASE = (',
        'class ControlledTextArtifactSmokeFixtureResult',
        'def run_controlled_text_artifact_smoke_fixture()',
        'def compute_text_sha256(text: str) -> str:',
        'def normalize_text(text: str) -> str:',
        'CONTROLLED_PAYLOAD_FIXTURE_PATH = (',
        'EXPECTED_VISIBLE_TEXT_FIXTURE_PATH = (',
        'RENDERER_MODULE_PATH = (',
    ])


def test_module_import_and_result_contract() -> None:
    before_files = snapshot_files()
    watched = REQUIRED_ARTIFACTS + [MODULE_PATH]
    before_stats = snapshot_stats(watched)
    module = load_module()
    after_import_files = snapshot_files()
    result = module.run_controlled_text_artifact_smoke_fixture()
    after_files = snapshot_files()
    after_stats = snapshot_stats(watched)

    assert before_files == after_import_files
    assert before_files == after_files
    assert before_stats == after_stats
    assert module.PHASE == IMPLEMENTATION_PHASE
    assert module.PREVIOUS_PHASE == IMPLEMENTATION_PREVIOUS_PHASE
    assert module.FUNCTIONAL_RESULT == IMPLEMENTATION_FUNCTIONAL_RESULT
    assert module.FUTURE_TARGET_TAG == IMPLEMENTATION_TARGET_TAG
    assert module.NEXT_MICROPHASE == IMPLEMENTATION_NEXT_PHASE
    assert is_dataclass(result)
    data = asdict(result)
    assert result.text_matches is True
    assert result.actual_text_sha256 == result.expected_text_sha256
    assert is_sha256(result.actual_text_sha256)
    assert is_sha256(result.expected_text_sha256)
    assert result.checked_line_count > 0
    for key in [
        "phase",
        "previous_phase",
        "functional_result",
        "controlled_payload_fixture_path",
        "expected_visible_text_fixture_path",
        "renderer_module_path",
        "actual_text_sha256",
        "expected_text_sha256",
        "text_matches",
        "checked_line_count",
        "real_media_used",
        "scanner_executed",
        "ffprobe_executed",
        "ffmpeg_executed",
        "subprocess_executed",
        "network_used",
        "database_used",
        "output_file_written",
        "export_packaging_performed",
        "artifact_generated",
        "cli_executed",
        "renderer_executed_as_process",
    ]:
        assert key in data
    for path_value in [
        result.controlled_payload_fixture_path,
        result.expected_visible_text_fixture_path,
        result.renderer_module_path,
    ]:
        assert not Path(path_value).is_absolute()
    serialized = str(data)
    for token in ["/home", "/mnt", "C:\\", "cwd", "secret", "token"]:
        assert token not in serialized
    for flag in [
        result.real_media_used,
        result.scanner_executed,
        result.ffprobe_executed,
        result.ffmpeg_executed,
        result.subprocess_executed,
        result.network_used,
        result.database_used,
        result.output_file_written,
        result.export_packaging_performed,
        result.artifact_generated,
        result.cli_executed,
        result.renderer_executed_as_process,
    ]:
        assert flag is False


def test_module_and_previous_test_validate_main_restrictions() -> None:
    module_source = read(MODULE_PATH)
    test_source = read(IMPLEMENTATION_TEST_PATH)
    for token in PROHIBITED_TOKENS:
        assert token not in module_source
    for token in [
        "text_matches is True",
        "actual_text_sha256 == result.expected_text_sha256",
        "result.output_file_written is False",
        "result.artifact_generated is False",
        "result.cli_executed is False",
        "result.renderer_executed_as_process is False",
        "result.real_media_used is False",
        "result.scanner_executed is False",
        "result.ffprobe_executed is False",
        "result.ffmpeg_executed is False",
        "result.subprocess_executed is False",
        "result.network_used is False",
        "result.database_used is False",
    ]:
        assert token in test_source


def test_no_forbidden_authorization_phrases_in_qa_gate() -> None:
    text = read(QA_DOC).lower()
    for phrase in [
        "authorizes real media",
        "authorizes scanner",
        "authorizes ffprobe",
        "authorizes ffmpeg",
        "authorizes audio extraction",
        "authorizes sync",
        "authorizes transcription",
        "authorizes subtitles",
        "authorizes timeline export",
        "authorizes network",
        "authorizes saas",
        "authorizes db",
        "authorizes installer",
        "authorizes production",
        "ready for client",
        "ready for sales demo",
        "ready for public demo",
        "export implementation is authorized",
        "packaging implementation is authorized",
        "file writing is authorized",
        "artifact generation is authorized",
        "smoke fixture implementation is authorized",
        "client export is authorized",
        "production export is authorized",
    ]:
        assert phrase not in text


def test_no_forbidden_authorization_phrases_in_module() -> None:
    text = read(MODULE_PATH).lower()
    for phrase in [
        "authorizes real media",
        "authorizes scanner",
        "authorizes ffprobe",
        "authorizes ffmpeg",
        "authorizes audio extraction",
        "authorizes sync",
        "authorizes transcription",
        "authorizes subtitles",
        "authorizes timeline export",
        "authorizes network",
        "authorizes saas",
        "authorizes db",
        "authorizes installer",
        "authorizes production",
        "ready for client",
        "ready for sales demo",
        "ready for public demo",
        "export implementation is authorized",
        "packaging implementation is authorized",
        "file writing is authorized",
        "artifact generation is authorized",
        "smoke fixture implementation is authorized",
        "client export is authorized",
        "production export is authorized",
    ]:
        assert phrase not in text


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [QA_DOC, MODULE_PATH, IMPLEMENTATION_TEST_PATH]:
        assert forbidden_prefix not in path.read_text(encoding="utf-8")
