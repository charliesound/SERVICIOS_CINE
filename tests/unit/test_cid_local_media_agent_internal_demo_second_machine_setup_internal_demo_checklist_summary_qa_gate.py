from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_internal_demo_checklist_summary_qa_gate_v1.md")
SUMMARY_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_internal_demo_checklist_summary_v1.md")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, items: list[str]) -> None:
    for item in items:
        assert item in content


def test_phase_and_acceptance_result() -> None:
    assert_all_present(read(QA_DOC), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.INTERNAL.DEMO.CHECKLIST.SUMMARY.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_INTERNAL_DEMO_CHECKLIST_SUMMARY_QA_GATE_PASS_CLOSED",
    ])


def test_source_stable_state() -> None:
    assert_all_present(read(QA_DOC), [
        "1e6b018b15e072d8cd1a1195b12fd9eb9ea609a1",
        "docs: add CID Local Media Agent internal demo checklist summary",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-internal-demo-checklist-summary-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_INTERNAL_DEMO_CHECKLIST_SUMMARY_PASS_READY_FOR_QA_GATE",
    ])


def test_summary_file_exists_and_declares_source_result() -> None:
    assert SUMMARY_DOC.exists()
    assert_all_present(read(SUMMARY_DOC), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.INTERNAL.DEMO.CHECKLIST.SUMMARY.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_INTERNAL_DEMO_CHECKLIST_SUMMARY_PASS_READY_FOR_QA_GATE",
    ])


def test_required_checklist_scope_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "internal controlled demo classification",
        "allowed internal demo items",
        "allowed narrative",
        "prohibited demo items",
        "required verbal disclaimer",
        "required visual disclaimer",
        "safe demo sequence",
        "stop conditions",
        "acceptance result",
        "next safe phase",
    ])


def test_allowed_items_are_limited_to_internal_demo() -> None:
    assert_all_present(read(QA_DOC), [
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


def test_blocked_items_are_preserved() -> None:
    assert_all_present(read(QA_DOC), [
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


def test_required_disclaimers_are_preserved() -> None:
    assert_all_present(read(QA_DOC), [
        "CID Local Media Agent is currently internal-only, controlled-fixture-only, local-only in product intent, not client-facing, not public, not sales-ready, not production-ready, not installer-ready, and not authorized for real media processing.",
        "INTERNAL CONTROLLED DEMO ONLY - NO REAL MEDIA - NO CLIENT MATERIAL - NO INSTALLER - NO PUBLIC OR SALES DEMO",
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
        "It does not open installer creation.",
        "It does not open client-facing installation.",
        "It does not open public demo use.",
        "It does not open sales demo use.",
    ])


def test_validation_evidence_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "internal demo checklist summary QA gate test passing",
        "internal demo checklist summary test passing",
        "chain summary QA gate test passing",
        "chain summary test passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
        "no protected files staged",
    ])
