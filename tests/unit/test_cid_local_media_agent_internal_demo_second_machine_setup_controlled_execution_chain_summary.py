from pathlib import Path

SUMMARY = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_chain_summary_v1.md")


def text() -> str:
    return SUMMARY.read_text(encoding="utf-8")


def assert_all_present(content: str, items: list[str]) -> None:
    for item in items:
        assert item in content


def test_summary_phase_and_result() -> None:
    assert_all_present(text(), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.CHAIN.SUMMARY.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_CHAIN_SUMMARY_PASS_READY_FOR_QA_GATE",
    ])


def test_stable_state_is_declared() -> None:
    assert_all_present(text(), [
        "f2f42746cfa16bd590bb4e7fecae76266325ca46",
        "test: add CID Local Media Agent controlled execution record QA gate",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-record-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_RECORD_QA_GATE_PASS_INTERNAL_CHAIN_CLOSED",
    ])


def test_closed_chain_phases_are_listed() -> None:
    assert_all_present(text(), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.READINESS.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.AUTHORIZATION.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.RECORD.V1",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.RECORD.QA.GATE.V1",
    ])


def test_controlled_execution_artifacts_are_summarized() -> None:
    assert_all_present(text(), [
        "DESKTOP-72I1HEL",
        "harliesound",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output/05_reports/cid_local_media_agent_visible_report_v1.md",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/evidence/controlled_execution_evidence_v1.json",
    ])


def test_validated_scope_is_internal_fixture_only() -> None:
    assert_all_present(text(), [
        "internal-only controlled second-machine setup planning",
        "controlled execution authorization",
        "one controlled internal execution using controlled fixture input only",
        "visible report generation from controlled scanner-result fixture",
        "controlled evidence JSON creation outside the repository",
        "source-controlled execution record",
        "source-controlled execution record QA gate",
        "repository cleanliness after controlled execution",
    ])


def test_not_validated_scope_is_explicit() -> None:
    assert_all_present(text(), [
        "scanner execution on real media",
        "media probing on real files",
        "ffprobe use on real files",
        "ffmpeg use on real files",
        "audio synchronization",
        "transcription",
        "subtitle generation",
        "translation",
        "timeline export",
        "DaVinci Resolve export",
        "Avid export",
        "SaaS integration",
        "database writes",
        "installer creation",
        "license activation",
        "client installation",
        "public demo",
        "sales demo",
        "paid pilot",
        "production readiness",
    ])


def test_boundary_status_remains_blocked() -> None:
    assert_all_present(text(), [
        "real_media_used: false",
        "production_footage_used: false",
        "client_material_used: false",
        "confidential_script_material_used: false",
        "scanner_on_real_media: false",
        "media_probe_on_real_media: false",
        "ffprobe_on_real_media: false",
        "ffmpeg_on_real_media: false",
        "audio_sync_generated: false",
        "transcription_generated: false",
        "subtitles_generated: false",
        "timeline_export_generated: false",
        "installer_created: false",
        "client_installation: false",
        "public_demo: false",
        "sales_demo: false",
        "database_write: false",
        "saas_upload: false",
    ])


def test_product_position_and_next_safe_phase_are_declared() -> None:
    assert_all_present(text(), [
        "CONTROLLED_INTERNAL_DEMO_CHAIN_CLOSED_FIXTURE_ONLY",
        "not client-facing",
        "not public",
        "not sales-ready",
        "not production-ready",
        "not installer-ready",
        "not authorized for real media",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.CHAIN.SUMMARY.QA.GATE.V1",
        "It must not execute setup again.",
        "It must not install the product.",
        "It must not create an installer.",
        "It must not use real media.",
    ])
