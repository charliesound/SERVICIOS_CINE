from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_second_fixture_scenario_qa_gate_v1.md")
SOURCE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_second_fixture_scenario_v1.md")
SOURCE_TEST = Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_second_fixture_scenario.py")
RUNTIME_SCRIPT = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py")
BASE_TEST = Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight.py")
BASE_QA_TEST = Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_qa_gate.py")

QA_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.QA.GATE.V1"
SOURCE_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.V1"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_qa_gate_phase_and_result_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        QA_PHASE,
        "PASS_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_SECOND_FIXTURE_SCENARIO_VALIDATED",
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_SECOND_FIXTURE_SCENARIO_QA_GATE_PASS_CLOSED",
    ])


def test_source_stable_state_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "d0d9b44d2c8c6dfd6d9f1267f12593e1ad382637",
        "test: add CID Local Media Agent ffprobe second fixture scenario",
        "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-preflight-second-fixture-scenario-v1-20260620",
        SOURCE_PHASE,
    ])


def test_required_source_files_exist() -> None:
    for path in [
        QA_DOC,
        SOURCE_DOC,
        SOURCE_TEST,
        RUNTIME_SCRIPT,
        BASE_TEST,
        BASE_QA_TEST,
    ]:
        assert path.exists(), path


def test_required_validated_behavior_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "controlled fixture path only",
        "mocked successful ffprobe metadata response",
        "preservation of `metadata.format`",
        "preservation of `metadata.streams`",
        "at least one video stream in mocked metadata",
        "at least one audio stream in mocked metadata",
        "`ffprobe_command_kind` equals `metadata_json`",
        "`input_path_redacted` is filename only",
        "full input path is not leaked",
        "uncontrolled paths remain rejected",
        "missing `--controlled-fixture` remains rejected",
        "all blocked execution flags remain false",
        "no forbidden imports",
        "no ffmpeg execution/reference",
        "runtime script remains unchanged",
    ])


def test_required_safe_flags_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
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


def test_required_boundaries_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "real rodaje material",
        "real media files",
        "arbitrary folders",
        "scanner execution",
        "ffmpeg media processing",
        "audio extraction",
        "sync generation",
        "transcription generation",
        "subtitle generation",
        "timeline export",
        "SaaS upload",
        "database writes",
        "installer creation",
        "client-facing use",
        "public demo",
        "sales demo",
        "production use",
    ])


def test_source_second_fixture_scenario_declares_expected_result_and_next_phase() -> None:
    assert_all_present(read(SOURCE_DOC), [
        SOURCE_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_SECOND_FIXTURE_SCENARIO_PASS_READY_FOR_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.QA.GATE.V1",
    ])


def test_second_fixture_test_mentions_expected_metadata_shape() -> None:
    content = read(SOURCE_TEST)
    assert_all_present(content, [
        "format",
        "streams",
        "video",
        "audio",
        "h264",
        "metadata_json",
        "input_path_redacted",
    ])


def test_forbidden_imports_are_not_present_in_second_fixture_test() -> None:
    content = read(SOURCE_TEST)
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


def test_no_ffmpeg_execution_reference_in_second_fixture_test() -> None:
    content = read(SOURCE_TEST)
    forbidden = [
        '"ffmpeg"',
        "'ffmpeg'",
        "ffmpeg -i",
        "ffmpeg -y",
        "ffmpeg -nostdin",
    ]
    for item in forbidden:
        assert item not in content


def test_validation_evidence_and_next_safe_phase_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "second fixture scenario QA gate test passing",
        "second fixture scenario test passing",
        "ffprobe controlled metadata preflight test passing",
        "ffprobe controlled metadata preflight QA gate test passing",
        "ffmpeg availability preflight QA gate test passing",
        "runtime script not staged",
        "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.V1",
    ])
