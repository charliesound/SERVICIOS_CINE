import json
import subprocess
import sys
from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffmpeg_local_availability_preflight_qa_gate_v1.md")
SOURCE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffmpeg_local_availability_preflight_v1.md")
SCRIPT = Path("scripts/local_media_agent/ffmpeg_local_availability_preflight.py")
SOURCE_TEST = Path("tests/unit/test_cid_local_media_agent_ffmpeg_local_availability_preflight.py")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, items: list[str]) -> None:
    for item in items:
        assert item in content


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        text=True,
        capture_output=True,
    )


def test_phase_and_acceptance_result() -> None:
    assert_all_present(read(QA_DOC), [
        "CID.LOCAL_MEDIA_AGENT.FFMPEG.LOCAL.AVAILABILITY.PREFLIGHT.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_FFMPEG_LOCAL_AVAILABILITY_PREFLIGHT_QA_GATE_PASS_CLOSED",
    ])


def test_source_stable_state_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "4d6410ae72d37598834acae1adc0249526eb8362",
        "feat: add CID Local Media Agent FFmpeg availability preflight",
        "cid-dev-stable-local-media-agent-ffmpeg-local-availability-preflight-v1-20260620",
        "CID.LOCAL_MEDIA_AGENT.FFMPEG.LOCAL.AVAILABILITY.PREFLIGHT.V1",
    ])


def test_required_source_files_exist() -> None:
    assert SOURCE_DOC.exists()
    assert SCRIPT.exists()
    assert SOURCE_TEST.exists()


def test_required_behavior_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "detect ffmpeg availability",
        "detect ffprobe availability",
        "report ffmpeg path",
        "report ffprobe path",
        "report ffmpeg version line",
        "report ffprobe version line",
        "emit valid JSON through the CLI",
        "accept no media path argument",
        "continue safely when a tool is missing",
        "continue safely when version lookup fails",
        "keep all blocked execution flags false",
    ])


def test_required_safe_flags_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "media_processing_performed: false",
        "scanner_executed: false",
        "real_media_used: false",
        "database_write: false",
        "saas_upload: false",
        "network_call: false",
    ])


def test_cli_json_smoke_preserves_safe_flags() -> None:
    result = run_cli("--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert payload["phase"] == "CID.LOCAL_MEDIA_AGENT.FFMPEG.LOCAL.AVAILABILITY.PREFLIGHT.V1"
    assert payload["media_processing_performed"] is False
    assert payload["scanner_executed"] is False
    assert payload["real_media_used"] is False
    assert payload["database_write"] is False
    assert payload["saas_upload"] is False
    assert payload["network_call"] is False
    assert "ffmpeg" in payload
    assert "ffprobe" in payload


def test_cli_rejects_unexpected_media_argument() -> None:
    result = run_cli("/tmp/fake.mov")
    assert result.returncode != 0
    assert "unrecognized arguments" in result.stderr


def test_forbidden_imports_not_present() -> None:
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


def test_gate_does_not_open_blocked_work() -> None:
    assert_all_present(read(QA_DOC), [
        "It does not open real media processing.",
        "It does not open ffprobe media probing.",
        "It does not open ffmpeg media processing.",
        "It does not open audio extraction.",
        "It does not open sync.",
        "It does not open transcription.",
        "It does not open subtitles.",
        "It does not open timeline export.",
        "It does not open SaaS integration.",
        "It does not open database writes.",
        "It does not open installer creation.",
    ])


def test_next_safe_phase_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1",
        "PASS_FFMPEG_LOCAL_AVAILABILITY_PREFLIGHT_VALIDATED",
    ])
