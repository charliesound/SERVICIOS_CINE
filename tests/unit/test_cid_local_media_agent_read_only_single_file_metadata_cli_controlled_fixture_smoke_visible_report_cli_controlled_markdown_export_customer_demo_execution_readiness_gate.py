from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_execution_readiness_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_customer_demo_execution_readiness_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.EXECUTION.READINESS.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_EXECUTION_READINESS_GATE_V1_CLOSED"
        in text
    )
    assert "READY_FOR_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PREFLIGHT_ONLY" in text


def test_customer_demo_execution_readiness_gate_records_base_state() -> None:
    text = _doc_text()

    assert "aad24d1f08f5a071f0568f0116744763720d2f91" in text
    assert "aad24d1 test: add CID Local Media Agent customer demo script gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-script-gate-v1-20260701"
        in text
    )


def test_customer_demo_execution_readiness_gate_defines_execution_scope() -> None:
    text = _doc_text()

    assert "Controlled customer-facing scripted presentation readiness." in text
    assert "Owner/operator only." in text
    assert "This gate does not execute the customer demo." in text
    assert "This gate does not approve customer material." in text
    assert "This gate does not approve real media." in text
    assert "This gate does not approve production use." in text


def test_customer_demo_execution_readiness_gate_defines_audiences() -> None:
    text = _doc_text()

    allowed = [
        "Trusted producer.",
        "Trusted executive producer.",
        "Trusted production manager.",
        "Trusted postproduction supervisor.",
        "Trusted distributor or exhibitor technical stakeholder.",
        "Trusted school decision-maker without participant files.",
    ]
    forbidden = [
        "Public launch audience.",
        "Paid delivery audience.",
        "Unsupervised user.",
        "Workshop participants using their own files.",
        "Real project team using production material.",
        "Any audience expecting production-ready processing.",
    ]

    for marker in allowed + forbidden:
        assert marker in text


def test_customer_demo_execution_readiness_gate_records_preflight_checklist() -> None:
    text = _doc_text()

    checklist = [
        "Confirm working directory is /opt/SERVICIOS_CINE.",
        "Confirm virtual environment is active.",
        "Confirm branch is main.",
        "Confirm HEAD is aad24d1f08f5a071f0568f0116744763720d2f91.",
        "Confirm stable script gate tag points to the same HEAD.",
        "Confirm workspace is clean.",
        "Confirm no export root exists before the demo.",
        "Confirm the target path is the controlled fixture path.",
        "Confirm the output path is inside the controlled temporary export root.",
        "Confirm no real media path is present.",
        "Confirm no customer material path is present.",
        "Confirm no SaaS screen is opened.",
        "Confirm no database screen is opened.",
    ]

    for item in checklist:
        assert item in text


def test_customer_demo_execution_readiness_gate_records_operator_lines() -> None:
    text = _doc_text()

    assert "This is a controlled local-first technical preview using an internal non-customer fixture only." in text
    assert "I will not process real footage, real sound, confidential files, or customer material in this demo." in text
    assert "The useful proof today is the controlled report chain" in text


def test_customer_demo_execution_readiness_gate_records_screen_order() -> None:
    text = _doc_text()

    screen_markers = [
        "Screen 1: Terminal inside /opt/SERVICIOS_CINE.",
        "Screen 2: Show current stable HEAD and clean workspace.",
        "Screen 4: Run visible report to stdout.",
        "Screen 7: Run controlled Markdown export.",
        "Screen 10: Capture generated report digest.",
        "Screen 12: Show final clean workspace.",
        "Screen 14: Close with private pilot boundary discussion.",
    ]

    for marker in screen_markers:
        assert marker in text


def test_customer_demo_execution_readiness_gate_records_safe_command_sequence() -> None:
    text = _doc_text()

    command_markers = [
        "PRECHECK_STATUS:",
        "PRECHECK_EXPORT_ROOT:",
        "STDOUT_REPORT:",
        "EXPORT_PREP:",
        "EXPORT_REPORT:",
        "VERIFY_REPORT:",
        "CLEANUP:",
        "FINAL_STATUS:",
        "git status --short",
        "git rev-parse HEAD",
        "test ! -e tests/tmp/local_media_agent/controlled_visible_report_exports",
        "--visible-report-markdown",
        "--visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md",
        "sha256sum tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md",
        "rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports",
    ]

    for marker in command_markers:
        assert marker in text


def test_customer_demo_execution_readiness_gate_records_fixture_identity() -> None:
    text = _doc_text()

    assert "controlled_plain_text_marker_v1" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )
    assert "CID Local Media Agent - Controlled Fixture Smoke Visible Report" in text


def test_customer_demo_execution_readiness_gate_records_evidence_to_capture() -> None:
    text = _doc_text()

    evidence = [
        "stdout success marker.",
        "exported report file size.",
        "exported report digest.",
        "report title verification.",
        "allowed relative path verification.",
        "controlled fixture digest verification.",
        "cleanup confirmation.",
        "final clean workspace confirmation.",
        "audience questions asked.",
        "next-step decision.",
    ]

    for item in evidence:
        assert item in text


def test_customer_demo_execution_readiness_gate_records_pass_and_fail_criteria() -> None:
    text = _doc_text()

    pass_items = [
        "Repository is at expected stable base.",
        "Workspace is clean before execution.",
        "Only controlled fixture path is used.",
        "Controlled export command returns expected success marker.",
        "Report contains expected title.",
        "Generated report digest is recorded.",
        "Workspace is clean after execution.",
    ]

    fail_items = [
        "Repository is not at expected stable base.",
        "Workspace is dirty before execution.",
        "Target path differs from controlled fixture path.",
        "Output path leaves controlled temporary export root.",
        "Expected success marker is absent.",
        "Report verification fails.",
        "Cleanup fails.",
        "Workspace is dirty after cleanup.",
    ]

    for item in pass_items + fail_items:
        assert item in text


def test_customer_demo_execution_readiness_gate_records_go_no_go_decision() -> None:
    text = _doc_text()

    assert "GO only if every preflight item passes." in text
    assert "NO-GO if any stop condition is true." in text
    assert "NO-GO if customer material is requested." in text
    assert "NO-GO if real media processing is requested." in text
    assert "NO-GO if the operator cannot clearly explain the current limitations." in text


def test_customer_demo_execution_readiness_gate_records_stop_conditions() -> None:
    text = _doc_text()

    stop_conditions = [
        "Stop if the repository is not at the expected stable base.",
        "Stop if the workspace is not clean before the demo.",
        "Stop if the target path is not the controlled fixture path.",
        "Stop if the output path is not inside the controlled temporary export root.",
        "Stop if the output suffix is not .md.",
        "Stop if any customer or real media path appears.",
        "Stop if any production folder path appears.",
        "Stop if the wrapper does not return the expected success marker.",
        "Stop if report verification fails.",
        "Stop if cleanup fails.",
        "Stop if workspace final status is not clean.",
        "Stop if the audience asks to process real material during this gate.",
        "Stop if the audience interprets the demo as production-ready.",
    ]

    for condition in stop_conditions:
        assert condition in text


def test_customer_demo_execution_readiness_gate_records_close_options_and_not_allowed_after_demo() -> None:
    text = _doc_text()

    close_options = [
        "Option 1: Schedule a private requirements call.",
        "Option 2: Define a paid pilot boundary.",
        "Option 3: Identify the first real-media gate needed before a private pilot.",
        "Option 4: Collect sample requirements without taking customer files.",
        "Option 5: Ask who approves technical pilots.",
    ]

    not_allowed = [
        "Do not take customer media.",
        "Do not promise immediate real-media processing.",
        "Do not promise folder scanning.",
        "Do not promise transcription.",
        "Do not promise sync.",
        "Do not promise subtitles.",
        "Do not promise DaVinci Resolve integration.",
        "Do not promise Avid integration.",
        "Do not promise SaaS integration.",
        "Do not promise installer delivery.",
        "Do not promise production readiness.",
    ]

    for marker in close_options + not_allowed:
        assert marker in text


def test_customer_demo_execution_readiness_gate_keeps_safety_scope_explicit() -> None:
    text = _doc_text()

    safety_markers = [
        "No real media is allowed.",
        "No customer material is allowed.",
        "No production material is allowed.",
        "No confidential material is allowed.",
        "No FFmpeg is allowed.",
        "No ffprobe is allowed.",
        "No scanner integration is allowed.",
        "No batch traversal is allowed.",
        "No recursive traversal is allowed.",
        "No SaaS module is allowed.",
        "No database is allowed.",
        "No backend change is allowed.",
        "No frontend change is allowed.",
        "No Docker change is allowed.",
        "No Alembic change is allowed.",
        "No Stripe change is allowed.",
        "No AI Jobs change is allowed.",
        "No credits or ledger change is allowed.",
        "No committed customer demo export artifact is allowed.",
    ]

    for marker in safety_markers:
        assert marker in text


def test_customer_demo_execution_readiness_gate_keeps_forbidden_scope_explicit() -> None:
    text = _doc_text()

    forbidden_markers = [
        "No implementation changes.",
        "No parser changes.",
        "No CLI behavior changes.",
        "No wrapper changes.",
        "No renderer changes.",
        "No in-memory integration changes.",
        "No fixture modification.",
        "No committed export artifact.",
        "No execution against real media.",
        "No execution against customer material.",
        "No FFmpeg.",
        "No ffprobe.",
        "No scanner integration.",
        "No batch processing.",
        "No recursive traversal.",
        "No unsafe shell execution.",
        "No pyproject modification.",
        "No console script registration.",
        "No SaaS integration.",
        "No database access.",
        "No backend changes.",
        "No frontend changes.",
        "No installer work.",
        "No Docker work.",
        "No Alembic work.",
        "No Stripe work.",
        "No AI Jobs work.",
        "No credits or ledger work.",
    ]

    for marker in forbidden_markers:
        assert marker in text


def test_customer_demo_execution_readiness_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
        "Customer demo execution readiness gate test.",
        "Customer demo script gate test.",
        "Customer demo readiness gate test.",
        "Manual demo execution QA gate test.",
        "Manual demo execution gate test.",
        "Manual demo readiness gate test.",
        "Controlled demo execution QA gate test.",
        "Controlled demo execution gate test.",
        "Wrapper smoke execution QA gate test.",
        "Wrapper smoke execution gate test.",
        "Implementation QA gate test.",
        "Implementation gate test.",
        "In-memory wrapper smoke execution QA gate test.",
        "In-memory wrapper smoke execution gate test.",
        "Visible report contract test.",
        "CLI contract gate test.",
        "WSL repo guard.",
        "PostgreSQL-only regression guard required by policy.",
    ]

    for validation_target in validation_targets:
        assert validation_target in text


def test_customer_demo_execution_readiness_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent customer demo execution readiness gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-execution-readiness-gate-v1-20260701"
        in text
    )
