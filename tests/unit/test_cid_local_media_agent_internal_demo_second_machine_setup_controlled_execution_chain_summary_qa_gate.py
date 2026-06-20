from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_chain_summary_qa_gate_v1.md")
SUMMARY_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_chain_summary_v1.md")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, items: list[str]) -> None:
    for item in items:
        assert item in content


def test_qa_gate_phase_and_result() -> None:
    assert_all_present(read(QA_DOC), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.CHAIN.SUMMARY.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_CHAIN_SUMMARY_QA_GATE_PASS_CLOSED",
    ])


def test_source_stable_state() -> None:
    assert_all_present(read(QA_DOC), [
        "b467f7bc158c06b49335dab904df43628bbee712",
        "docs: add CID Local Media Agent controlled execution chain summary",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-chain-summary-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_CHAIN_SUMMARY_PASS_READY_FOR_QA_GATE",
    ])


def test_summary_file_exists_and_declares_source_result() -> None:
    assert SUMMARY_DOC.exists()
    assert_all_present(read(SUMMARY_DOC), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.CHAIN.SUMMARY.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_CHAIN_SUMMARY_PASS_READY_FOR_QA_GATE",
    ])


def test_required_summary_sections_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "closed internal controlled second-machine setup execution chain",
        "current stable HEAD",
        "closed phases",
        "controlled execution evidence",
        "validated internal fixture-only scope",
        "not validated real-media scope",
        "blocked boundary status",
        "product position",
        "next safe phase",
        "acceptance result",
    ])


def test_product_boundaries_are_preserved() -> None:
    assert_all_present(read(QA_DOC), [
        "internal-only",
        "controlled-fixture-only",
        "not client-facing",
        "not public",
        "not sales-ready",
        "not production-ready",
        "not installer-ready",
        "not authorized for real media",
    ])


def test_blocked_capabilities_are_preserved() -> None:
    assert_all_present(read(QA_DOC), [
        "real media",
        "production footage",
        "client material",
        "scanner on real media",
        "media probe on real files",
        "ffprobe on real files",
        "ffmpeg on real files",
        "audio sync",
        "transcription",
        "subtitles",
        "timeline export",
        "installer creation",
        "client installation",
        "public demo",
        "sales demo",
        "database writes",
        "SaaS upload",
    ])


def test_gate_does_not_open_blocked_work() -> None:
    assert_all_present(read(QA_DOC), [
        "It does not open real scanner execution.",
        "It does not open real media probing.",
        "It does not open ffprobe use on real files.",
        "It does not open ffmpeg use on real files.",
        "It does not open audio synchronization.",
        "It does not open transcription.",
        "It does not open subtitle generation.",
        "It does not open timeline export.",
        "It does not open SaaS integration.",
        "It does not open database writes.",
        "It does not open client-facing installation.",
        "It does not open installer creation.",
    ])


def test_validation_evidence_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "chain summary QA gate test passing",
        "chain summary test passing",
        "record QA gate test passing",
        "record test passing",
        "plan QA gate test passing",
        "plan test passing",
        "authorization gate test passing",
        "execution readiness QA gate test passing",
        "execution readiness test passing",
        "setup plan QA gate test passing",
        "setup plan test passing",
        "setup readiness test passing",
        "runtime support tests passing",
        "supporting runtime chain tests passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
    ])
