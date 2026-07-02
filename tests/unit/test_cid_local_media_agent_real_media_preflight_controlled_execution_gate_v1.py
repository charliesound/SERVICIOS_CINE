from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md"
)

READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_readiness_gate_v1.md"
)

PLANNING_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_planning_gate_v1.md"
)

PRIVATE_PILOT_BOUNDARY_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_private_pilot_boundary_gate_v1.md"
)

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_controlled_execution_gate_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_EXECUTION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_EXECUTION_GATE_V1_CLOSED" in text
    assert "READY_FOR_SINGLE_FILE_REAL_MEDIA_PREFLIGHT_CONTROLLED_EXECUTION_GATE" in text
    assert "CONTROLLED_EXECUTION_DEFERRED_PENDING_EXPLICIT_SINGLE_LOCAL_FILE" in text


def test_controlled_execution_gate_records_base_state() -> None:
    text = _text()

    assert "f1e2fb9c545157d56d927cbaf324a5a65a24f9e0" in text
    assert "f1e2fb9 docs: add CID Local Media Agent real media preflight readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-readiness-gate-v1-20260702" in text


def test_controlled_execution_gate_references_upstream_documents() -> None:
    text = _text()

    assert READINESS_DOC.exists()
    assert PLANNING_DOC.exists()
    assert PRIVATE_PILOT_BOUNDARY_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_planning_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_private_pilot_boundary_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_controlled_execution_gate_is_no_runtime_execution() -> None:
    text = _text()

    markers = [
        "This gate does not execute real media.",
        "This gate does not select a real media file.",
        "This gate does not invent a file path.",
        "This gate does not request customer media.",
        "This gate does not process customer media.",
        "This gate does not run FFmpeg.",
        "This gate does not run ffprobe.",
        "This gate does not run scanner behavior.",
        "This gate does not approve production use.",
        "This gate does not approve paid delivery.",
    ]

    for marker in markers:
        assert marker in text


def test_controlled_execution_gate_explains_safe_deferral() -> None:
    text = _text()

    markers = [
        "A controlled execution gate must not fabricate a file path.",
        "A controlled execution gate must not silently choose media.",
        "A controlled execution gate must not run against customer files without written scope.",
        "A controlled execution gate must not run against confidential media.",
        "A controlled execution gate must stop when no explicit eligible local file is available.",
        "Deferring execution is the correct safe decision when the required input is missing.",
    ]

    for marker in markers:
        assert marker in text


def test_controlled_execution_gate_records_decision_fields() -> None:
    text = _text()

    fields = [
        "EXECUTION_DECISION_RECORD_ID:",
        "controlled_real_media_preflight_execution_deferred_v1",
        "EXECUTION_RECORD_TYPE:",
        "controlled_execution_decision_no_runtime_execution",
        "EXECUTION_DECISION:",
        "DEFERRED_NO_EXPLICIT_ELIGIBLE_SINGLE_LOCAL_FILE",
        "EXECUTION_STATUS:",
        "NOT_EXECUTED",
        "EXECUTION_ALLOWED:",
        "no",
        "EXECUTION_ATTEMPTED:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_controlled_execution_gate_records_no_file_no_customer_no_dependency() -> None:
    text = _text()

    fields = [
        "REAL_FILE_SELECTED:",
        "no",
        "REAL_FILE_PATH_RECORDED:",
        "no",
        "CUSTOMER_MEDIA_USED:",
        "no",
        "CUSTOMER_FILE_REQUESTED:",
        "no",
        "CONFIDENTIAL_MATERIAL_USED:",
        "no",
        "DEPENDENCY_COMMAND_RUN:",
        "no",
        "FFMPEG_RUN:",
        "no",
        "FFPROBE_RUN:",
        "no",
        "SCANNER_RUN:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_controlled_execution_gate_records_deferral_reasons() -> None:
    text = _text()

    reasons = [
        "No explicit local file path has been provided.",
        "No material owner has been confirmed.",
        "No confidentiality status has been confirmed.",
        "No output path has been approved for a real-media run.",
        "No execution command has been approved.",
    ]

    for reason in reasons:
        assert reason in text


def test_controlled_execution_gate_defines_required_input_before_any_execution() -> None:
    text = _text()

    requirements = [
        "One explicit local file path.",
        "Confirmation that the input is a file, not a folder.",
        "Confirmation that the file is not customer material unless separately scoped.",
        "Confirmation that the file is not confidential material.",
        "Confirmation that the operator owns or is authorized to use the file.",
        "Confirmation that source file policy is read-only.",
        "Confirmation that output path is controlled.",
        "Confirmation that no upload will occur.",
        "Confirmation that no batch behavior will occur.",
        "Confirmation that no recursive behavior will occur.",
        "Confirmation that no media-derived confidential data will be committed.",
    ]

    for requirement in requirements:
        assert requirement in text


def test_controlled_execution_gate_defines_deferred_boundary() -> None:
    text = _text()

    markers = [
        "The gate is closed as a safe decision record.",
        "execution is not allowed in the absence of explicit eligible input",
        "The gate does not claim real-media proof.",
        "The gate does not claim technical success against real media.",
        "The gate does not claim customer validation.",
        "The gate does not claim production readiness.",
        "The gate does not claim private pilot execution.",
        "The gate does not claim paid delivery readiness.",
    ]

    for marker in markers:
        assert marker in text


def test_controlled_execution_gate_records_validated_and_not_validated_scope() -> None:
    text = _text()

    validated = [
        "Controlled execution cannot proceed without explicit eligible input.",
        "The safe stop condition works.",
        "The readiness policy is respected.",
        "No file path is invented.",
        "No dependency command is run.",
        "No source media is touched.",
        "No customer data is captured.",
        "No production claim is made.",
    ]
    not_validated = [
        "Real file readability.",
        "Real media metadata.",
        "Real FFmpeg behavior.",
        "Real ffprobe behavior.",
        "Real scanner behavior.",
        "Real output report from media.",
        "Real dependency availability.",
        "Real performance.",
        "Real production usefulness.",
        "Real customer workflow usefulness.",
    ]

    for marker in validated + not_validated:
        assert marker in text


def test_controlled_execution_gate_defines_safe_next_step_and_input_selection_requirements() -> None:
    text = _text()

    markers = [
        "Create an explicit single-file input selection gate before any real-media execution.",
        "The selected input must be one file only.",
        "The selected input must be local.",
        "The selected input must be operator-owned or explicitly approved.",
        "The selected input must be non-confidential.",
        "The selected input must not be a folder.",
        "The selected input must not be a wildcard.",
        "The selected input must not be a glob.",
        "The selected input must not be a batch list.",
        "The selected input must not be customer media unless later written scope exists.",
        "The selected input path must not be committed if it contains personal or customer information.",
        "The selected input filename must not be committed if it reveals customer, project, or confidential data.",
    ]

    for marker in markers:
        assert marker in text


def test_controlled_execution_gate_confirms_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop because no explicit eligible single local file exists.",
        "Stop because no material owner is confirmed.",
        "Stop because no confidentiality status is confirmed.",
        "Stop because no approved output path exists for real-media execution.",
        "Stop because no dependency execution has been approved.",
        "Stop because no implementation change is allowed.",
        "Stop because no scanner behavior is allowed.",
        "Stop because no customer material is allowed.",
    ]

    for condition in conditions:
        assert condition in text


def test_controlled_execution_gate_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Controlled execution gate phase is defined.",
        "Base state is recorded.",
        "Real-media preflight readiness gate is referenced.",
        "Real-media preflight planning gate is referenced.",
        "Private pilot boundary gate is referenced.",
        "Production path scope gate is referenced.",
        "Execution decision record id is present.",
        "Execution record type is no runtime execution.",
        "Execution decision is deferred.",
        "Execution status is not executed.",
        "Execution allowed is no.",
        "Execution attempted is no.",
        "Real file selected is no.",
        "Real file path recorded is no.",
        "Customer media used is no.",
        "Dependency command run is no.",
        "FFmpeg run is no.",
        "ffprobe run is no.",
        "Scanner run is no.",
        "Deferral reason is explicit.",
        "Required input before execution is explicit.",
        "Deferred execution boundary is explicit.",
        "Validated scope is explicit.",
        "Non-validated scope is explicit.",
        "Safe next step is explicit.",
        "Stop conditions are confirmed.",
        "No real media is executed.",
        "No real file is selected.",
        "No customer material is requested.",
        "No dependency command is run.",
        "No production use is approved.",
        "No paid delivery is approved.",
        "No installer is created.",
        "No binary is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_controlled_execution_gate_keeps_limitations_and_safety_active() -> None:
    text = _text()

    markers = [
        "Production use is not approved.",
        "Paid delivery is not approved.",
        "Private pilot execution is not approved.",
        "Real media processing is not approved.",
        "Customer material processing is not approved.",
        "Folder scanning is not approved.",
        "Batch processing is not approved.",
        "Recursive traversal is not approved.",
        "No real media is executed in this gate.",
        "No real media file is selected in this gate.",
        "No customer material is allowed in this gate.",
        "No FFmpeg is allowed in this gate.",
        "No ffprobe is allowed in this gate.",
        "No scanner integration is allowed in this gate.",
        "No SaaS module is allowed in this gate.",
        "No database is allowed in this gate.",
        "No installer is created in this gate.",
        "No binary is created in this gate.",
    ]

    for marker in markers:
        assert marker in text


def test_controlled_execution_gate_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this real-media preflight controlled execution decision document.",
        "Add one real-media preflight controlled execution decision unit test.",
        "Inspect existing real-media preflight readiness document.",
        "Inspect existing real-media preflight planning document.",
        "Inspect existing private pilot boundary document.",
        "Inspect existing production use path scope document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No real-media execution.",
        "No real file selection.",
        "No customer media.",
        "No customer files.",
        "No production material.",
        "No confidential material.",
        "No customer file paths.",
        "No media filenames from customer material.",
        "No production approval.",
        "No paid delivery approval.",
        "No private pilot execution.",
        "No implementation changes.",
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


def test_controlled_execution_gate_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.EXPLICIT_SINGLE_FILE_SELECTION.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_EXPLICIT_SINGLE_FILE_SELECTION_READINESS_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent real media preflight controlled execution gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-controlled-execution-gate-v1-20260702" in text
