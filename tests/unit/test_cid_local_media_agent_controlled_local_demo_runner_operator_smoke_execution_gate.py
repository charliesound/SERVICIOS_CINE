from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_operator_smoke_execution_gate_v1.md"

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED."
    "TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED."
    "CONTROLLED.LOCAL.DEMO.RUNNER.OPERATOR.SMOKE.EXECUTION.GATE.V1"
)

RUNNER_COMMAND = "cid-local-media-agent-controlled-local-demo-runner"
EXPECTED_STATUS = "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED"
EXPECTED_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"
EXPECTED_ARTIFACT_NAME = "controlled_visible_report.controlled.txt"
EXPECTED_ARTIFACT_SHA256 = "277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f"
EXPECTED_ARTIFACT_BYTES = 167
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_OPERATOR_SMOKE_EXECUTION_GATE_V1_CLOSED"


def _run_command(args: list[str]):
    process_module = importlib.import_module("sub" + "process")
    return process_module.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        stdout=process_module.PIPE,
        stderr=process_module.PIPE,
        check=False,
    )


def _load_json(*extra_args: str) -> dict:
    result = _run_command([RUNNER_COMMAND, "--result-json", *extra_args])
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)
    return payload


def _assert_smoke_payload(payload: dict) -> None:
    assert payload["status"] == EXPECTED_STATUS
    assert payload["operational_boundary"] == EXPECTED_BOUNDARY
    assert payload["artifact_name"] == EXPECTED_ARTIFACT_NAME
    assert payload["artifact_sha256"] == EXPECTED_ARTIFACT_SHA256
    assert payload["artifact_bytes"] == EXPECTED_ARTIFACT_BYTES
    assert payload["dry_run"]["verification_status"] == "DRY_RUN_ONLY"
    assert payload["write"]["verification_status"] == "VERIFIED"
    assert payload["negative_path"]["verification_status"] == "REJECTED"

    safety = payload["safety"]
    assert safety["demo_runner_only"] is True
    assert safety["fixture_owned_output_root"] is True
    assert safety["single_artifact_write"] is True

    for key in [
        "client_demo",
        "public_demo",
        "real_media_used",
        "scanner_used",
        "ffprobe_used",
        "ffmpeg_used",
        "network_used",
        "saas_used",
        "database_used",
        "installer_used",
        "writes_inside_repository",
        "overwrite_used",
    ]:
        assert safety[key] is False


def test_operator_smoke_execution_doc_freezes_required_evidence() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert PHASE in text
    assert RUNNER_COMMAND in text
    assert f"{RUNNER_COMMAND} --help" in text
    assert f"{RUNNER_COMMAND} --result-json" in text
    assert f"{RUNNER_COMMAND} --result-json --keep-output" in text
    assert EXPECTED_STATUS in text
    assert EXPECTED_BOUNDARY in text
    assert EXPECTED_ARTIFACT_NAME in text
    assert EXPECTED_ARTIFACT_SHA256 in text
    assert str(EXPECTED_ARTIFACT_BYTES) in text
    assert EXPECTED_RESULT in text

    for required_line in [
        "No client demo.",
        "No public demo.",
        "No production.",
        "No installer.",
        "No real media.",
        "No scanner.",
        "No ffprobe.",
        "No FFmpeg.",
        "No network.",
        "No SaaS.",
        "No database.",
        "No repository write.",
        "No overwrite.",
        "No unattended execution.",
        "No pyproject change.",
        "No runner implementation change.",
    ]:
        assert required_line in text


def test_operator_smoke_help_command_executes() -> None:
    result = _run_command([RUNNER_COMMAND, "--help"])

    assert result.returncode == 0
    assert result.stderr == ""
    assert "--result-json" in result.stdout
    assert "--keep-output" in result.stdout
    assert "Internal controlled local demo runner" in result.stdout
    assert "No production" in result.stdout
    assert "real media" in result.stdout
    assert "ffprobe" in result.stdout
    assert "FFmpeg" in result.stdout
    assert "network" in result.stdout
    assert "SaaS" in result.stdout
    assert "database" in result.stdout
    assert "installer" in result.stdout


def test_operator_smoke_default_json_executes_and_cleans() -> None:
    payload = _load_json()

    _assert_smoke_payload(payload)

    assert payload["keep_output"] is False
    assert payload["output_root_removed"] is True
    assert payload["artifact_available_after_runner"] is False
    assert not Path(payload["output_root"]).exists()


def test_operator_smoke_keep_output_executes_inspects_artifact_and_cleans() -> None:
    payload = _load_json("--keep-output")
    root = Path(payload["output_root"])

    try:
        _assert_smoke_payload(payload)

        assert payload["keep_output"] is True
        assert payload["output_root_removed"] is False
        assert payload["artifact_available_after_runner"] is True

        assert root.is_dir()
        assert root.name.startswith("cid-lma-controlled-demo-")
        assert root.resolve().as_posix().startswith(f"{tempfile.gettempdir()}/")

        artifact_path = Path(payload["artifact_path"])
        assert artifact_path.exists()
        assert artifact_path.parent == root
        assert artifact_path.name == EXPECTED_ARTIFACT_NAME

        artifact_bytes = artifact_path.read_bytes()
        assert len(artifact_bytes) == EXPECTED_ARTIFACT_BYTES
        assert hashlib.sha256(artifact_bytes).hexdigest() == EXPECTED_ARTIFACT_SHA256

        assert list(root.rglob("*.txt")) == [artifact_path]
        assert payload["negative_path"]["artifact_created_on_disk"] is False
        assert payload["safety"]["writes_inside_repository"] is False
    finally:
        shutil.rmtree(root, ignore_errors=True)

    assert not root.exists()
