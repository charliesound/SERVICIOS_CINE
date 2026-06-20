from pathlib import Path

AUTHORIZATION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_implementation_authorization_gate_v1.md"
)

READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_implementation_readiness_gate_v1.md"
)

QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_decision_record_qa_gate_v1.md"
)

DECISION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_decision_record_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.IMPLEMENTATION.AUTHORIZATION.GATE.V1"


def read(path):
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_authorization_doc_exists_and_names_phase():
    text = read(AUTHORIZATION_DOC)
    assert PHASE in text
    assert "Product Semantics Implementation Authorization Gate v1" in text


def test_authorization_depends_on_implementation_readiness_gate():
    authorization_text = read(AUTHORIZATION_DOC)
    readiness_text = read(READINESS_DOC)

    assert "PRODUCT.SEMANTICS.IMPLEMENTATION.READINESS.GATE.V1" in authorization_text
    assert "PRODUCT_SEMANTICS_IMPLEMENTATION_READINESS_GATE_PASS_NO_IMPLEMENTATION_AUTHORIZED" in authorization_text
    assert "PRODUCT_SEMANTICS_IMPLEMENTATION_READINESS_GATE_PASS_NO_IMPLEMENTATION_AUTHORIZED" in readiness_text


def test_authorization_depends_on_decision_record_qa_gate():
    authorization_text = read(AUTHORIZATION_DOC)
    qa_text = read(QA_DOC)

    assert "PRODUCT.SEMANTICS.DECISION.RECORD.QA.GATE.V1" in authorization_text
    assert "PRODUCT_SEMANTICS_DECISION_RECORD_QA_GATE_PASS_DOCUMENTED_ONLY" in authorization_text
    assert "PRODUCT_SEMANTICS_DECISION_RECORD_QA_GATE_PASS_DOCUMENTED_ONLY" in qa_text


def test_selected_product_semantics_remain_non_media_rejected():
    authorization_text = read(AUTHORIZATION_DOC)
    decision_text = read(DECISION_DOC)

    for text in [authorization_text, decision_text]:
        assert "NON_MEDIA_REJECTED" in text

    assert "`selected_product_semantics`: `NON_MEDIA_REJECTED`" in decision_text
    assert "`selected_product_behavior`: `NON_MEDIA_REJECTED`" in decision_text


def test_selected_behavior_scope_is_still_documented_only_before_later_implementation():
    authorization_text = read(AUTHORIZATION_DOC)
    decision_text = read(DECISION_DOC)

    assert "`selected_product_behavior_scope`: `DOCUMENTED_ONLY_NOT_IMPLEMENTED`" in authorization_text
    assert "`selected_product_behavior_scope`: `DOCUMENTED_ONLY_NOT_IMPLEMENTED`" in decision_text


def test_authorization_result_allows_only_separate_bounded_later_phase():
    text = read(AUTHORIZATION_DOC)
    assert "PRODUCT_SEMANTICS_IMPLEMENTATION_AUTHORIZATION_GATE_PASS_SEPARATE_BOUNDED_IMPLEMENTATION_PHASE_AUTHORIZED" in text
    assert "A later implementation phase is authorized only as a separate phase." in text
    assert "This current authorization gate does not implement anything." in text


def test_current_gate_is_docs_test_only_and_does_not_implement_behavior():
    text = read(AUTHORIZATION_DOC)
    assert "This gate is docs/test-only." in text
    assert "This gate does not implement behavior." in text
    assert "This gate does not change scanner behavior, runtime behavior, report behavior, or CLI behavior." in text


def test_later_implementation_scope_is_limited_to_non_media_product_semantics():
    text = read(AUTHORIZATION_DOC)
    assert "only address product semantics consistency for non-media files" in text
    for required in [
        ".txt` and `.exe` remain rejected",
        ".txt` and `.exe` are not converted to ignored",
        "ignored_extension_counts={}",
        "NON_MEDIA_REJECTED` remains the product semantics",
        "no client-facing clean classification claim is introduced",
    ]:
        assert required in text


def test_later_implementation_runtime_file_boundary_is_explicit_and_narrow():
    text = read(AUTHORIZATION_DOC)
    assert "`scripts/cid_media_agent_scan.py`" in text
    assert "the only runtime/scanner/CLI file that may be proposed for change" in text
    assert "No report file is authorized by this gate." in text
    assert "No SaaS file is authorized by this gate." in text
    assert "No database file is authorized by this gate." in text
    assert "No infrastructure file is authorized by this gate." in text


def test_later_implementation_test_boundary_is_defined():
    text = read(AUTHORIZATION_DOC)
    for required in [
        "non-media files remain rejected",
        "non-media files are not counted as ignored",
        "accepted media counts remain unchanged",
        "rejected extension counts preserve `.exe:1,.txt:1`",
        "`ignored_extension_counts={}` remains unchanged",
        "no clean classification PASS claim is emitted",
        "no client-facing classification claim is emitted",
        "no ffprobe or ffmpeg execution is introduced",
    ]:
        assert required in text


def test_observation_counts_are_preserved():
    authorization_text = read(AUTHORIZATION_DOC)
    decision_text = read(DECISION_DOC)

    for required in [
        "accepted_extension_counts=.mov:1,.wav:1",
        "rejected_extension_counts=.exe:1,.txt:1",
        "ignored_extension_counts={}",
    ]:
        assert required in authorization_text
        assert required in decision_text


def test_txt_and_exe_remain_rejected_not_ignored():
    authorization_text = read(AUTHORIZATION_DOC)
    decision_text = read(DECISION_DOC)

    for text in [authorization_text, decision_text]:
        assert ".txt` and `.exe` are classified as rejected" in text
        assert ".txt` and `.exe` are not classified as ignored" in text


def test_current_gate_preserves_claim_boundaries():
    text = read(AUTHORIZATION_DOC)
    for required in [
        "`client_facing_classification_claim`: `NONE`",
        "`clean_classification_pass_claim`: `NONE`",
        "`runtime_change_authorized_by_this_gate`: `false`",
        "`scanner_change_authorized_by_this_gate`: `false`",
        "`report_change_authorized_by_this_gate`: `false`",
        "`cli_change_authorized_by_this_gate`: `false`",
        "`implementation_performed_by_this_gate`: `false`",
    ]:
        assert required in text


def test_current_gate_blocks_behavior_changes_in_this_phase():
    text = read(AUTHORIZATION_DOC)
    for blocked in [
        "scanner behavior changes in this phase",
        "runtime behavior changes in this phase",
        "report behavior changes in this phase",
        "CLI behavior changes in this phase",
    ]:
        assert blocked in text


def test_media_processing_and_saas_scopes_remain_blocked_in_this_gate():
    text = read(AUTHORIZATION_DOC)
    for blocked_scope in [
        "scanner execution",
        "ffprobe execution",
        "ffmpeg execution",
        "media probing",
        "media decoding",
        "report generation",
        "transcription",
        "translation",
        "subtitles",
        "sync",
        "NLE export",
        "SaaS backend changes",
        "SaaS frontend changes",
        "database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe changes",
        "AI Jobs changes",
        "credits changes",
        "ledger changes",
    ]:
        assert blocked_scope in text


def test_required_next_phase_is_separate_bounded_implementation():
    text = read(AUTHORIZATION_DOC)
    assert "Required next phase" in text
    assert "PRODUCT.SEMANTICS.BOUNDED.IMPLEMENTATION.V1" in text
    assert "must be a separate implementation phase" in text


def test_later_phase_must_inspect_current_behavior_and_prefer_noop_if_already_valid():
    text = read(AUTHORIZATION_DOC)
    assert "must inspect current behavior before changing runtime code" in text
    assert "If current behavior already satisfies `NON_MEDIA_REJECTED`" in text
    assert "prefer a no-op implementation decision rather than unnecessary code changes" in text


def test_phase_scope_boundary_forbids_code_changes_now():
    text = read(AUTHORIZATION_DOC)
    assert "This phase is docs/test-only." in text
    assert "No runtime code, scanner code, report code, CLI code, SaaS code, database code, infrastructure code, or media-processing code may be changed by this phase." in text


def test_gate_result_is_pass_but_current_gate_still_has_no_implementation():
    text = read(AUTHORIZATION_DOC)
    assert "`PASS`" in text
    assert "A later separate bounded implementation phase is authorized." in text
    assert "Implementation in this gate remains unauthorized." in text
    assert "Client-facing claims remain unauthorized." in text
    assert "Clean classification PASS claims remain unauthorized." in text
