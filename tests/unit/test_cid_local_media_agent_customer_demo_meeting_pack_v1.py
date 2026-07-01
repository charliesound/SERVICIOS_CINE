from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_meeting_pack_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_customer_demo_meeting_pack_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.PACKAGING.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_PACKAGING_GATE_V1_CLOSED"
        in text
    )
    assert "SAFE_CUSTOMER_DEMO_MEETING_PACK_CREATED" in text


def test_customer_demo_meeting_pack_records_base_state() -> None:
    text = _doc_text()

    assert "5d664840018db93502db3d487a80a0ae92692f87" in text
    assert "5d66484 test: add CID Local Media Agent customer demo packaging readiness gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-readiness-gate-v1-20260701"
        in text
    )


def test_customer_demo_meeting_pack_defines_pack_use_and_limits() -> None:
    text = _doc_text()

    assert "Safe controlled customer demo meeting pack." in text
    assert "Owner/operator only." in text
    assert "Spanish meeting copy with technical evidence preserved." in text
    assert "Private one-to-one meeting" in text
    assert "Public launch." in text
    assert "Paid delivery." in text
    assert "Unsupervised execution." in text
    assert "Customer media ingestion." in text


def test_customer_demo_meeting_pack_contains_pitch_and_summary() -> None:
    text = _doc_text()

    assert "CID Local Media Agent - Demo controlada para productores audiovisuales" in text
    assert "CID Local Media Agent está pensado para ayudar" in text
    assert "CID Local Media Agent es una línea de producto local-first" in text
    assert "La demo actual no procesa material real." in text
    assert "La demo actual no procesa material de cliente." in text
    assert "reducir desorden, riesgo y pérdida de tiempo" in text


def test_customer_demo_meeting_pack_contains_opening_and_boundary_scripts() -> None:
    text = _doc_text()

    opening_markers = [
        "Esto es una demo técnica controlada, no una versión comercial final.",
        "el material del cliente debe quedarse en su máquina",
        "Hoy no voy a procesar material real, sonido real, material confidencial ni archivos del cliente.",
        "validación, informe visible, exportación controlada, verificación, limpieza y evidencia.",
        "Esta demo no demuestra todavía escaneo de carpetas reales.",
        "Esta demo no demuestra transcripción.",
        "Esta demo no demuestra sincronización.",
        "Esta demo solo demuestra que la cadena local de reporte controlado ya está funcionando y auditada.",
    ]

    for marker in opening_markers:
        assert marker in text


def test_customer_demo_meeting_pack_contains_screen_order() -> None:
    text = _doc_text()

    screen_markers = [
        "1. Terminal en /opt/SERVICIOS_CINE.",
        "2. Rama main.",
        "3. HEAD estable esperado.",
        "4. Tag estable esperado.",
        "5. Workspace limpio.",
        "6. Fixture interno no cliente.",
        "7. Comando de informe visible por stdout.",
        "10. Marcador CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK.",
        "13. SHA256 del reporte generado.",
        "15. Workspace final limpio.",
    ]

    for marker in screen_markers:
        assert marker in text


def test_customer_demo_meeting_pack_contains_safe_preflight() -> None:
    text = _doc_text()

    preflight_markers = [
        "Workdir must be /opt/SERVICIOS_CINE.",
        "Virtual environment must be active.",
        "Branch must be main.",
        "HEAD must be 5d664840018db93502db3d487a80a0ae92692f87",
        "Workspace must be clean.",
        "Controlled export root must be absent before execution.",
        "No real media path may be used.",
        "No customer path may be used.",
        "No production path may be used.",
        "No cloud upload may be shown.",
        "No SaaS screen may be shown.",
        "No database screen may be shown.",
        "No installer may be shown.",
        "No binary package may be shown.",
    ]

    for marker in preflight_markers:
        assert marker in text


def test_customer_demo_meeting_pack_contains_safe_commands() -> None:
    text = _doc_text()

    assert "SAFE_STDOUT_REPORT_COMMAND:" in text
    assert "SAFE_EXPORT_REPORT_COMMAND:" in text
    assert "SAFE_VERIFY_COMMANDS:" in text
    assert "SAFE_CLEANUP_COMMAND:" in text
    assert "--target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt" in text
    assert "--fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "--expected-bytes 239" in text
    assert "--allowed-relative-path media/controlled_plain_text_marker.txt" in text
    assert "--visible-report-markdown" in text
    assert "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK" in text


def test_customer_demo_meeting_pack_records_controlled_fixture_identity() -> None:
    text = _doc_text()

    assert "CONTROLLED_FIXTURE_ID:\ncontrolled_plain_text_marker_v1" in text
    assert "CONTROLLED_FIXTURE_ROOT:" in text
    assert "CONTROLLED_TARGET_PATH:" in text
    assert "ALLOWED_RELATIVE_PATH:\nmedia/controlled_plain_text_marker.txt" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "EXPECTED_FIXTURE_SHA256:\n"
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )


def test_customer_demo_meeting_pack_records_last_execution_evidence() -> None:
    text = _doc_text()

    assert "Customer demo execution result: LOCAL_MEDIA_AGENT_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PASS" in text
    assert "Generated report size: 1795 bytes" in text
    assert "Generated report SHA256: b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd" in text
    assert "Controlled fixture SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a" in text
    assert "Final workspace: clean" in text


def test_customer_demo_meeting_pack_contains_business_value_hypotheses() -> None:
    text = _doc_text()

    hypotheses = [
        "Reduce chaos when several productions deliver material at the same time.",
        "Give producers and production managers early visibility before material enters postproduction.",
        "Help detect incomplete or suspicious handoffs before they become schedule problems.",
        "Create local reports that can be reviewed without uploading sensitive files.",
        "Offer a future bridge between local project material and CID production coordination.",
    ]

    for hypothesis in hypotheses:
        assert hypothesis in text


def test_customer_demo_meeting_pack_contains_producer_discovery_questions() -> None:
    text = _doc_text()

    questions = [
        "How many active productions do you supervise at the same time?",
        "How many production managers, coordinators, DITs, editors, or vendors send material to you?",
        "Where does material control currently break: shooting, handoff, ingest, editing, delivery, or archive?",
        "Who currently checks whether incoming material is complete and understandable?",
        "Would a local report before upload or handoff reduce operational risk?",
        "What kind of first real-media preflight would be worth paying for?",
        "Who would approve a private pilot?",
        "What material cannot leave your premises under any circumstance?",
        "Would your team prefer a local app, CLI workflow, or CID-integrated module?",
    ]

    for question in questions:
        assert question in text


def test_customer_demo_meeting_pack_defines_private_pilot_boundary() -> None:
    text = _doc_text()

    boundary_markers = [
        "A future private pilot may be discussed.",
        "A future private pilot must have explicit scope.",
        "A future private pilot must define accepted file types.",
        "A future private pilot must define allowed test material.",
        "A future private pilot must define what cannot be copied or uploaded.",
        "A future private pilot must define success criteria.",
        "This meeting pack does not itself approve a private pilot.",
    ]

    for marker in boundary_markers:
        assert marker in text


def test_customer_demo_meeting_pack_contains_follow_up_options() -> None:
    text = _doc_text()

    follow_up = [
        "Schedule a requirements call.",
        "Collect only non-sensitive workflow requirements.",
        "Define first real-media preflight requirements without taking files.",
        "Request synthetic or non-confidential sample structures only.",
        "Define a written private pilot boundary.",
        "Define pilot success criteria.",
        "Define pilot buyer, user, and technical approver.",
        "Prepare a future real-media preflight readiness gate only after explicit authorization.",
    ]

    for marker in follow_up:
        assert marker in text


def test_customer_demo_meeting_pack_contains_do_not_promise_list() -> None:
    text = _doc_text()

    do_not_promise = [
        "Do not promise production readiness.",
        "Do not promise installer availability.",
        "Do not promise Windows or macOS packaging from this demo.",
        "Do not promise FFmpeg or ffprobe processing from this demo.",
        "Do not promise transcription from this demo.",
        "Do not promise sync from this demo.",
        "Do not promise subtitles from this demo.",
        "Do not promise DaVinci Resolve or Avid integration from this demo.",
        "Do not promise SaaS integration from this demo.",
        "Do not promise customer data processing from this demo.",
        "Do not promise delivery dates without a scoped plan.",
    ]

    for marker in do_not_promise:
        assert marker in text


def test_customer_demo_meeting_pack_contains_stop_conditions() -> None:
    text = _doc_text()

    stop_conditions = [
        "Stop if the prospect asks to process real material during the meeting.",
        "Stop if the prospect asks to send files.",
        "Stop if the prospect wants to drag and drop customer media.",
        "Stop if the prospect interprets the demo as production-ready.",
        "Stop if the repo is not at the expected stable state.",
        "Stop if the workspace is not clean.",
        "Stop if the fixture path changes.",
        "Stop if the export path leaves the controlled temporary root.",
        "Stop if report verification fails.",
        "Stop if cleanup fails.",
        "Stop if any customer material appears on screen.",
    ]

    for marker in stop_conditions:
        assert marker in text


def test_customer_demo_meeting_pack_contains_close_options() -> None:
    text = _doc_text()

    close_options = [
        "Option 1: No fit now; record objections.",
        "Option 2: Requirements call only.",
        "Option 3: Define private pilot boundary.",
        "Option 4: Prepare future first real-media preflight readiness.",
        "Option 5: Discuss commercial buyer and pricing assumptions later.",
    ]

    for marker in close_options:
        assert marker in text


def test_customer_demo_meeting_pack_records_packaging_gate_pass_criteria() -> None:
    text = _doc_text()

    criteria = [
        "Meeting title is present.",
        "One-sentence pitch is present.",
        "Executive summary is present.",
        "Opening script is present.",
        "Demo boundary script is present.",
        "Screen order is present.",
        "Safe pre-meeting preflight is present.",
        "Safe stdout report command is present.",
        "Safe export report command is present.",
        "Safe verify commands are present.",
        "Safe cleanup command is present.",
        "Controlled fixture identity is present.",
        "Last verified execution evidence is present.",
        "Business value hypotheses are present.",
        "Producer discovery questions are present.",
        "Private pilot boundary is present.",
        "Safe follow-up options are present.",
        "Do-not-promise list is present.",
        "Stop conditions are present.",
        "Meeting close options are present.",
        "No real material is included.",
        "No customer material is included.",
        "No generated report artifact is committed.",
        "No installer is created.",
        "No binary package is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_customer_demo_meeting_pack_keeps_safety_scope_explicit() -> None:
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
        "No installer is created.",
        "No binary is created.",
    ]

    for marker in safety_markers:
        assert marker in text


def test_customer_demo_meeting_pack_keeps_forbidden_scope_explicit() -> None:
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
        "No binary packaging.",
        "No Docker work.",
        "No Alembic work.",
        "No Stripe work.",
        "No AI Jobs work.",
        "No credits or ledger work.",
    ]

    for marker in forbidden_markers:
        assert marker in text


def test_customer_demo_meeting_pack_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
        "Customer demo meeting pack test.",
        "Customer demo packaging readiness gate test.",
        "Customer demo execution QA gate test.",
        "Customer demo execution gate test.",
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


def test_customer_demo_meeting_pack_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "docs: add CID Local Media Agent customer demo meeting pack" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-gate-v1-20260701"
        in text
    )
