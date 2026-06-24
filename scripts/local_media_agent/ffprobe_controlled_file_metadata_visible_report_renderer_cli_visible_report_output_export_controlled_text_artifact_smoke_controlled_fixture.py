from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


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
FUTURE_TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-v1-20260622"
)
NEXT_MICROPHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.QA.GATE.V1"
)

CONTROLLED_PAYLOAD_FIXTURE_PATH = (
    "tests/fixtures/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"
)
EXPECTED_VISIBLE_TEXT_FIXTURE_PATH = (
    "tests/fixtures/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt"
)
RENDERER_MODULE_PATH = (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer.py"
)
_RENDERER_FUNCTION_NAME = "render_controlled_ffprobe_metadata_visible_report"


@dataclass(frozen=True)
class ControlledTextArtifactSmokeFixtureResult:
    phase: str
    previous_phase: str
    functional_result: str
    controlled_payload_fixture_path: str
    expected_visible_text_fixture_path: str
    renderer_module_path: str
    actual_text_sha256: str
    expected_text_sha256: str
    text_matches: bool
    checked_line_count: int
    real_media_used: bool
    scanner_executed: bool
    ffprobe_executed: bool
    ffmpeg_executed: bool
    subprocess_executed: bool
    network_used: bool
    database_used: bool
    output_file_written: bool
    export_packaging_performed: bool
    artifact_generated: bool
    cli_executed: bool
    renderer_executed_as_process: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized if normalized.endswith("\n") else normalized + "\n"


def run_controlled_text_artifact_smoke_fixture() -> ControlledTextArtifactSmokeFixtureResult:
    repo_root = _repo_root()
    payload = _read_controlled_payload(repo_root / CONTROLLED_PAYLOAD_FIXTURE_PATH)
    expected_text = normalize_text(
        (repo_root / EXPECTED_VISIBLE_TEXT_FIXTURE_PATH).read_text(encoding="utf-8")
    )
    renderer = _load_renderer_function(repo_root / RENDERER_MODULE_PATH)
    actual_text = normalize_text(renderer(payload))

    return ControlledTextArtifactSmokeFixtureResult(
        phase=PHASE,
        previous_phase=PREVIOUS_PHASE,
        functional_result=FUNCTIONAL_RESULT,
        controlled_payload_fixture_path=CONTROLLED_PAYLOAD_FIXTURE_PATH,
        expected_visible_text_fixture_path=EXPECTED_VISIBLE_TEXT_FIXTURE_PATH,
        renderer_module_path=RENDERER_MODULE_PATH,
        actual_text_sha256=compute_text_sha256(actual_text),
        expected_text_sha256=compute_text_sha256(expected_text),
        text_matches=actual_text == expected_text,
        checked_line_count=len(expected_text.splitlines()),
        real_media_used=False,
        scanner_executed=False,
        ffprobe_executed=False,
        ffmpeg_executed=False,
        subprocess_executed=False,
        network_used=False,
        database_used=False,
        output_file_written=False,
        export_packaging_performed=False,
        artifact_generated=False,
        cli_executed=False,
        renderer_executed_as_process=False,
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_controlled_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_renderer_function(path: Path):
    module = _load_renderer_module(path)
    return getattr(module, _RENDERER_FUNCTION_NAME)


def _load_renderer_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("cid_local_media_agent_visible_report_renderer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load controlled visible report renderer module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
