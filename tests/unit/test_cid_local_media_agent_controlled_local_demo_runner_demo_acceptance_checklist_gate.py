from pathlib import Path

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_demo_acceptance_checklist_gate_v1.md"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED."
    "TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED."
    "CONTROLLED.LOCAL.DEMO.RUNNER.DEMO.ACCEPTANCE.CHECKLIST.GATE.V1"
)

RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_ACCEPTANCE_CHECKLIST_GATE_V1_CLOSED"
ACCEPTED = "CONTROLLED_DEMO_ACCEPTED_FOR_LIMITED_STAKEHOLDER_CONVERSATION"
BLOCKED = "DEMO_ACCEPTANCE_BLOCKED"
SHA = "277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f"
ARTIFACT = "controlled_visible_report.controlled.txt"


def _doc() -> str:
    assert DOC_PATH.exists(), f"missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_gate_identity_and_closure_tokens_are_present() -> None:
    text = _doc()

    assert PHASE in text
    assert RESULT in text
    assert ACCEPTED in text
    assert BLOCKED in text


def test_gate_is_explicitly_documentation_and_qa_only() -> None:
    text = _doc()

    required = [
        "documentation and QA only",
        "does not modify runtime behavior",
        "command packaging",
        "scanner logic",
        "media processing",
        "ffprobe/FFmpeg integration",
        "SaaS/backend/frontend modules",
        "installer logic",
        "real material workflow",
    ]

    for item in required:
        assert item in text


def test_all_acceptance_groups_are_defined() -> None:
    text = _doc()

    for group in list("ABCDEFGHIJ"):
        assert f"Acceptance group {group}" in text


def test_repository_and_environment_readiness_is_required() -> None:
    text = _doc()

    required = [
        "/opt/SERVICIOS_CINE",
        "WSL Ubuntu",
        "virtual environment is active",
        "worktree is clean",
        "HEAD",
        "origin/main",
        "target tag",
        "No Windows path",
        "No nested repo copy",
    ]

    for item in required:
        assert item in text


def test_installed_command_readiness_is_required() -> None:
    text = _doc()

    required = [
        "/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-visible-report-write-enabled-export",
        "/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-controlled-local-demo-runner",
        "cid-local-media-agent-controlled-local-demo-runner --help",
        "cid-local-media-agent-controlled-local-demo-runner --result-json",
        "cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output",
    ]

    for item in required:
        assert item in text


def test_stable_evidence_values_are_required() -> None:
    text = _doc()

    assert ARTIFACT in text
    assert SHA in text
    assert "bytes: `167`" in text
    assert "hash proves the exact content is stable" in text
    assert "does not prove real media scanning" in text


def test_cleanup_readiness_is_required() -> None:
    text = _doc()

    required = [
        "Default run cleans temporary output automatically",
        "`--keep-output` preserves the controlled output",
        "manually cleaned afterwards",
        "repo remains free of generated output artifacts",
    ]

    for item in required:
        assert item in text


def test_operator_narrative_order_is_present() -> None:
    text = _doc()

    required = [
        "State the current demo boundary",
        "Show `--help`",
        "Run `--result-json`",
        "Explain the artifact name, SHA, and bytes",
        "Run `--result-json --keep-output`",
        "Explain cleanup",
        "Re-state current limits",
        "Invite feedback on product value",
    ]

    for item in required:
        assert item in text


def test_recovery_stop_conditions_are_present() -> None:
    text = _doc()

    required = [
        "command not found",
        "virtual environment not active",
        "JSON output missing or invalid",
        "artifact name, SHA, or byte count mismatch",
        "preserved output cannot be cleaned",
        "repo is dirty",
        "guard fails",
        "target tag already exists",
        "unexpected file enters the staged diff",
        "real-client-material demonstration",
    ]

    for item in required:
        assert item in text


def test_stakeholder_suitability_is_bounded() -> None:
    text = _doc()

    suitable = [
        "producer evaluating whether the product direction is useful",
        "film school evaluating teaching or workflow value",
        "postproduction supervisor evaluating future local workflow possibilities",
    ]
    unsuitable = [
        "public launch",
        "paid customer onboarding",
        "real project processing",
        "installer handoff",
        "unattended operation by a non-technical user",
    ]

    for item in suitable + unsuitable:
        assert item in text


def test_claim_discipline_is_explicit() -> None:
    text = _doc()

    approved = [
        "The demo command is installed in the controlled development environment",
        "The runner produces stable JSON evidence",
        "The controlled artifact has stable SHA and byte count",
    ]
    forbidden = [
        "The product is finished",
        "The product processes client footage today",
        "The scanner is real in this demo",
        "Real ffprobe or FFmpeg processing is demonstrated here",
        "The demo can be installed by a client now",
    ]

    for item in approved + forbidden:
        assert item in text


def test_evidence_chain_and_closure_validation_are_required() -> None:
    text = _doc()

    required = [
        "operator evidence pack gate",
        "demo narrative gate",
        "operator runbook gate",
        "failure modes and recovery gate",
        "this acceptance checklist gate",
        "the new QA test passes",
        "the previous failure modes gate test passes",
        "the previous operator runbook gate test passes",
        "the previous demo narrative gate test passes",
        "the previous operator evidence pack gate test passes",
        "PostgreSQL-only regression guard passes",
        "staged scope contains exactly this document and its QA test",
        "HEAD, origin/main, and the tag on the same commit",
    ]

    for item in required:
        assert item in text
