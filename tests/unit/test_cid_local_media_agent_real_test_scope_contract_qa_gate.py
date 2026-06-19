from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md"
)
CONTRACT_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_test_scope_contract_v1.md"
)
CONTRACT_TEST = REPO_ROOT / "tests" / "unit" / (
    "test_cid_local_media_agent_real_test_scope_contract.py"
)

SYNTHETIC_CLI = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_cli.py"
SYNTHETIC_PREFLIGHT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_preflight_check.py"
SYNTHETIC_RENDERER = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts" / "cid_media_agent_scan.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_real_test_scope_qa_gate_declares_phase_baseline_and_decision() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.QA.GATE.V1" in text
    assert "Stable HEAD before this phase: `8a697c0`." in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.V1" in text
    assert "This phase is documentation/test-only." in text
    assert "REAL_TEST_SCOPE_CONTRACT_QA_GATE_READY_FOR_PRIVACY_SAFETY_GATE_WITH_RESTRICTIONS" in text


def test_real_test_scope_qa_gate_blocks_real_execution_and_runtime_changes() -> None:
    text = _read(QA_DOC)

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


def test_real_test_scope_qa_gate_references_target_contract_and_test() -> None:
    text = _read(QA_DOC)

    assert "docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_real_test_scope_contract.py" in text
    assert CONTRACT_DOC.exists()
    assert CONTRACT_TEST.exists()


def test_real_test_scope_qa_gate_allowed_files_are_limited() -> None:
    text = _read(QA_DOC)

    assert "Allowed files for this phase:" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_real_test_scope_contract_qa_gate.py" in text
    assert "Runtime files may be audited by tests but must not be modified." in text


def test_real_test_scope_qa_gate_audits_required_contract_assertions() -> None:
    text = _read(QA_DOC)

    required = [
        "declares the correct phase and stable baseline;",
        "references the completed packaging readiness QA gate;",
        "declares documentation/test-only status;",
        "blocks real media execution in the current phase;",
        "blocks ffprobe/ffmpeg execution on real files;",
        "blocks scanner integration;",
        "blocks real report generation;",
        "blocks runtime implementation;",
        "defines the first real test as internal laboratory only;",
        "allows only owned or explicitly authorized material;",
        "requires copied test media, never original camera masters;",
        "excludes client material unless a later explicit client authorization gate exists;",
        "keeps input and output folders manually selected and local;",
        "sets read-only inspection as the default safety posture;",
        "requires human review before considering the result usable.",
    ]

    for item in required:
        assert item in text


def test_real_test_scope_qa_gate_audits_required_exclusions() -> None:
    text = _read(QA_DOC)

    exclusions = [
        "client material;",
        "confidential productions;",
        "original camera masters;",
        "destructive operations;",
        "moving, deleting or renaming files;",
        "transcoding;",
        "upload;",
        "cloud processing;",
        "external API calls;",
        "sync;",
        "transcription;",
        "translation;",
        "subtitle generation;",
        "NLE export;",
        "packaging;",
        "installable entry point;",
        "shell launcher;",
        "SaaS/backend/frontend/database/Docker/Alembic work;",
        "Stripe, AI Jobs, credits or ledger work.",
    ]

    for item in exclusions:
        assert item in text


def test_real_test_scope_qa_gate_requires_next_gates_before_real_execution() -> None:
    text = _read(QA_DOC)

    required_gates = [
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


def test_target_contract_still_blocks_real_execution_and_client_material() -> None:
    text = _read(CONTRACT_DOC)

    required = [
        "No real media execution is authorized by this document.",
        "It does not execute real media",
        "does not call ffprobe/ffmpeg on real files",
        "does not implement a real scanner workflow",
        "does not generate a real report",
        "does not modify runtime code",
        "client material;",
        "confidential productions;",
        "original camera masters;",
        "upload;",
        "cloud processing;",
        "external API calls;",
    ]

    for item in required:
        assert item in text


def test_target_contract_still_defines_internal_local_only_laboratory_scope() -> None:
    text = _read(CONTRACT_DOC)

    required = [
        "The first real test must be an internal laboratory test only.",
        "material owned or explicitly authorized by the developer;",
        "a small local-only folder created specifically for the test;",
        "copied test media, never original camera masters;",
        "a manually selected input folder;",
        "a manually selected output folder;",
        "read-only inspection as the default safety posture.",
        "input folder is local;",
        "output folder is local;",
        "no upload path exists;",
        "no external network dependency is required;",
        "original media files are not modified;",
        "human review is mandatory before considering the result usable.",
    ]

    for item in required:
        assert item in text


def test_target_contract_test_covers_required_contract_assertions() -> None:
    text = _read(CONTRACT_TEST)

    required_tests = [
        "test_real_test_scope_contract_declares_phase_baseline_and_decision",
        "test_real_test_scope_contract_blocks_real_execution_and_runtime_changes",
        "test_real_test_scope_contract_defines_internal_laboratory_test_only",
        "test_real_test_scope_contract_allows_only_safe_future_material",
        "test_real_test_scope_contract_excludes_client_and_destructive_workflows",
        "test_real_test_scope_contract_requires_next_gates_before_real_execution",
        "test_real_test_scope_contract_explicitly_blocks_current_phase_actions",
        "test_runtime_sources_are_not_modified_for_real_test_scope_contract",
    ]

    for name in required_tests:
        assert name in text


def test_real_test_scope_qa_gate_explicitly_blocks_current_phase_actions() -> None:
    text = _read(QA_DOC)

    blocked = [
        "real media execution;",
        "ffprobe or ffmpeg execution on real files;",
        "real preflight implementation;",
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


def test_runtime_sources_are_not_modified_for_real_test_scope_qa_gate() -> None:
    sources = [
        _read(SYNTHETIC_CLI),
        _read(SYNTHETIC_PREFLIGHT),
        _read(SYNTHETIC_RENDERER),
        _read(SCANNER_SCRIPT),
    ]

    forbidden_runtime_terms = [
        "REAL.TEST.SCOPE.CONTRACT.QA.GATE",
        "REAL_TEST_SCOPE_CONTRACT_QA_GATE_READY",
        "privacy safety gate",
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
