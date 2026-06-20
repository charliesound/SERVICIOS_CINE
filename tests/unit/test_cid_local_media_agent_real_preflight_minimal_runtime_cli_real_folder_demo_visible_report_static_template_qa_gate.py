from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_static_template_qa_gate_v1.md")
STATIC_TEMPLATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_static_template_v1.md")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_contract_v1.md")


def _text(path: Path = DOC) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_doc_exists_and_source_docs_exist() -> None:
    assert DOC.exists()
    assert STATIC_TEMPLATE_DOC.exists()
    assert CONTRACT_DOC.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.STATIC.TEMPLATE.QA.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.STATIC.TEMPLATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_STATIC_TEMPLATE_PASS_READY_FOR_STATIC_TEMPLATE_QA_GATE" in text
    assert "46e718cc8e56f87b0f44a0d6c4c5f4124e5f91cb" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-static-template-v1-20260620" in text


def test_files_under_qa_are_recorded() -> None:
    text = _text()
    assert "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_static_template_v1.md" in text
    assert "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_contract_v1.md" in text


def test_all_qa_checks_are_defined() -> None:
    text = _text()
    for token in [
        "Check 1 - Required report identity is present",
        "Check 2 - Required sections are present and ordered",
        "Check 3 - Current scanner facts are present",
        "Check 4 - Media intake interpretation is accurate",
        "Check 5 - Current output families are accurate",
        "Check 6 - Roadmap modules are not over-claimed",
        "Check 7 - Privacy-safe visible report text",
        "Check 8 - Boundary remains docs/test-only",
    ]:
        assert token in text


def test_required_identity_and_sections_are_gated() -> None:
    text = _text()
    for token in [
        "CID Local Media Agent - Internal Demo Visible Report",
        "producer_product_post_internal_review",
        "internal_demo_only",
        "local_only",
        "approved_synthetic_controlled_demo",
        "Executive Summary",
        "Local-Only Privacy Confirmation",
        "Controlled Demo Input Summary",
        "Scanner Result Summary",
        "Accepted Media",
        "Rejected Non-Media",
        "Human Review Required",
        "Warnings",
        "Created Output Artifacts",
        "Roadmap Modules Not Yet Generated",
        "Producer Interpretation",
        "Next Technical Actions",
    ]:
        assert token in text


def test_current_scanner_facts_and_media_intake_are_gated() -> None:
    text = _text()
    for token in [
        "completed_with_warnings",
        "candidate media count: 5",
        "human review required count: 1",
        "warnings count: 1",
        "unknown synthetic placeholder",
        "ffprobe preflight: skipped",
        "original media left client system: false",
        "`.mov = 1`",
        "`.mp4 = 2`",
        "`.wav = 1`",
        "`.exe = 1`",
        "`.txt = 2`",
        "accepted media are scanner candidates, not edited deliverables",
        "rejected non-media protects the media catalog",
        "ambiguous material is surfaced to human review",
    ]:
        assert token in text


def test_output_families_and_roadmap_boundaries_are_gated() -> None:
    text = _text()
    for token in [
        "`00_project/`",
        "`01_media_catalog/`",
        "`99_logs/`",
        "audio synchronization",
        "transcription",
        "subtitle generation",
        "translation",
        "report generation runtime",
        "DaVinci Resolve export",
        "Avid export",
        "`02_audio_sync/`",
        "`03_transcription/`",
        "`04_subtitles/`",
        "`05_reports/`",
        "`06_exports/`",
    ]:
        assert token in text


def test_privacy_forbidden_tokens_are_gated() -> None:
    text = _text()
    for token in [
        "`/mnt/`",
        "Windows drive paths",
        "UNC paths",
        "`DESKTOP-`",
        "`harliesound`",
        "`SERVICIOS_CINE`",
        "repository paths",
        "private project titles",
        "private filenames from real shoots",
        "avoids local user names, machine names, absolute system paths, repository paths, and real client material",
    ]:
        assert token in text


def test_static_template_does_not_contain_local_environment_leaks() -> None:
    text = _text(STATIC_TEMPLATE_DOC)
    forbidden = [
        "/mnt/",
        "DESKTOP-",
        "harliesound",
        "SERVICIOS_CINE",
        "\\\\wsl.localhost",
        "C:\\\\",
    ]
    for token in forbidden:
        assert token not in text


def test_boundary_decision_result_and_next_phase_are_recorded() -> None:
    text = _text()
    for token in [
        "runtime report generation",
        "scanner implementation changes",
        "real media scanning",
        "public demo use",
        "client-facing demo use",
        "ffprobe execution",
        "ffmpeg execution",
        "SaaS upload",
        "database writes",
        "network calls",
        "Docker or Alembic changes",
        "frontend/backend SaaS changes",
        "Stripe, AI Jobs, credits, or ledger changes",
        "readable by producer, product, and post-production stakeholders",
        "staying technically honest about the current scanner baseline",
        "not as a finished sync, transcription, subtitle, export, or client-facing delivery product",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_STATIC_TEMPLATE_QA_GATE_PASS_READY_FOR_STATIC_REPORT_FIXTURE",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.STATIC.FIXTURE.V1",
    ]:
        assert token in text
