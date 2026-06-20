import json
import subprocess
import sys
from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_qa_gate_v1.md")
SOURCE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_v1.md")
SCRIPT = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py")
SOURCE_TEST = Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1"
QA_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.QA.GATE.V1"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        text=True,
        capture_output=True,
    )


def controlled_empty_fixture() -> Path:
    root = Path("/tmp/cid_local_media_agent_controlled_ffprobe")
    root.mkdir(parents=True, exist_ok=True)
    fixture = root / "qa_gate_empty_controlled_fixture.mov"
    fixture.write_bytes(b"")
    return fixture


def test_qa_gate_phase_and_acceptance_result_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        QA_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_QA_GATE_PASS_CLOSED",
        "PASS_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_VALIDATED",
    ])


def test_source_stable_state_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "5c8d1d96c128bf3b8457dac71e55b83d18759ca8",
        "feat: add CID Local Media Agent ffprobe controlled metadata preflight",
        "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-preflight-v1-20260620",
        PHASE,
    ])


def test_required_source_files_exist() -> None:
    assert QA_DOC.exists()
    assert SOURCE_DOC.exists()
    assert SCRIPT.exists()
    assert SOURCE_TEST.exists()


def test_required_behavior_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "require `--input`",
        "require `--json`",
        "require `--controlled-fixture`",
        "reject uncontrolled paths",
        "reject missing controlled fixture authorization",
        "reject unexpected positional arguments",
        "use ffprobe only for metadata JSON",
        "never call ffmpeg",
        "never scan real folders",
        "never process real media",
        "redact full input paths from JSON output",
        "preserve safe failure behavior",
    ])


def test_required_boundaries_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "real media or rodaje material",
        "arbitrary folders",
        "scanner execution",
        "ffmpeg media processing",
        "audio extraction",
        "sync",
        "transcription",
        "subtitles",
        "timeline export",
        "SaaS upload",
        "database writes",
        "installer creation",
        "client-facing use",
        "public demo",
        "sales demo",
        "production use",
    ])


def test_safe_json_fields_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "`phase`",
        "`result`",
        "`input_policy`",
        "`input_path_redacted`",
        "`ffprobe_command_kind`",
        "`metadata.format`",
        "`metadata.streams`",
        "`media_processing_performed`",
        "`scanner_executed`",
        "`real_media_used`",
        "`ffmpeg_used`",
        "`audio_extraction_performed`",
        "`sync_generated`",
        "`transcription_generated`",
        "`subtitles_generated`",
        "`timeline_export_generated`",
        "`database_write`",
        "`saas_upload`",
        "`network_call`",
    ])


def test_controlled_empty_fixture_json_is_safe_and_redacted() -> None:
    fixture = controlled_empty_fixture()
    result = run_cli("--input", str(fixture), "--json", "--controlled-fixture")
    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout)

    assert payload["phase"] == PHASE
    assert payload["input_policy"] == "controlled_fixture_only"
    assert payload["input_path_redacted"] == fixture.name
    assert "/tmp/cid_local_media_agent_controlled_ffprobe" not in result.stdout
    assert payload["ffprobe_command_kind"] == "metadata_json"
    assert "metadata" in payload
    assert "format" in payload["metadata"]
    assert "streams" in payload["metadata"]

    for flag in [
        "media_processing_performed",
        "scanner_executed",
        "real_media_used",
        "ffmpeg_used",
        "audio_extraction_performed",
        "sync_generated",
        "transcription_generated",
        "subtitles_generated",
        "timeline_export_generated",
        "database_write",
        "saas_upload",
        "network_call",
    ]:
        assert payload[flag] is False


def test_uncontrolled_path_is_rejected() -> None:
    result = run_cli("--input", "/tmp/fake.mov", "--json", "--controlled-fixture")
    assert result.returncode != 0
    assert "--input must be under a controlled fixture root" in result.stderr


def test_missing_controlled_fixture_flag_is_rejected() -> None:
    fixture = controlled_empty_fixture()
    result = run_cli("--input", str(fixture), "--json")
    assert result.returncode != 0
    assert "--controlled-fixture" in result.stderr


def test_unexpected_positional_argument_is_rejected() -> None:
    result = run_cli("unexpected.mov", "--input", "/tmp/fake.mov", "--json", "--controlled-fixture")
    assert result.returncode != 0
    assert "unrecognized arguments" in result.stderr


def test_forbidden_imports_and_ffmpeg_execution_are_not_present() -> None:
    content = read(SCRIPT)
    forbidden = [
        "import requests",
        "import httpx",
        "import socket",
        "import sqlalchemy",
        "import fastapi",
        "from requests",
        "from httpx",
        "from socket",
        "from sqlalchemy",
        "from fastapi",
    ]
    for item in forbidden:
        assert item not in content

    forbidden_ffmpeg_patterns = [
        '"ffmpeg"',
        "'ffmpeg'",
        "ffmpeg -i",
        "ffmpeg -y",
        "ffmpeg -nostdin",
    ]
    for item in forbidden_ffmpeg_patterns:
        assert item not in content


def test_next_safe_phase_is_declared() -> None:
    assert "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.V1" in read(QA_DOC)
