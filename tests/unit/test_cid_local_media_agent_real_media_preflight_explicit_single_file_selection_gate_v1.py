from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_explicit_single_file_selection_gate_v1.md"
)

SELECTION_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_explicit_single_file_selection_readiness_gate_v1.md"
)

CONTROLLED_EXECUTION_DOC = Path(
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

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_selection_gate_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.EXPLICIT_SINGLE_FILE_SELECTION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_EXPLICIT_SINGLE_FILE_SELECTION_GATE_V1_CLOSED" in text
    assert "READY_FOR_EXPLICIT_SINGLE_FILE_SELECTION_GATE" in text
    assert "EXPLICIT_SINGLE_FILE_SELECTION_DEFERRED_PENDING_SANITIZED_LOCAL_FILE_CANDIDATE" in text


def test_selection_gate_records_base_state() -> None:
    text = _text()

    assert "60dd98656af581d9dc7ca9b274471e93974077f4" in text
    assert "60dd986 docs: add CID Local Media Agent explicit single file selection readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-explicit-single-file-selection-readiness-gate-v1-20260702" in text


def test_selection_gate_references_upstream_documents() -> None:
    text = _text()

    assert SELECTION_READINESS_DOC.exists()
    assert CONTROLLED_EXECUTION_DOC.exists()
    assert READINESS_DOC.exists()
    assert PLANNING_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_explicit_single_file_selection_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_planning_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_selection_gate_does_not_select_or_execute_anything() -> None:
    text = _text()

    markers = [
        "This gate does not select a real file.",
        "This gate does not record a real file path.",
        "This gate does not record a real filename.",
        "This gate does not stat a real file.",
        "This gate does not open a real file.",
        "This gate does not execute real media.",
        "This gate does not request customer media.",
        "This gate does not process customer media.",
        "This gate does not run FFmpeg.",
        "This gate does not run ffprobe.",
        "This gate does not run scanner behavior.",
    ]

    for marker in markers:
        assert marker in text


def test_selection_gate_explains_safe_deferral() -> None:
    text = _text()

    markers = [
        "A selection gate must not fabricate a file path.",
        "A selection gate must not silently choose a file.",
        "A selection gate must not record sensitive paths in committed artifacts.",
        "A selection gate must not record customer or project-identifying filenames in committed artifacts.",
        "A selection gate must stop if no explicit eligible sanitized candidate exists.",
        "Deferring selection is the correct safe decision when the required candidate is missing.",
    ]

    for marker in markers:
        assert marker in text


def test_selection_gate_records_decision_fields() -> None:
    text = _text()

    fields = [
        "SELECTION_DECISION_RECORD_ID:",
        "explicit_single_file_selection_deferred_v1",
        "SELECTION_RECORD_TYPE:",
        "selection_decision_no_real_file_selected",
        "SELECTION_DECISION:",
        "DEFERRED_NO_EXPLICIT_SANITIZED_ELIGIBLE_LOCAL_FILE_CANDIDATE",
        "SELECTION_STATUS:",
        "NOT_SELECTED",
        "SELECTION_ALLOWED:",
        "no",
        "SELECTION_ATTEMPTED:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_selection_gate_records_no_file_no_customer_no_dependency() -> None:
    text = _text()

    fields = [
        "REAL_FILE_SELECTED:",
        "no",
        "REAL_FILE_PATH_RECORDED:",
        "no",
        "REAL_FILENAME_RECORDED:",
        "no",
        "REAL_FILE_STAT_RUN:",
        "no",
        "REAL_FILE_OPEN_RUN:",
        "no",
        "CUSTOMER_FILE_SELECTED:",
        "no",
        "CUSTOMER_MEDIA_USED:",
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


def test_selection_gate_records_deferral_reasons() -> None:
    text = _text()

    reasons = [
        "No explicit sanitized local file candidate has been provided.",
        "No material owner has been confirmed.",
        "No confidentiality status has been confirmed.",
        "No redacted input token has been approved.",
        "No generic file category has been approved.",
        "No output path has been approved for later execution.",
        "No execution gate has been approved after selection.",
    ]

    for reason in reasons:
        assert reason in text


def test_selection_gate_defines_required_candidate_before_selection() -> None:
    text = _text()

    requirements = [
        "One explicit local file candidate.",
        "Confirmation that the candidate is a file, not a folder.",
        "Confirmation that the candidate is not recursive.",
        "Confirmation that the candidate is not a wildcard.",
        "Confirmation that the candidate is not a glob pattern.",
        "Confirmation that the candidate is not a batch list.",
        "Confirmation that the candidate is operator-owned or explicitly approved.",
        "Confirmation that the candidate is non-confidential.",
        "Confirmation that the candidate is not customer material unless later written scope exists.",
        "Confirmation that no absolute path will be committed.",
        "Confirmation that no sensitive filename will be committed.",
        "Confirmation that a placeholder selection id will be used.",
        "Confirmation that a redacted input token will be used.",
        "Confirmation that a generic file category will be used.",
        "Confirmation that source policy remains read-only.",
        "Confirmation that no upload will occur.",
        "Confirmation that no execution is requested inside the selection gate.",
    ]

    for requirement in requirements:
        assert requirement in text


def test_selection_gate_defines_deferred_boundary() -> None:
    text = _text()

    markers = [
        "The gate is closed as a safe selection decision record.",
        "selection is not allowed without an explicit sanitized eligible local file candidate",
        "The gate does not claim a real file was selected.",
        "The gate does not claim a real path was validated.",
        "The gate does not claim a real filename was accepted.",
        "The gate does not claim media readiness.",
        "The gate does not claim real-media execution readiness.",
        "The gate does not claim production readiness.",
    ]

    for marker in markers:
        assert marker in text


def test_selection_gate_records_validated_and_not_validated_scope() -> None:
    text = _text()

    validated = [
        "Explicit file selection cannot proceed without a sanitized eligible candidate.",
        "The safe stop condition works.",
        "The selection readiness policy is respected.",
        "No file path is invented.",
        "No filename is invented.",
        "No real file is touched.",
        "No dependency command is run.",
        "No customer data is captured.",
        "No production claim is made.",
    ]
    not_validated = [
        "Real file existence.",
        "Real file readability.",
        "Real file ownership.",
        "Real file confidentiality.",
        "Real file extension.",
        "Real file size.",
        "Real media metadata.",
        "Real FFmpeg behavior.",
        "Real ffprobe behavior.",
        "Real scanner behavior.",
        "Real output report from media.",
        "Real dependency availability.",
    ]

    for marker in validated + not_validated:
        assert marker in text


def test_selection_gate_defines_next_step_and_candidate_record_requirements() -> None:
    text = _text()

    markers = [
        "Provide or define a sanitized single-file candidate record in a separate gate.",
        "The record must use a placeholder selection id.",
        "The record must use a redacted path token.",
        "The record must use a generic file category.",
        "The record must not commit the real absolute path.",
        "The record must not commit a sensitive filename.",
        "The record must not execute, open, or stat the file unless later explicitly approved.",
        "Selection id.",
        "Redacted input token.",
        "Generic file category.",
        "Material owner category.",
        "Confidentiality confirmation.",
        "Single-file confirmation.",
        "Source read-only confirmation.",
        "Network no-upload confirmation.",
        "Execution-not-requested confirmation.",
    ]

    for marker in markers:
        assert marker in text


def test_selection_gate_confirms_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop because no explicit sanitized eligible local file candidate exists.",
        "Stop because no material owner is confirmed.",
        "Stop because no confidentiality status is confirmed.",
        "Stop because no redacted input token is approved.",
        "Stop because no generic file category is approved.",
        "Stop because no output path is approved for later execution.",
        "Stop because no real file selection should be invented.",
        "Stop because no real path should be committed.",
        "Stop because no real filename should be committed.",
        "Stop because no customer material is allowed.",
        "Stop because no dependency execution is allowed.",
        "Stop because no implementation change is allowed.",
        "Stop because no scanner behavior is allowed.",
    ]

    for condition in conditions:
        assert condition in text


def test_selection_gate_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Explicit single-file selection gate phase is defined.",
        "Base state is recorded.",
        "Selection readiness gate is referenced.",
        "Controlled execution gate is referenced.",
        "Real-media preflight readiness gate is referenced.",
        "Real-media preflight planning gate is referenced.",
        "Production path scope gate is referenced.",
        "Selection decision record id is present.",
        "Selection record type is no real file selected.",
        "Selection decision is deferred.",
        "Selection status is not selected.",
        "Selection allowed is no.",
        "Selection attempted is no.",
        "Real file selected is no.",
        "Real file path recorded is no.",
        "Real filename recorded is no.",
        "Real file stat run is no.",
        "Real file open run is no.",
        "Customer file selected is no.",
        "Customer media used is no.",
        "Dependency command run is no.",
        "FFmpeg run is no.",
        "ffprobe run is no.",
        "Scanner run is no.",
        "Deferral reason is explicit.",
        "Required candidate before selection is explicit.",
        "Deferred selection boundary is explicit.",
        "Validated scope is explicit.",
        "Non-validated scope is explicit.",
        "Safe next step is explicit.",
        "Next candidate record requirements are explicit.",
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


def test_selection_gate_keeps_limitations_and_safety_active() -> None:
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
        "No real file path is recorded in this gate.",
        "No real filename is recorded in this gate.",
        "No real file stat is run in this gate.",
        "No real file open is run in this gate.",
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


def test_selection_gate_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this explicit single-file selection decision document.",
        "Add one explicit single-file selection decision unit test.",
        "Inspect existing explicit single-file selection readiness document.",
        "Inspect existing real-media preflight controlled execution document.",
        "Inspect existing real-media preflight readiness document.",
        "Inspect existing real-media preflight planning document.",
        "Inspect existing production use path scope document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No real-media execution.",
        "No real file selection.",
        "No real file path recording.",
        "No real filename recording.",
        "No real file stat.",
        "No real file open.",
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


def test_selection_gate_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_SINGLE_FILE_CANDIDATE.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_SANITIZED_SINGLE_FILE_CANDIDATE_READINESS_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent explicit single file selection gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-explicit-single-file-selection-gate-v1-20260702" in text
