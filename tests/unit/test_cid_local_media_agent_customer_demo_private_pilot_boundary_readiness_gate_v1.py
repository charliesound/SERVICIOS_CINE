from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_private_pilot_boundary_readiness_gate_v1.md"
)

FEEDBACK_CAPTURE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_prospect_feedback_capture_gate_v1.md"
)

FEEDBACK_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_prospect_feedback_capture_readiness_gate_v1.md"
)

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)

MEETING_PACK_DOC = Path(
    "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_private_pilot_boundary_readiness_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PRIVATE_PILOT_BOUNDARY.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PRIVATE_PILOT_BOUNDARY_READINESS_GATE_V1_CLOSED" in text
    assert "SAFE_PLACEHOLDER_PROSPECT_FEEDBACK_CAPTURED" in text
    assert "READY_FOR_SAFE_PRIVATE_PILOT_BOUNDARY_DRAFTING" in text


def test_private_pilot_boundary_readiness_records_base_state() -> None:
    text = _text()

    assert "5a574aa8e428893068041c4702d2689ee4eaa639" in text
    assert "5a574aa docs: add CID Local Media Agent prospect feedback capture gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-prospect-feedback-capture-gate-v1-20260701" in text


def test_private_pilot_boundary_readiness_references_upstream_documents() -> None:
    text = _text()

    assert FEEDBACK_CAPTURE_DOC.exists()
    assert FEEDBACK_READINESS_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert MEETING_PACK_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_prospect_feedback_capture_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_prospect_feedback_capture_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md" in text


def test_private_pilot_boundary_readiness_does_not_approve_execution() -> None:
    text = _text()

    markers = [
        "This gate prepares private pilot boundary drafting only.",
        "This gate does not approve private pilot execution.",
        "This gate does not define a real customer.",
        "This gate does not include customer names.",
        "This gate does not request customer files.",
        "This gate does not process real media.",
        "This gate does not approve production use.",
        "This gate does not approve paid delivery.",
        "This gate does not create an installer.",
        "This gate does not create binaries.",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_readiness_explains_why_gate_exists() -> None:
    text = _text()

    markers = [
        "The production path requires a written private pilot boundary before any real customer execution.",
        "A pilot must not be improvised during a meeting.",
        "A pilot must separate commercial interest from technical approval.",
        "A pilot must define exactly what is allowed and what is forbidden.",
        "A pilot must protect customer material, customer privacy, and source files.",
        "A pilot must have stop conditions before any execution occurs.",
        "A pilot must not become production use by accident.",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_readiness_defines_private_pilot() -> None:
    text = _text()

    markers = [
        "A private pilot is a limited, written, controlled evaluation with a trusted prospect.",
        "A private pilot is not public production use.",
        "A private pilot is not paid delivery by default.",
        "A private pilot is not unlimited customer file processing.",
        "A private pilot is not permission to scan folders recursively.",
        "A private pilot is not permission to upload media.",
        "A private pilot is not permission to modify source files.",
        "A private pilot is not permission to use confidential material without explicit written scope.",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_readiness_contains_boundary_template() -> None:
    text = _text()

    fields = [
        "Pilot boundary id: controlled_private_pilot_boundary_placeholder_v1",
        "Pilot status: draft_template_only",
        "Customer category: producer | executive producer | postproduction supervisor | school | other",
        "Customer identity: not recorded in this readiness gate",
        "Operator: internal operator only",
        "Machine: to be defined later",
        "Operating system: to be defined later",
        "Execution location: local-only",
        "Network policy: no upload by default",
        "Material category: placeholder only until separately approved",
        "Forbidden material type: confidential material unless explicitly authorized",
        "Recursive traversal: forbidden unless separately approved",
        "Batch processing: forbidden unless separately approved",
        "Allowed output: controlled human-readable report",
        "Source file policy: read-only",
        "Approval required before execution: yes",
    ]

    for field in fields:
        assert field in text


def test_private_pilot_boundary_readiness_lists_required_future_fields() -> None:
    text = _text()

    fields = [
        "Allowed customer category.",
        "Allowed operator.",
        "Allowed machine.",
        "Allowed operating system.",
        "Allowed execution location.",
        "Allowed material category.",
        "Allowed material type.",
        "Allowed file count.",
        "Allowed folder count.",
        "Allowed output report.",
        "Forbidden operations.",
        "Read-only source policy.",
        "Controlled output path.",
        "Network policy.",
        "Retention rule.",
        "Deletion rule.",
        "Support owner.",
        "Support window.",
        "Rollback rule.",
        "Success criteria.",
        "Failure criteria.",
        "Stop conditions.",
        "Commercial status.",
        "Production status.",
        "Explicit approval before execution.",
    ]

    for field in fields:
        assert field in text


def test_private_pilot_boundary_readiness_lists_forbidden_operations() -> None:
    text = _text()

    forbidden = [
        "Unscoped customer files.",
        "Confidential production material.",
        "Recursive folder scan.",
        "Batch folder scan.",
        "Any upload.",
        "Any source file modification.",
        "Any destructive write.",
        "Any customer data committed to repository.",
        "Any hidden network access.",
        "Any production workflow replacement.",
        "Any public demonstration.",
        "Any installer distribution.",
        "Any binary distribution.",
        "Any SaaS integration.",
        "Any database integration.",
        "Any transcription.",
        "Any subtitles.",
        "Any sync.",
        "Any DaVinci Resolve integration.",
        "Any Avid integration.",
    ]

    for marker in forbidden:
        assert marker in text


def test_private_pilot_boundary_readiness_lists_stop_conditions() -> None:
    text = _text()

    markers = [
        "Stop if customer material is outside written scope.",
        "Stop if customer requests recursive scan without approval.",
        "Stop if customer requests batch processing without approval.",
        "Stop if confidential content appears unexpectedly.",
        "Stop if source files may be modified.",
        "Stop if output path is not controlled.",
        "Stop if network behavior is unclear.",
        "Stop if operator cannot explain limitations.",
        "Stop if prospect interprets pilot as production use.",
        "Stop if execution result cannot be audited.",
        "Stop if any dependency behaves unexpectedly.",
        "Stop if privacy expectations are unclear.",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_readiness_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Private pilot boundary readiness phase is defined.",
        "Base state is recorded.",
        "Feedback capture gate is referenced.",
        "Production path scope gate is referenced.",
        "Meeting pack is referenced.",
        "Boundary template status is template only.",
        "Private pilot definition is explicit.",
        "Private pilot boundary template is present.",
        "Required future boundary fields are listed.",
        "Forbidden operations are listed.",
        "Required stop conditions are listed.",
        "No actual private pilot is created.",
        "No real customer is named.",
        "No company identity is recorded.",
        "No customer material is requested.",
        "No real media is processed.",
        "No production use is approved.",
        "No paid delivery is approved.",
        "No installer is created.",
        "No binary is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_private_pilot_boundary_readiness_keeps_limitations_active() -> None:
    text = _text()

    limitations = [
        "Production use is not approved.",
        "Paid delivery is not approved.",
        "Private pilot execution is not approved.",
        "Real media processing is not approved.",
        "Customer material processing is not approved.",
        "Folder scanning is not approved.",
        "Batch processing is not approved.",
        "Recursive traversal is not approved.",
        "Transcription is not approved.",
        "Subtitles are not approved.",
        "Sync is not approved.",
        "DaVinci Resolve integration is not approved.",
        "Avid integration is not approved.",
        "SaaS integration is not approved.",
        "Installer delivery is not approved.",
        "Binary distribution is not approved.",
    ]

    for limitation in limitations:
        assert limitation in text


def test_private_pilot_boundary_readiness_keeps_safety_confirmation_explicit() -> None:
    text = _text()

    markers = [
        "No real media is allowed in this gate.",
        "No customer material is allowed in this gate.",
        "No production material is allowed in this gate.",
        "No confidential material is allowed in this gate.",
        "No FFmpeg is allowed in this gate.",
        "No ffprobe is allowed in this gate.",
        "No scanner integration is allowed in this gate.",
        "No batch traversal is allowed in this gate.",
        "No recursive traversal is allowed in this gate.",
        "No SaaS module is allowed in this gate.",
        "No database is allowed in this gate.",
        "No backend change is allowed in this gate.",
        "No frontend change is allowed in this gate.",
        "No Docker change is allowed in this gate.",
        "No Alembic change is allowed in this gate.",
        "No Stripe change is allowed in this gate.",
        "No AI Jobs change is allowed in this gate.",
        "No credits or ledger change is allowed in this gate.",
        "No installer is created in this gate.",
        "No binary is created in this gate.",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_readiness_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this private pilot boundary readiness document.",
        "Add one private pilot boundary readiness unit test.",
        "Inspect existing prospect feedback capture document.",
        "Inspect existing production use path scope document.",
        "Inspect existing customer demo meeting pack document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No actual private pilot creation.",
        "No private pilot execution.",
        "No real customer names.",
        "No company names.",
        "No emails.",
        "No phone numbers.",
        "No confidential project details.",
        "No customer file paths.",
        "No media filenames from customer material.",
        "No customer files.",
        "No production approval.",
        "No paid delivery approval.",
        "No meeting pack edits.",
        "No implementation changes.",
        "No execution against real media.",
        "No execution against customer material.",
        "No FFmpeg.",
        "No ffprobe.",
        "No scanner integration.",
        "No batch processing.",
        "No recursive traversal.",
        "No SaaS integration.",
        "No database access.",
        "No backend changes.",
        "No frontend changes.",
        "No installer work.",
        "No binary packaging.",
    ]

    for marker in allowed + forbidden:
        assert marker in text


def test_private_pilot_boundary_readiness_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PRIVATE_PILOT_BOUNDARY.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PRIVATE_PILOT_BOUNDARY_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent private pilot boundary readiness gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-private-pilot-boundary-readiness-gate-v1-20260701" in text
