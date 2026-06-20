from __future__ import annotations

from pathlib import Path


RECORD_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_record_v1.md")
PLAN_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_qa_gate_v1.md")
PLAN_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_qa_gate.py")
PLAN_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan_v1.md")
PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_plan.py")
AUTH_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_controlled_execution_authorization_gate.py")
EXECUTION_READINESS_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness_qa_gate.py")
EXECUTION_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_execution_readiness.py")
SETUP_PLAN_QA_GATE_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan_qa_gate.py")
SETUP_PLAN_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_plan.py")
SETUP_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py")
INTERNAL_DEMO_READINESS_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py")
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
RUNTIME_FILE = Path("scripts/local_media_agent/visible_report_runtime_generator.py")


def _text(path: Path = RECORD_DOC) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_record_doc_exists_and_declares_phase_and_result() -> None:
    text = _text()
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.RECORD.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_RECORD_PASS_READY_FOR_RECORD_QA_GATE",
    ])


def test_source_stable_state_is_declared() -> None:
    text = _text()
    _assert_all_present(text, [
        "cc55d6e5f62d4f83f9288573197ac8fddeca338f",
        "test: add CID Local Media Agent controlled execution plan QA gate",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-plan-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PLAN_QA_GATE_PASS_READY_FOR_ONE_CONTROLLED_INTERNAL_EXECUTION",
    ])


def test_required_source_artifacts_exist() -> None:
    for path in [
        PLAN_QA_GATE_DOC,
        PLAN_QA_GATE_TEST,
        PLAN_DOC,
        PLAN_TEST,
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


def test_execution_evidence_source_paths_are_recorded() -> None:
    text = _text()
    _assert_all_present(text, [
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/evidence/controlled_execution_evidence_v1.json",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output/05_reports/cid_local_media_agent_visible_report_v1.md",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json",
        "/tmp/cid_local_media_agent_second_machine_controlled_execution_v1",
    ])


def test_controlled_execution_result_is_recorded() -> None:
    text = _text()
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PASS_READY_FOR_EXECUTION_RECORD",
        "DESKTOP-72I1HEL",
        "harliesound",
        "/opt/SERVICIOS_CINE",
        "Expected HEAD:",
        "Actual HEAD:",
    ])


def test_artifact_summary_is_recorded() -> None:
    text = _text()
    _assert_all_present(text, [
        "Controlled fixture exists:",
        "True",
        "Generated report exists:",
        "Generated report path:",
        "Controlled fixture path:",
        "Evidence path:",
    ])


def test_true_boundary_results_are_recorded() -> None:
    text = _text()
    _assert_all_present(text, [
        "internal_only: true",
        "project_owner_controlled_machine: true",
        "controlled_fixture_only: true",
    ])


def test_false_boundary_results_are_recorded() -> None:
    text = _text()
    _assert_all_present(text, [
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


def test_report_boundary_evidence_is_recorded() -> None:
    text = _text()
    _assert_all_present(text, [
        "Client-facing readiness: false.",
        "Scanner execution by this renderer: false.",
        "Media probing by this renderer: false.",
        "audio sync: not_generated",
        "transcription: not_generated",
        "subtitles: not_generated",
        "timeline exports: not_generated",
        "SaaS upload: not_generated",
        "database records: not_generated",
    ])


def test_controlled_execution_interpretation_is_constrained() -> None:
    text = _text()
    _assert_all_present(text, [
        "controlled visible report CLI can run against a controlled scanner-result fixture",
        "does not prove scanner execution on real media",
        "does not prove media probing on real files",
        "does not prove ffprobe integration on real files",
        "does not prove ffmpeg integration on real files",
        "does not prove audio synchronization",
        "does not prove transcription",
        "does not prove subtitle generation",
        "does not prove timeline export",
        "does not prove installer readiness",
        "does not prove client installation readiness",
        "does not prove public demo readiness",
        "does not prove sales demo readiness",
        "does not prove production readiness",
    ])


def test_explicit_non_claims_are_recorded() -> None:
    text = _text()
    _assert_all_present(text, [
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


def test_required_preservation_excludes_sensitive_or_product_artifacts() -> None:
    text = _text()
    _assert_all_present(text, [
        "The controlled evidence remains outside the repository",
        "The repository record intentionally stores only the controlled execution summary and boundary assertions.",
        "real media",
        "client media",
        "production footage",
        "confidential scripts",
        "environment secret files",
        "database files",
        "installer artifacts",
        "license activation files",
        "sales demo assets",
        "public demo assets",
    ])


def test_next_safe_phase_is_record_qa_gate_only() -> None:
    text = _text()
    _assert_all_present(text, [
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


def test_upstream_plan_qa_gate_names_execution_as_next_safe_phase() -> None:
    text = PLAN_QA_GATE_DOC.read_text(encoding="utf-8")
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.V1",
        "may execute one controlled internal second-machine setup execution using the validated plan",
        "It must remain internal-only.",
        "It must use controlled fixture input only.",
        "It must write an evidence record.",
        "It must stop on any stop condition.",
        "It must not install on a client machine.",
        "It must not create an installer.",
        "It must not authorize public demo use.",
        "It must not authorize sales demo use.",
        "It must not use real media.",
    ])


def test_record_does_not_claim_commercial_or_client_readiness() -> None:
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


def test_validation_evidence_is_declared() -> None:
    text = _text()
    _assert_all_present(text, [
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
