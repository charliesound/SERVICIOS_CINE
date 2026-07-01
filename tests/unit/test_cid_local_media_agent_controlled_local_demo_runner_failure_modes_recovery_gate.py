from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_failure_modes_recovery_gate_v1.md"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED."
    "TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED."
    "CONTROLLED.LOCAL.DEMO.RUNNER.FAILURE.MODES.RECOVERY.GATE.V1"
)

RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_FAILURE_MODES_RECOVERY_GATE_V1_CLOSED"


EXPECTED_SHA = "277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f"
EXPECTED_ARTIFACT = "controlled_visible_report.controlled.txt"


def _doc() -> str:
    assert DOC_PATH.exists(), f"Missing documentation file: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_failure_modes_recovery_gate_declares_phase_and_result() -> None:
    doc = _doc()

    assert PHASE in doc
    assert RESULT in doc


def test_failure_modes_recovery_gate_preserves_controlled_artifact_invariants() -> None:
    doc = _doc()

    assert EXPECTED_ARTIFACT in doc
    assert EXPECTED_SHA in doc
    assert "stable byte count is `167`" in doc
    assert "deterministic evidence" in doc


def test_failure_modes_recovery_gate_defines_severity_levels_zero_to_five() -> None:
    doc = _doc()

    for level in range(0, 6):
        assert f"### Level {level}" in doc


def test_failure_modes_recovery_gate_defines_stop_and_recovery_protocols() -> None:
    doc = _doc()

    required = [
        "Stop the demo flow",
        "Allowed recovery",
        "Stop condition",
        "Decision tree",
        "resume only if the recovery returns to a known safe state",
        "operator must not improvise",
    ]

    for token in required:
        assert token in doc


def test_failure_modes_recovery_gate_covers_environment_runner_cleanup_and_repo_failures() -> None:
    doc = _doc()

    required = [
        "Virtual environment not active",
        "Command not found",
        "JSON cannot be parsed",
        "SHA256 does not match",
        "Byte count does not match `167`",
        "Default mode leaves an output directory unexpectedly",
        "Worktree is dirty",
        "Target tag already exists",
    ]

    for token in required:
        assert token in doc


def test_failure_modes_recovery_gate_blocks_scope_breaches() -> None:
    doc = _doc()

    forbidden_scope_tokens = [
        "Runtime file changes appear",
        "Packaging file changes appear",
        "Scanner file changes appear",
        "SaaS, database, installer, backend, or frontend files appear",
        "Real customer media appears in the flow",
    ]

    for token in forbidden_scope_tokens:
        assert token in doc


def test_failure_modes_recovery_gate_includes_evidence_policy() -> None:
    doc = _doc()

    required = [
        "Evidence policy",
        "The exact command that failed",
        "The terminal output",
        "whether the failure was recovered or the demo was stopped",
        "Customer media paths",
        "Secrets",
        "Environment files",
    ]

    for token in required:
        assert token in doc


def test_failure_modes_recovery_gate_includes_safe_client_facing_language() -> None:
    doc = _doc()

    required = [
        "How to explain a stop to a producer, school, or potential client",
        "I am stopping here because this is a controlled technical demo",
        "not to fake a product state",
        "Real media work is a later, explicit phase",
        "Productization remains separate from this controlled demo",
    ]

    for token in required:
        assert token in doc


def test_failure_modes_recovery_gate_defines_what_not_to_say() -> None:
    doc = _doc()

    required = [
        "What not to say",
        "This already processes a real production folder",
        "This is already a final installer",
        "This can be sold as a complete product today",
        "full sync, transcription, translation, and edit preparation",
    ]

    for token in required:
        assert token in doc


def test_failure_modes_recovery_gate_keeps_demo_limits_explicit() -> None:
    doc = _doc()

    limits = [
        "The demo is controlled",
        "The demo is local",
        "does not inspect real client media",
        "does not run real probe tooling",
        "does not run transcoding or decoding",
        "does not call SaaS services",
        "does not write into the repository",
        "must not overwrite existing output",
    ]

    for token in limits:
        assert token in doc


def test_failure_modes_recovery_gate_closure_criteria_are_complete() -> None:
    doc = _doc()

    required = [
        "Closure criteria",
        "failure-mode document exists",
        "QA test exists",
        "severity levels 0 through 5",
        "stop conditions",
        "recovery rules",
        "safe client-facing language",
        "what not to say",
        "previous demo narrative and operator runbook gates still pass",
        "WSL/repo guard passes",
        "PostgreSQL-only regression guard passes",
    ]

    for token in required:
        assert token in doc


def test_failure_modes_recovery_gate_does_not_claim_product_readiness() -> None:
    doc = _doc()

    forbidden_claims = [
        "customer-ready product",
        "final production release",
        "complete commercial product",
        "public demo approved",
    ]

    for claim in forbidden_claims:
        assert claim not in doc
