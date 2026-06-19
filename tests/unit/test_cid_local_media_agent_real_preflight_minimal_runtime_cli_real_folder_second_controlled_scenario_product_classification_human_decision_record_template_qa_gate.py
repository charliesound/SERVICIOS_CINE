from pathlib import Path

QA_DOC = Path('docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_record_template_qa_gate_v1.md')
TEMPLATE_DOC = Path('docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_record_template_v1.md')
TEMPLATE_TEST = Path('tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_record_template.py')
READINESS_DOC = Path('docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_readiness_gate_v1.md')
READINESS_TEST = Path('tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_readiness_gate.py')

def qa_text():
    return QA_DOC.read_text(encoding='utf-8')

def template_text():
    return TEMPLATE_DOC.read_text(encoding='utf-8')

def test_template_qa_gate_document_exists():
    assert QA_DOC.exists()

def test_template_qa_gate_depends_on_upstream_artifacts():
    assert TEMPLATE_DOC.exists()
    assert TEMPLATE_TEST.exists()
    assert READINESS_DOC.exists()
    assert READINESS_TEST.exists()

def test_template_qa_gate_links_to_stable_upstream_baseline():
    t = qa_text()
    assert '1d57a273dbe611b9362d19a01e9b0b736ff83cf5' in t
    assert 'human-decision-record-template-v1-20260619' in t
    assert 'PRODUCT.CLASSIFICATION.HUMAN.DECISION.RECORD.TEMPLATE.V1' in t

def test_template_qa_gate_declares_pass_with_no_option_selected():
    t = qa_text()
    assert 'HUMAN_DECISION_RECORD_TEMPLATE_QA_GATE_PASS_WITH_NO_PRODUCT_OPTION_SELECTED' in t
    assert 'HUMAN_DECISION_RECORD_TEMPLATE_READY_WITH_NO_PRODUCT_OPTION_SELECTED' in t
    assert 'PRODUCT_CLASSIFICATION_DECISION_REQUIRED' in t

def test_template_qa_gate_preserves_evidence_metrics():
    t = qa_text()
    for item in ['controlled_execution_status=PREFLIGHT_PASS','cli_exit_code=0','leak_check_exit_code=0','media_file_count=2','accepted_extension_counts=.mov:1,.wav:1','ignored_extension_counts={}']:
        assert item in t
    assert 'rejected_extension_counts=.exe:1,.txt:1' in t
    assert 'maximum_detected_scan_depth=3' in t
    assert 'total_selected_media_size_bucket=LE_100MB' in t

def test_template_qa_gate_validates_template_has_human_placeholders():
    t = template_text()
    for field in ['decision_record_status','decision_owner','decision_date','selected_product_semantics','decision_scope','user_visible_behavior','report_visible_behavior','log_visible_behavior','runtime_change_required','qa_gate_required_before_runtime_change','client_facing_claims_allowed','migration_or_compatibility_notes','decision_rationale','evidence_reference','known_limitations']:
        assert field in t
        assert f'{field}=TO_BE_FILLED_BY_HUMAN' in t

def test_template_qa_gate_keeps_allowed_values_as_future_options_only():
    q = qa_text()
    t = template_text()
    for value in ['NON_MEDIA_REJECTED','NON_MEDIA_IGNORED','NON_MEDIA_SEPARATE_CATEGORY','NON_MEDIA_POLICY_CONFIGURABLE','OTHER_NAMED_PRODUCT_BEHAVIOR']:
        assert value in q
        assert value in t
    assert 'This template does not choose any of these values.' in t

def test_template_qa_gate_blocks_filling_and_selection():
    t = qa_text()
    assert 'No downstream phase may fill the human decision record based only on this QA gate.' in t
    assert 'No downstream phase may select final product semantics based only on this QA gate.' in t
    assert 'Filling the human decision record.' in t
    assert 'Selecting final product semantics.' in t

def test_template_qa_gate_blocks_client_claims_and_clean_pass():
    t = qa_text()
    assert 'No downstream phase may claim clean classification pass based only on this QA gate.' in t
    assert 'No downstream phase may make client-facing claims based only on this QA gate.' in t

def test_template_qa_gate_blocks_runtime_scanner_report_cli_changes():
    t = qa_text()
    for item in ['No downstream phase may change scanner behavior based only on this QA gate.','No downstream phase may change runtime behavior based only on this QA gate.','No downstream phase may change report behavior based only on this QA gate.','No downstream phase may change CLI behavior based only on this QA gate.']:
        assert item in t

def test_template_qa_gate_keeps_out_of_scope_surfaces_blocked():
    t = qa_text()
    for item in ['Runtime code changes.','Scanner behavior changes.','CLI behavior changes.','Report behavior changes.','FFmpeg or ffprobe execution.','Media probing or decoding.','Real client media.','Personal data processing.','SaaS application changes.','Database changes.','Docker changes.','Alembic changes.','Stripe, AI Jobs, credits, or ledger changes.']:
        assert item in t
