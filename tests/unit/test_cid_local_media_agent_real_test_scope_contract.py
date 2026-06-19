from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CONTRACT_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_test_scope_contract_v1.md"
)

SYNTHETIC_CLI = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_cli.py"
SYNTHETIC_PREFLIGHT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_preflight_check.py"
SYNTHETIC_RENDERER = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts" / "cid_media_agent_scan.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_real_test_scope_contract_declares_phase_baseline_and_decision() -> None:
    text = _read(CONTRACT_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.V1" in text
    assert "Stable HEAD before this phase: `ac9e168`." in text
    assert (
        "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT."
        "PREFLIGHT.PACKAGING.READINESS.QA.GATE.V1"
    ) in text
    assert "This phase is documentation/test-only." in text
    assert "REAL_TEST_SCOPE_CONTRACT_READY_FOR_QA_GATE_WITH_RESTRICTIONS" in text


def test_real_test_scope_contract_blocks_real_execution_and_runtime_changes() -> None:
    text = _read(CONTRACT_DOC)

    required = [
        "It does not execute real media",
        "does not call ffprobe/ffmpeg on real files",
        "does not implement a real scanner workflow",
        "does not generate a real report",
        "does not modify runtime code",
    ]

    for item in required:
        assert item in text


def test_real_test_scope_contract_defines_internal_laboratory_test_only() -> None:
    text = _read(CONTRACT_DOC)

    required = [
        "The first real test must be an internal laboratory test only.",
        "small local folder of real audiovisual files",
        "controlled internal environment",
        "without uploading, modifying, deleting, moving, transcoding or exposing the material",
    ]

    for item in required:
        assert item in text


def test_real_test_scope_contract_allows_only_safe_future_material() -> None:
    text = _read(CONTRACT_DOC)

    allowed = [
        "material owned or explicitly authorized by the developer;",
        "a small local-only folder created specifically for the test;",
        "copied test media, never original camera masters;",
        "non-client material unless a later explicit client authorization gate exists;",
        "a manually selected input folder;",
        "a manually selected output folder;",
        "read-only inspection as the default safety posture.",
    ]

    for item in allowed:
        assert item in text


def test_real_test_scope_contract_excludes_client_and_destructive_workflows() -> None:
    text = _read(CONTRACT_DOC)

    exclusions = [
        "client material;",
        "confidential productions;",
        "original camera masters;",
        "destructive operations;",
        "moving files;",
        "deleting files;",
        "renaming files;",
        "transcoding;",
        "upload;",
        "cloud processing;",
        "external API calls;",
    ]

    for item in exclusions:
        assert item in text


def test_real_test_scope_contract_excludes_postproduction_and_packaging_workflows() -> None:
    text = _read(CONTRACT_DOC)

    exclusions = [
        "sync;",
        "transcription;",
        "translation;",
        "subtitle generation;",
        "DaVinci Resolve export;",
        "Avid export;",
        "packaging;",
        "installable entry point;",
        "shell launcher;",
        "desktop app;",
        "licensing;",
    ]

    for item in exclusions:
        assert item in text


def test_real_test_scope_contract_excludes_saas_database_and_billing_workflows() -> None:
    text = _read(CONTRACT_DOC)

    exclusions = [
        "SaaS/backend/frontend/database/Docker/Alembic work;",
        "Stripe, AI Jobs, credits or ledger work.",
    ]

    for item in exclusions:
        assert item in text


def test_real_test_scope_contract_sets_minimum_future_success_criteria() -> None:
    text = _read(CONTRACT_DOC)

    criteria = [
        "input folder is local;",
        "output folder is local;",
        "no upload path exists;",
        "no external network dependency is required;",
        "original media files are not modified;",
        "no files are moved, deleted or renamed;",
        "sensitive full paths are not exposed in user-facing reports by default;",
        "human review is mandatory before considering the result usable.",
    ]

    for item in criteria:
        assert item in text


def test_real_test_scope_contract_requires_next_gates_before_real_execution() -> None:
    text = _read(CONTRACT_DOC)

    required_gates = [
        "CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.MEDIA.PRIVACY.SAFETY.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1",
    ]

    for gate in required_gates:
        assert gate in text


def test_real_test_scope_contract_explicitly_blocks_current_phase_actions() -> None:
    text = _read(CONTRACT_DOC)

    blocked = [
        "real media execution;",
        "ffprobe or ffmpeg execution on real files;",
        "scanner integration;",
        "real report generation;",
        "runtime implementation;",
        "packaging implementation;",
        "installable entry point;",
        "shell launcher;",
        "client delivery;",
        "SaaS/backend/frontend/database/Docker/Alembic work;",
        "Stripe, AI Jobs, credits or ledger work.",
    ]

    for item in blocked:
        assert item in text


def test_real_test_scope_contract_does_not_authorize_real_execution_by_language() -> None:
    text = _read(CONTRACT_DOC)

    assert "No real media execution is authorized by this document." in text
    assert "A future phase may audit this scope contract." in text
    assert "real execution phase may be considered only if future gates confirm" in text


def test_runtime_sources_are_not_modified_for_real_test_scope_contract() -> None:
    sources = [
        _read(SYNTHETIC_CLI),
        _read(SYNTHETIC_PREFLIGHT),
        _read(SYNTHETIC_RENDERER),
        _read(SCANNER_SCRIPT),
    ]

    forbidden_runtime_terms = [
        "REAL.TEST.SCOPE.CONTRACT",
        "REAL_TEST_SCOPE_CONTRACT_READY_FOR_QA_GATE",
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
