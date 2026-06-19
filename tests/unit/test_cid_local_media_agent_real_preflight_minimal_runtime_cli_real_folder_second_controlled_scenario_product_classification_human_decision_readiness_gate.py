from pathlib import Path


READINESS_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_human_decision_readiness_gate_v1.md"
)

DECISION_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate_v1.md"
)

DECISION_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate.py"
)

OBSERVATION_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate_v1.md"
)

OBSERVATION_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate.py"
)


def _doc() -> str:
    return READINESS_GATE_DOC_PATH.read_text(encoding="utf-8")


def _decision_gate_doc() -> str:
    return DECISION_GATE_DOC_PATH.read_text(encoding="utf-8")


def _observation_qa_doc() -> str:
    return OBSERVATION_QA_GATE_DOC_PATH.read_text(encoding="utf-8")


def test_product_classification_human_decision_readiness_gate_document_exists():
    assert READINESS_GATE_DOC_PATH.exists()


def test_product_classification_human_decision_readiness_gate_depends_on_upstream_artifacts():
    assert DECISION_GATE_DOC_PATH.exists()
    assert DECISION_GATE_TEST_PATH.exists()
    assert OBSERVATION_QA_GATE_DOC_PATH.exists()
    assert OBSERVATION_QA_GATE_TEST_PATH.exists()


def test_product_classification_human_decision_readiness_gate_links_to_stable_upstream_baseline():
    text = _doc()

    assert "55296400c2f9ae8834f9fcaa31e1df23e0b00a6a" in text
    assert (
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-"
        "second-controlled-scenario-product-classification-decision-gate-v1-20260619"
    ) in text
    assert (
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER."
        "SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.DECISION.GATE.V1"
    ) in text


def test_product_classification_human_decision_readiness_gate_declares_readiness_result():
    text = _doc()

    assert "HUMAN_DECISION_READINESS_GATE_PASS_WITH_PRODUCT_DECISION_REQUIRED" in text
    assert "The evidence is ready for human/product review" in text
    assert "The product decision is still not made" in text


def test_product_classification_human_decision_readiness_gate_keeps_decision_required_active():
    text = _doc()
    decision_text = _decision_gate_doc()

    assert "PRODUCT_CLASSIFICATION_DECISION_REQUIRED" in text
    assert "PRODUCT_CLASSIFICATION_DECISION_REQUIRED" in decision_text
    assert "`PRODUCT_CLASSIFICATION_DECISION_REQUIRED` remains active" in text


def test_product_classification_human_decision_readiness_gate_preserves_controlled_execution_facts():
    text = _doc()

    required_metrics = [
        "controlled_execution_status=PREFLIGHT_PASS",
        "cli_exit_code=0",
        "leak_check_exit_code=0",
        "media_file_count=2",
        "accepted_extension_counts=.mov:1,.wav:1",
        "ignored_extension_counts={}",
        "rejected_extension_counts=.exe:1,.txt:1",
        "maximum_detected_scan_depth=3",
        "total_selected_media_size_bucket=LE_100MB",
    ]

    for metric in required_metrics:
        assert metric in text


def test_product_classification_human_decision_readiness_gate_preserves_observation_facts():
    text = _doc()

    required_facts = [
        ".mov` and `.wav` were accepted as media",
        ".txt` and `.exe` were classified as rejected",
        ".txt` and `.exe` were not classified as ignored",
        "`ignored_extension_counts` remained empty",
        "The observation concerns product classification semantics",
    ]

    for fact in required_facts:
        assert fact in text


def test_product_classification_human_decision_readiness_gate_separates_observation_from_failures():
    text = _doc()

    non_failures = [
        "The observation is not a privacy failure",
        "The observation is not a sanitization failure",
        "The observation is not a leak-check failure",
        "The observation is not an execution boundary failure",
    ]

    for non_failure in non_failures:
        assert non_failure in text


def test_product_classification_human_decision_readiness_gate_prepares_allowed_decision_options():
    text = _doc()

    options = [
        "Non-media files are rejected",
        "Non-media files are ignored",
        "Non-media files are classified into a separate category",
        "Non-media classification is configurable by policy",
        "Another named product behavior is required",
    ]

    for option in options:
        assert option in text


def test_product_classification_human_decision_readiness_gate_does_not_select_any_option():
    text = _doc()

    assert "This readiness gate does not select any option" in text
    assert "The product decision is still not made" in text


def test_product_classification_human_decision_readiness_gate_requires_decision_record_fields():
    text = _doc()

    required_fields = [
        "decision_owner",
        "decision_date",
        "selected_product_semantics",
        "decision_scope",
        "user_visible_behavior",
        "report_visible_behavior",
        "log_visible_behavior",
        "runtime_change_required",
        "qa_gate_required_before_runtime_change",
        "client_facing_claims_allowed",
        "migration_or_compatibility_notes",
        "decision_rationale",
        "evidence_reference",
        "known_limitations",
    ]

    for field in required_fields:
        assert field in text


def test_product_classification_human_decision_readiness_gate_requires_scope_questions():
    text = _doc()

    required_questions = [
        "Does the decision apply only to the second controlled scenario?",
        "Does the decision apply to the general Local Media Agent scanner product?",
        "Should `.txt` and `.exe` use the same classification behavior?",
        "Should harmless non-media files and risky executable files share the same category?",
        "Should rejected files be user-visible?",
        "Should ignored files be user-visible?",
        "Should separately classified files appear in reports?",
        "Should policy configuration be exposed to users or remain internal?",
        "Does the decision require runtime implementation?",
        "Does the decision require a separate QA gate before implementation?",
    ]

    for question in required_questions:
        assert question in text


def test_product_classification_human_decision_readiness_gate_blocks_downstream_claims_until_decision():
    text = _doc()

    blocked_claims = [
        "No downstream phase may claim clean classification pass",
        "No downstream phase may claim final ignored behavior",
        "No downstream phase may claim final rejected behavior",
        "No downstream phase may claim final separate-category behavior",
        "No downstream phase may claim final configurable-policy behavior",
        "No downstream phase may make client-facing claims about extension classification",
    ]

    for claim in blocked_claims:
        assert claim in text


def test_product_classification_human_decision_readiness_gate_blocks_behavior_changes_until_decision():
    text = _doc()

    blocked_changes = [
        "No downstream phase may change scanner behavior",
        "No downstream phase may change runtime behavior",
        "No downstream phase may change report behavior",
        "No downstream phase may change CLI behavior",
    ]

    for change in blocked_changes:
        assert change in text


def test_product_classification_human_decision_readiness_gate_explicitly_keeps_non_decision_state():
    text = _doc()

    non_decisions = [
        "That `.txt` should be ignored",
        "That `.txt` should be rejected",
        "That `.exe` should be ignored",
        "That `.exe` should be rejected",
        "That `.txt` and `.exe` should share the same category",
        "That `.txt` and `.exe` should use different categories",
        "That rejected is the preferred product behavior",
        "That ignored is the preferred product behavior",
        "That separate-category is the preferred product behavior",
        "That policy configuration is the preferred product behavior",
    ]

    for non_decision in non_decisions:
        assert non_decision in text


def test_product_classification_human_decision_readiness_gate_keeps_runtime_and_media_processing_out_of_scope():
    text = _doc()

    forbidden_scope_items = [
        "Runtime code changes",
        "Scanner behavior changes",
        "CLI behavior changes",
        "Report behavior changes",
        "FFmpeg or ffprobe execution",
        "Media probing or decoding",
        "Real client media",
        "Personal data processing",
        "Report generation",
        "Transcription",
        "Translation",
        "Subtitle generation",
        "Synchronization",
        "DaVinci Resolve, Avid, NLE, export, or upload workflows",
    ]

    for item in forbidden_scope_items:
        assert item in text


def test_product_classification_human_decision_readiness_gate_keeps_saas_and_financial_surfaces_out_of_scope():
    text = _doc()

    forbidden_scope_items = [
        "SaaS application changes",
        "Database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe, AI Jobs, credits, or ledger changes",
    ]

    for item in forbidden_scope_items:
        assert item in text


def test_product_classification_human_decision_readiness_gate_completion_criteria_are_bounded():
    text = _doc()

    assert "The staged diff contains only this readiness gate document and its unit test" in text
    assert "Repository guards pass" in text
    assert "The readiness gate validates `HUMAN_DECISION_READINESS_GATE_PASS_WITH_PRODUCT_DECISION_REQUIRED`" in text


def test_product_classification_human_decision_readiness_gate_is_consistent_with_decision_gate():
    text = _doc()
    decision_text = _decision_gate_doc()

    assert "This phase does not make the product decision" in text
    assert "This decision gate does not choose any of those options" in decision_text
    assert "No downstream phase may claim a clean classification pass" in decision_text


def test_product_classification_human_decision_readiness_gate_is_consistent_with_observation_qa_gate():
    text = _doc()
    qa_text = _observation_qa_doc()

    assert "The observation concerns product classification semantics" in text
    assert "QA_GATE_PASS_WITH_ACTIVE_OBSERVATION" in qa_text
    assert "Product semantics for ignored versus rejected remain undecided" in qa_text
