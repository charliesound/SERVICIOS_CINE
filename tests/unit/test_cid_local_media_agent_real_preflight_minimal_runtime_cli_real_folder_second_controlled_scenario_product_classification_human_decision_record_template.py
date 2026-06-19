from pathlib import Path

DOC = Path('docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_record_template_v1.md')
READINESS_DOC = Path('docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_readiness_gate_v1.md')
READINESS_TEST = Path('tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_readiness_gate.py')
DECISION_DOC = Path('docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate_v1.md')
DECISION_TEST = Path('tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate.py')

def text():
    return DOC.read_text(encoding='utf-8')

def test_template_document_exists():
    assert DOC.exists()

def test_upstream_artifacts_exist():
    assert READINESS_DOC.exists()
    assert READINESS_TEST.exists()
    assert DECISION_DOC.exists()
    assert DECISION_TEST.exists()

def test_links_to_stable_upstream_baseline():
    t = text()
    assert '6f69cdc9524d32ed7695eb915acb980bb6cc6138' in t
    assert 'human-decision-readiness-gate-v1-20260619' in t
    assert 'PRODUCT.CLASSIFICATION.HUMAN.DECISION.READINESS.GATE.V1' in t

def test_template_status_and_upstream_statuses():
    t = text()
    assert 'HUMAN_DECISION_RECORD_TEMPLATE_READY_WITH_NO_PRODUCT_OPTION_SELECTED' in t
    assert 'PRODUCT_CLASSIFICATION_DECISION_REQUIRED' in t
    assert 'HUMAN_DECISION_READINESS_GATE_PASS_WITH_PRODUCT_DECISION_REQUIRED' in t

def test_preserves_evidence_metrics():
    t = text()
    for item in ['controlled_execution_status=PREFLIGHT_PASS','cli_exit_code=0','leak_check_exit_code=0','media_file_count=2','accepted_extension_counts=.mov:1,.wav:1','ignored_extension_counts={}']:
        assert item in t
    assert 'rejected_extension_counts=.exe:1,.txt:1' in t
    assert 'maximum_detected_scan_depth=3' in t
    assert 'total_selected_media_size_bucket=LE_100MB' in t

def test_preserves_observation_without_failure_claim():
    t = text()
    assert '.txt and .exe were classified as rejected.' in t
    assert '.txt and .exe were not classified as ignored.' in t
    assert 'The observation is not a privacy failure.' in t
    assert 'The observation is not a sanitization failure.' in t
    assert 'The observation is not a leak-check failure.' in t
    assert 'The observation is not an execution boundary failure.' in t

def test_contains_required_record_fields():
    t = text()
    for field in ['decision_record_status','decision_owner','decision_date','selected_product_semantics','decision_scope','user_visible_behavior','report_visible_behavior','log_visible_behavior','runtime_change_required','qa_gate_required_before_runtime_change','client_facing_claims_allowed','migration_or_compatibility_notes','decision_rationale','evidence_reference','known_limitations']:
        assert field in t
        assert f'{field}=TO_BE_FILLED_BY_HUMAN' in t

def test_lists_allowed_future_values_without_selecting_one():
    t = text()
    for value in ['NON_MEDIA_REJECTED','NON_MEDIA_IGNORED','NON_MEDIA_SEPARATE_CATEGORY','NON_MEDIA_POLICY_CONFIGURABLE','OTHER_NAMED_PRODUCT_BEHAVIOR']:
        assert value in t
    assert 'This template does not choose any of these values.' in t

def test_blocks_downstream_claims_and_changes():
    t = text()
    for item in ['No downstream phase may claim clean classification pass.','No downstream phase may claim final ignored behavior.','No downstream phase may claim final rejected behavior.','No downstream phase may make client-facing claims about extension classification.','No downstream phase may change scanner behavior.','No downstream phase may change runtime behavior.','No downstream phase may change report behavior.','No downstream phase may change CLI behavior.']:
        assert item in t

def test_out_of_scope_surfaces_are_blocked():
    t = text()
    for item in ['Filling the human decision record.','Selecting final product semantics.','Runtime code changes.','Scanner behavior changes.','FFmpeg or ffprobe execution.','Media probing or decoding.','Real client media.','Personal data processing.','SaaS application changes.','Database changes.','Docker changes.','Alembic changes.','Stripe, AI Jobs, credits, or ledger changes.']:
        assert item in t
