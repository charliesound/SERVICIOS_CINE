from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_internal_demo_checklist_summary_v1.md")


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def assert_all_present(content: str, items: list[str]) -> None:
    for item in items:
        assert item in content


def test_phase_and_acceptance_result() -> None:
    content = read_doc()
    assert_all_present(content, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.INTERNAL.DEMO.CHECKLIST.SUMMARY.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_INTERNAL_DEMO_CHECKLIST_SUMMARY_PASS_READY_FOR_QA_GATE",
    ])


def test_source_stable_state_is_declared() -> None:
    content = read_doc()
    assert_all_present(content, [
        "f904c847f0029f6da0d4199d0331b73ef6a0cf18",
        "test: add CID Local Media Agent controlled execution chain summary QA gate",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-chain-summary-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_CHAIN_SUMMARY_QA_GATE_PASS_CLOSED",
    ])


def test_demo_classification_blocks_external_claims() -> None:
    content = read_doc()
    assert_all_present(content, [
        "internal controlled demo checklist only",
        "It is not a public demo.",
        "It is not a sales demo.",
        "It is not a client-facing demo.",
        "It is not an installer checklist.",
        "It is not a production readiness checklist.",
        "It is not a real-media execution checklist.",
    ])


def test_allowed_internal_demo_items_are_limited() -> None:
    content = read_doc()
    assert_all_present(content, [
        "repository phase history",
        "closed chain summary",
        "controlled execution record",
        "QA gate evidence",
        "stable HEAD and tag evidence",
        "local-only product boundary",
        "controlled-fixture-only status",
        "visible report concept",
        "CLI help or dry explanation only",
        "non-real-media workflow explanation",
        "blocked capability map",
        "next safe phase options",
    ])


def test_prohibited_demo_items_remain_blocked() -> None:
    content = read_doc()
    assert_all_present(content, [
        "real production footage",
        "client material",
        "confidential script material",
        "real media folders",
        "scanner execution on real media",
        "media probe execution on real files",
        "ffprobe execution on real files",
        "ffmpeg execution on real files",
        "audio synchronization",
        "transcription output from real media",
        "subtitle generation from real media",
        "timeline export",
        "installer creation",
        "client installation",
        "public demo claim",
        "sales demo claim",
        "production readiness claim",
        "SaaS upload",
        "database writes",
    ])


def test_required_disclaimers_are_present() -> None:
    content = read_doc()
    assert_all_present(content, [
        "CID Local Media Agent is currently internal-only, controlled-fixture-only, local-only in product intent, not client-facing, not public, not sales-ready, not production-ready, not installer-ready, and not authorized for real media processing.",
        "INTERNAL CONTROLLED DEMO ONLY - NO REAL MEDIA - NO CLIENT MATERIAL - NO INSTALLER - NO PUBLIC OR SALES DEMO",
    ])


def test_safe_demo_sequence_stops_before_execution() -> None:
    content = read_doc()
    assert_all_present(content, [
        "Show repository stable state.",
        "Show closed chain summary.",
        "Show QA gate result.",
        "Show allowed boundary.",
        "Show prohibited capabilities.",
        "Explain next safe gate.",
        "Stop before any real media execution.",
    ])


def test_stop_conditions_are_explicit() -> None:
    content = read_doc()
    assert_all_present(content, [
        "selecting a real media folder",
        "scanning real footage",
        "probing real files",
        "running media processing tools on real files",
        "generating sync",
        "generating transcription",
        "generating subtitles",
        "exporting a timeline",
        "installing on another machine",
        "presenting to a client",
        "presenting publicly",
        "making sales claims",
        "writing to SaaS",
        "writing to a database",
    ])
