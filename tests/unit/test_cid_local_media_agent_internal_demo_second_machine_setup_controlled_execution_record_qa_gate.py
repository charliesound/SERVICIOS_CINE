from __future__ import annotations

from pathlib import Path


RECORD_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_record_qa_gate_v1.md")
RECORD_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_record_v1.md")
RECORD_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_record.py")
PLAN_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_qa_gate_v1.md")
PLAN_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_qa_gate.py")
PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_v1.md")
PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan.py")
AUTH_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate_v1.md")
AUTH_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate.py")
EXECUTION_READINESS_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate.py")
EXECUTION_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness.py")
SETUP_PLAN_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate.py")
SETUP_PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py")
SETUP_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py")
INTERNAL_DEMO_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path = RECORD_QA_GATE_DOC) -> str:
    return path.read_text(encoding="utf-8")


def _record_text() -> str:
    return RECORD_DOC.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_01_record_qa_gate_doc_exists_and_declares_phase_and_result() -> None:
    _assert_all_present(_text(), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.RECORD.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_RECORD_QA_GATE_PASS_INTERNAL_CHAIN_CLOSED",
    ])


def test_02_source_stable_state_is_declared() -> None:
    _assert_all_present(_text(), [
        "e73b2ef3dc19526b4db93945d554cb6dadccd950",
        "docs: add CID Local Media Agent controlled execution record",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-record-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_RECORD_PASS_READY_FOR_RECORD_QA_GATE",
    ])


def test_03_required_source_artifacts_exist() -> None:
    for path in [
        RECORD_DOC,
        RECORD_TEST,
        PLAN_QA_GATE_DOC,
        PLAN_QA_GATE_TEST,
        PLAN_DOC,
        PLAN_TEST,
        AUTH_GATE_DOC,
        AUTH_GATE_TEST,
        EXECUTION_READINESS_QA_GATE_TEST,
        EXECUTION_READINESS_TEST,
        SETUP_PLAN_QA_GATE_TEST,
        SETUP_PLAN_TEST,
        SETUP_READINESS_TEST,
        INTERNAL_DEMO_READINESS_TEST,
        CLI_FILE,
        RUNTIME_FILE,
    ]:
        assert path.exists()


def test_04_qa_gate_decision_does_not_open_client_or_real_media_use() -> None:
    _assert_all_present(_text(), [
        "PASS_INTERNAL_CONTROLLED_EXECUTION_CHAIN_CLOSED_FOR_RECORD",
        "It does not mean product installation is authorized.",
        "It does not mean client installation is authorized.",
        "It does not mean installer creation is authorized.",
        "It does not mean public demo readiness.",
        "It does not mean sales demo readiness.",
        "It does not mean production readiness.",
        "It does not mean real media processing is authorized.",
    ])


def test_05_record_completeness_criteria_are_declared() -> None:
    _assert_all_present(_text(), [
        "phase",
        "objective",
        "source stable state",
        "execution evidence source",
        "controlled execution result",
        "artifact summary",
        "boundary results",
        "report boundary evidence",
        "controlled execution interpretation",
        "explicit non-claims",
        "required preservation",
        "next safe phase",
        "validation evidence",
        "acceptance result",
    ])


def test_06_required_record_and_execution_results_are_declared() -> None:
    _assert_all_present(_text(), [
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_RECORD_PASS_READY_FOR_RECORD_QA_GATE",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PASS_READY_FOR_EXECUTION_RECORD",
    ])


def test_07_required_machine_evidence_is_declared() -> None:
    _assert_all_present(_text(), [
        "DESKTOP-72I1HEL",
        "harliesound",
        "/opt/SERVICIOS_CINE",
        "cc55d6e5f62d4f83f9288573197ac8fddeca338f",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1",
    ])


def test_08_required_controlled_artifact_evidence_is_declared() -> None:
    _assert_all_present(_text(), [
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/evidence/controlled_execution_evidence_v1.json",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output/05_reports/cid_local_media_agent_visible_report_v1.md",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json",
        "must not copy real media into the repository",
        "must not copy controlled fixture JSON into the repository as product data",
        "must not copy generated report markdown into the repository as product output",
        "only a controlled summary and boundary assertions",
    ])


def test_09_required_true_boundary_evidence_is_declared_and_present_in_record() -> None:
    required = [
        "internal_only: true",
        "project_owner_controlled_machine: true",
        "controlled_fixture_only: true",
    ]
    _assert_all_present(_text(), required)
    _assert_all_present(_record_text(), required)


def test_10_required_false_boundary_evidence_is_declared_and_present_in_record() -> None:
    required = [
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
    ]
    _assert_all_present(_text(), required)
    _assert_all_present(_record_text(), required)


def test_11_required_report_boundary_evidence_is_declared_and_present_in_record() -> None:
    required = [
        "Client-facing readiness: false.",
        "Scanner execution by this renderer: false.",
        "Media probing by this renderer: false.",
        "audio sync: not_generated",
        "transcription: not_generated",
        "subtitles: not_generated",
        "timeline exports: not_generated",
        "SaaS upload: not_generated",
        "database records: not_generated",
    ]
    _assert_all_present(_text(), required)
    _assert_all_present(_record_text(), required)


def test_12_interpretation_limits_are_declared() -> None:
    _assert_all_present(_text(), [
        "controlled visible report CLI can run",
        "controlled scanner-result fixture can be consumed",
        "controlled report can be generated",
        "controlled evidence can be recorded",
        "repository remains clean",
        "scanner execution on real media",
        "media probing on real files",
        "ffprobe integration on real files",
        "ffmpeg integration on real files",
        "audio synchronization",
        "transcription",
        "subtitle generation",
        "timeline export",
        "installer readiness",
        "client installation readiness",
        "public demo readiness",
        "sales demo readiness",
        "production readiness",
    ])


def test_13_explicit_non_claims_are_declared() -> None:
    _assert_all_present(_text(), [
        "commercial installation",
        "client installation",
        "installer creation",
        "package creation",
        "public demo readiness",
        "sales demo readiness",
        "production readiness",
        "real media processing",
        "client material processing",
        "productora deployment",
        "school deployment",
        "investor delivery",
        "SaaS integration",
        "database integration",
    ])


def test_14_chain_closure_does_not_open_blocked_work() -> None:
    _assert_all_present(_text(), [
        "closes only the internal controlled execution record chain",
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


def test_15_next_safe_phase_is_chain_summary_only() -> None:
    _assert_all_present(_text(), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.CHAIN.SUMMARY.V1",
        "That phase may summarize the internal controlled execution chain.",
        "It must not execute setup again.",
        "It must not install the product.",
        "It must not create an installer.",
        "It must not authorize client installation.",
        "It must not authorize public demo use.",
        "It must not authorize sales demo use.",
        "It must not use real media.",
    ])


def test_16_upstream_record_names_this_qa_gate_as_next_safe_phase() -> None:
    _assert_all_present(_record_text(), [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.RECORD.QA.GATE.V1",
        "That phase may validate this execution record.",
        "It must not execute setup again.",
        "It must not install the product.",
        "It must not create an installer.",
        "It must not authorize client installation.",
        "It must not authorize public demo use.",
        "It must not authorize sales demo use.",
        "It must not use real media.",
    ])


def test_17_record_qa_gate_does_not_claim_commercial_or_client_readiness() -> None:
    text = _text().lower()
    forbidden_claims = [
        "client-ready: true",
        "production-ready: true",
        "public-ready: true",
        "sales-ready: true",
        "installer-ready: true",
        "commercial-ready: true",
    ]
    for claim in forbidden_claims:
        assert claim not in text


def test_18_validation_evidence_is_declared() -> None:
    _assert_all_present(_text(), [
        "controlled execution record QA gate test passing",
        "controlled execution record test passing",
        "controlled execution plan QA gate test passing",
        "controlled execution plan test passing",
        "controlled execution authorization gate test passing",
        "second machine setup execution readiness QA gate test passing",
        "second machine setup execution readiness test passing",
        "second machine setup plan QA gate test passing",
        "second machine setup plan test passing",
        "second machine setup readiness test passing",
        "internal demo readiness test passing",
        "CLI test passing",
        "CLI implementation QA gate passing",
        "runtime generator test passing",
        "controlled runtime implementation QA gate passing",
        "supporting implemented runtime chain tests passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
    ])
