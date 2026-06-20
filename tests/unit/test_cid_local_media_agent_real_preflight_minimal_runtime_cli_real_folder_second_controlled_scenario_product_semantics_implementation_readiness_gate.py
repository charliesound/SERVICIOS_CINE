from pathlib import Path

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

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.IMPLEMENTATION.READINESS.GATE.V1"


def read(path):
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_readiness_doc_exists_and_names_phase():
    text = read(READINESS_DOC)
    assert PHASE in text
    assert "Product Semantics Implementation Readiness Gate v1" in text


def test_readiness_gate_depends_on_decision_record_qa_gate():
    readiness_text = read(READINESS_DOC)
    qa_text = read(QA_DOC)

    assert "PRODUCT.SEMANTICS.DECISION.RECORD.QA.GATE.V1" in readiness_text
    assert "PRODUCT_SEMANTICS_DECISION_RECORD_QA_GATE_PASS_DOCUMENTED_ONLY" in readiness_text
    assert "PRODUCT_SEMANTICS_DECISION_RECORD_QA_GATE_PASS_DOCUMENTED_ONLY" in qa_text


def test_selected_product_semantics_remain_non_media_rejected():
    readiness_text = read(READINESS_DOC)
    decision_text = read(DECISION_DOC)

    for text in [readiness_text, decision_text]:
        assert "NON_MEDIA_REJECTED" in text

    assert "`selected_product_semantics`: `NON_MEDIA_REJECTED`" in decision_text
    assert "`selected_product_behavior`: `NON_MEDIA_REJECTED`" in decision_text


def test_selected_behavior_scope_remains_documented_only():
    readiness_text = read(READINESS_DOC)
    decision_text = read(DECISION_DOC)

    assert "`selected_product_behavior_scope`: `DOCUMENTED_ONLY_NOT_IMPLEMENTED`" in readiness_text
    assert "`selected_product_behavior_scope`: `DOCUMENTED_ONLY_NOT_IMPLEMENTED`" in decision_text


def test_readiness_result_does_not_authorize_implementation():
    text = read(READINESS_DOC)
    assert "PRODUCT_SEMANTICS_IMPLEMENTATION_READINESS_GATE_PASS_NO_IMPLEMENTATION_AUTHORIZED" in text
    assert "This readiness gate does not authorize implementation." in text
    assert "Implementation remains unauthorized." in text


def test_readiness_gate_does_not_change_runtime_scanner_report_or_cli():
    text = read(READINESS_DOC)
    assert "does not change scanner behavior, runtime behavior, report behavior, or CLI behavior" in text
    for required in [
        "`runtime_change_authorized`: `false`",
        "`scanner_change_authorized`: `false`",
        "`report_change_authorized`: `false`",
        "`cli_change_authorized`: `false`",
        "`implementation_authorized`: `false`",
    ]:
        assert required in text


def test_no_allowed_runtime_scanner_report_or_cli_files_are_defined():
    text = read(READINESS_DOC)
    for required in [
        "This readiness gate defines no allowed runtime files.",
        "This readiness gate defines no allowed scanner files.",
        "This readiness gate defines no allowed report files.",
        "This readiness gate defines no allowed CLI files.",
    ]:
        assert required in text


def test_later_implementation_phase_must_define_boundaries():
    text = read(READINESS_DOC)
    for required in [
        "exact runtime files allowed to change",
        "exact scanner behavior allowed to change",
        "exact report behavior allowed to change",
        "exact CLI behavior allowed to change",
        "exact tests proving the change",
        "rollback boundary",
        "privacy boundary",
        "no media-probing boundary unless separately authorized",
    ]:
        assert required in text


def test_observation_counts_are_preserved():
    readiness_text = read(READINESS_DOC)
    decision_text = read(DECISION_DOC)

    for required in [
        "accepted_extension_counts=.mov:1,.wav:1",
        "rejected_extension_counts=.exe:1,.txt:1",
        "ignored_extension_counts={}",
    ]:
        assert required in readiness_text
        assert required in decision_text


def test_txt_and_exe_remain_rejected_not_ignored():
    readiness_text = read(READINESS_DOC)
    decision_text = read(DECISION_DOC)

    for text in [readiness_text, decision_text]:
        assert ".txt` and `.exe` are classified as rejected" in text
        assert ".txt` and `.exe` are not classified as ignored" in text


def test_non_media_rejected_interpretation_is_preserved():
    text = read(READINESS_DOC)
    assert "For this controlled scenario, `.txt` and `.exe` are non-media files." in text
    assert "They are not converted to ignored files by this gate." in text
    assert "remain rejected in the controlled evidence" in text


def test_no_client_facing_or_clean_pass_claims_are_authorized():
    text = read(READINESS_DOC)
    for required in [
        "`client_facing_classification_claim`: `NONE`",
        "`clean_classification_pass_claim`: `NONE`",
        "Client-facing claims remain unauthorized.",
        "Clean classification PASS claims remain unauthorized.",
    ]:
        assert required in text


def test_behavior_changes_remain_blocked():
    text = read(READINESS_DOC)
    for blocked in [
        "scanner behavior changes",
        "runtime behavior changes",
        "report behavior changes",
        "CLI behavior changes",
    ]:
        assert blocked in text


def test_media_processing_and_saas_scopes_remain_blocked():
    text = read(READINESS_DOC)
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


def test_required_next_gate_before_implementation_is_named():
    text = read(READINESS_DOC)
    assert "Required next gate before implementation" in text
    assert "PRODUCT.SEMANTICS.IMPLEMENTATION.AUTHORIZATION.GATE.V1" in text
    assert "must pass a separate implementation authorization gate" in text


def test_phase_is_docs_test_only():
    text = read(READINESS_DOC)
    assert "This phase is docs/test-only." in text
    assert "No runtime code, scanner code, report code, CLI code, SaaS code, database code, infrastructure code, or media-processing code may be changed by this phase." in text


def test_gate_result_is_pass_but_implementation_remains_unauthorized():
    text = read(READINESS_DOC)
    assert "`PASS`" in text
    assert "Implementation readiness is documented." in text
    assert "Implementation remains unauthorized." in text
