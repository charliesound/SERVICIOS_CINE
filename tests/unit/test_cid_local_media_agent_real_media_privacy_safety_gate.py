from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PRIVACY_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_media_privacy_safety_gate_v1.md"
)
SCOPE_CONTRACT_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_test_scope_contract_v1.md"
)
SCOPE_QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md"
)

SYNTHETIC_CLI = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_cli.py"
SYNTHETIC_PREFLIGHT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_preflight_check.py"
SYNTHETIC_RENDERER = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts" / "cid_media_agent_scan.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_privacy_safety_gate_declares_phase_baseline_and_decision() -> None:
    text = _read(PRIVACY_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.MEDIA.PRIVACY.SAFETY.GATE.V1" in text
    assert "Stable HEAD before this phase: `b878466`." in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.QA.GATE.V1" in text
    assert "This phase is documentation/test-only." in text
    assert "REAL_MEDIA_PRIVACY_SAFETY_GATE_READY_FOR_INPUT_FOLDER_CONTRACT_WITH_RESTRICTIONS" in text


def test_privacy_safety_gate_blocks_real_execution_and_runtime_changes() -> None:
    text = _read(PRIVACY_DOC)

    required = [
        "It does not execute real media",
        "does not call ffprobe/ffmpeg on real files",
        "does not implement real preflight",
        "does not implement scanner integration",
        "does not generate a real report",
        "does not modify runtime code",
    ]

    for item in required:
        assert item in text


def test_privacy_safety_gate_references_previous_scope_contracts() -> None:
    text = _read(PRIVACY_DOC)

    assert "docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md" in text
    assert SCOPE_CONTRACT_DOC.exists()
    assert SCOPE_QA_DOC.exists()


def test_privacy_safety_gate_defines_private_production_asset_position() -> None:
    text = _read(PRIVACY_DOC)

    required = [
        "CID Local Media Agent must treat real audiovisual files as private production assets.",
        "media files remain on the local disk;",
        "media files are not uploaded;",
        "media files are not sent to cloud services;",
        "media files are not sent to external APIs;",
        "media files are not copied outside the selected output area;",
        "media files are not modified, renamed, moved, deleted or transcoded;",
        "full private paths are not exposed in user-facing reports by default;",
        "client material remains excluded until a later explicit client authorization gate exists.",
    ]

    for item in required:
        assert item in text


def test_privacy_safety_gate_requires_local_only_manual_input_and_output() -> None:
    text = _read(PRIVACY_DOC)

    required = [
        "manually selected local input folder;",
        "manually selected local output folder;",
        "output folder separated from the input folder unless a later explicit safe exception exists;",
        "no automatic recursive scan of a whole drive;",
        "no hidden upload path;",
        "no external network dependency;",
        "no destructive filesystem operation;",
        "human review before marking any real test result usable.",
    ]

    for item in required:
        assert item in text


def test_privacy_safety_gate_blocks_sensitive_telemetry_and_logs() -> None:
    text = _read(PRIVACY_DOC)

    required = [
        "no telemetry containing media names, full paths, client names or project names;",
        "no log line containing sensitive full local paths by default;",
        "logs may record phase, status, counts and generic error codes;",
        "logs must not contain raw private media content;",
        "logs must not contain full private paths by default;",
        "logs must not contain client names or project names by default;",
        "errors must fail closed when privacy cannot be guaranteed;",
        "no analytics or telemetry may be introduced in the first real test path.",
    ]

    for item in required:
        assert item in text


def test_privacy_safety_gate_defines_report_privacy_requirements() -> None:
    text = _read(PRIVACY_DOC)

    required = [
        "Any future real report contract must default to privacy-preserving output:",
        "show file basenames only when needed;",
        "avoid full absolute paths in user-facing reports;",
        "avoid user home directory exposure;",
        "avoid client, production or project identifiers unless explicitly authorized;",
        "avoid embedding private source media;",
        "avoid thumbnails, waveform previews or frame captures unless a later explicit visual-output gate exists;",
        "clearly mark reports as internal test output until reviewed by a human.",
    ]

    for item in required:
        assert item in text


def test_privacy_safety_gate_requires_future_gates_before_real_execution() -> None:
    text = _read(PRIVACY_DOC)

    required_gates = [
        "CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1",
    ]

    for gate in required_gates:
        assert gate in text


def test_privacy_safety_gate_explicitly_blocks_current_phase_actions() -> None:
    text = _read(PRIVACY_DOC)

    blocked = [
        "real media execution;",
        "ffprobe or ffmpeg execution on real files;",
        "real preflight implementation;",
        "scanner integration;",
        "real report generation;",
        "thumbnail, waveform or frame extraction;",
        "sync;",
        "transcription;",
        "translation;",
        "subtitle generation;",
        "NLE export;",
        "runtime implementation;",
        "packaging implementation;",
        "installable entry point;",
        "shell launcher;",
        "desktop app;",
        "licensing;",
        "client delivery;",
        "SaaS/backend/frontend/database/Docker/Alembic work;",
        "Stripe, AI Jobs, credits or ledger work.",
    ]

    for item in blocked:
        assert item in text


def test_privacy_safety_gate_does_not_authorize_real_execution_by_language() -> None:
    text = _read(PRIVACY_DOC)

    assert "This privacy safety gate does not authorize real execution." in text
    assert "No real media execution is authorized by this privacy safety gate." in text
    assert "A future phase may define the real input-folder contract." in text


def test_previous_scope_contracts_still_block_real_execution() -> None:
    scope_text = _read(SCOPE_CONTRACT_DOC)
    qa_text = _read(SCOPE_QA_DOC)

    required_scope_items = [
        "No real media execution is authorized by this document.",
        "client material;",
        "upload;",
        "cloud processing;",
        "external API calls;",
        "read-only inspection as the default safety posture.",
    ]

    for item in required_scope_items:
        assert item in scope_text

    required_qa_items = [
        "No real media execution is authorized by this QA gate.",
        "real preflight implementation;",
        "scanner integration;",
        "client delivery;",
        "REAL_TEST_SCOPE_CONTRACT_QA_GATE_READY_FOR_PRIVACY_SAFETY_GATE_WITH_RESTRICTIONS",
    ]

    for item in required_qa_items:
        assert item in qa_text


def test_runtime_sources_are_not_modified_for_privacy_safety_gate() -> None:
    sources = [
        _read(SYNTHETIC_CLI),
        _read(SYNTHETIC_PREFLIGHT),
        _read(SYNTHETIC_RENDERER),
        _read(SCANNER_SCRIPT),
    ]

    forbidden_runtime_terms = [
        "REAL.MEDIA.PRIVACY.SAFETY.GATE",
        "REAL_MEDIA_PRIVACY_SAFETY_GATE_READY",
        "private production assets",
        "no hidden upload path",
        "real media execution",
        "client delivery",
    ]

    for source in sources:
        for term in forbidden_runtime_terms:
            assert term not in source

    cli_source = sources[0]
    renderer_source = sources[2]
    scanner_source = sources[3]

    assert "cid_media_agent_scan" not in cli_source
    assert "--preflight" not in renderer_source
    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source
    assert "PREFLIGHT_PASS" not in scanner_source
    assert "PREFLIGHT_FAIL" not in scanner_source
