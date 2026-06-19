from pathlib import Path


DECISION_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_product_classification_decision_gate_v1.md"
)

OBSERVATION_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate_v1.md"
)

OBSERVATION_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate.py"
)

OBSERVATION_CONTRACT_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract_v1.md"
)

OBSERVATION_CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract.py"
)


def _doc() -> str:
    return DECISION_GATE_DOC_PATH.read_text(encoding="utf-8")


def _qa_gate_doc() -> str:
    return OBSERVATION_QA_GATE_DOC_PATH.read_text(encoding="utf-8")


def _contract_doc() -> str:
    return OBSERVATION_CONTRACT_DOC_PATH.read_text(encoding="utf-8")


def test_product_classification_decision_gate_document_exists():
    assert DECISION_GATE_DOC_PATH.exists()


def test_product_classification_decision_gate_depends_on_upstream_artifacts():
    assert OBSERVATION_QA_GATE_DOC_PATH.exists()
    assert OBSERVATION_QA_GATE_TEST_PATH.exists()
    assert OBSERVATION_CONTRACT_DOC_PATH.exists()
    assert OBSERVATION_CONTRACT_TEST_PATH.exists()


def test_product_classification_decision_gate_links_to_stable_upstream_baseline():
    text = _doc()

    assert "6f30152ef7ade860a18ef45d40828718a44a3598" in text
    assert (
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-"
        "second-controlled-scenario-observation-classification-qa-gate-v1-20260619"
    ) in text
    assert (
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER."
        "SECOND.CONTROLLED.SCENARIO.OBSERVATION.CLASSIFICATION.QA.GATE.V1"
    ) in text


def test_product_classification_decision_gate_requires_decision_status():
    text = _doc()

    assert "PRODUCT_CLASSIFICATION_DECISION_REQUIRED" in text
    assert "not authorized to finalize extension classification semantics yet" in text


def test_product_classification_decision_gate_preserves_active_observation():
    text = _doc()
    qa_text = _qa_gate_doc()

    assert "QA_GATE_PASS_WITH_ACTIVE_OBSERVATION" in text
    assert "QA_GATE_PASS_WITH_ACTIVE_OBSERVATION" in qa_text
    assert "The observation remains active" in qa_text


def test_product_classification_decision_gate_preserves_controlled_execution_facts():
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


def test_product_classification_decision_gate_preserves_rejected_not_ignored_observation():
    text = _doc()

    assert ".txt` and `.exe` were classified as rejected" in text
    assert ".txt` and `.exe` were not classified as ignored" in text
    assert "`ignored_extension_counts` remained empty" in text


def test_product_classification_decision_gate_keeps_privacy_and_boundary_results_valid():
    text = _doc()

    assert "did not violate privacy, sanitization, leak-check, or execution boundary guarantees" in text


def test_product_classification_decision_gate_lists_allowed_future_decision_shapes():
    text = _doc()

    expected_options = [
        "Non-media files are rejected",
        "Non-media files are ignored",
        "Non-media files are classified into a separate category",
        "Non-media classification is configurable by policy",
        "Non-media classification requires another named product behavior",
    ]

    for option in expected_options:
        assert option in text


def test_product_classification_decision_gate_does_not_choose_a_product_option():
    text = _doc()

    assert "This decision gate does not choose any of those options" in text
    assert "This gate explicitly does not decide" in text


def test_product_classification_decision_gate_blocks_clean_classification_pass():
    text = _doc()

    assert "No downstream phase may claim a clean classification pass" in text
    assert "until a later authorized product classification contract resolves ignored versus rejected behavior" in text


def test_product_classification_decision_gate_blocks_client_facing_claims():
    text = _doc()

    assert "No downstream phase may make client-facing claims about ignored or rejected extension behavior" in text
    assert "until that product classification contract exists" in text


def test_product_classification_decision_gate_blocks_runtime_behavior_changes():
    text = _doc()

    assert "No downstream phase may change scanner behavior, runtime behavior, reporting behavior, or CLI behavior" in text
    assert "based only on this decision gate" in text


def test_product_classification_decision_gate_explicitly_rejects_implicit_final_semantics():
    text = _doc()

    prohibited_final_claims = [
        "That `.txt` should be ignored",
        "That `.txt` should be rejected",
        "That `.exe` should be ignored",
        "That `.exe` should be rejected",
        "That rejected is better than ignored",
        "That ignored is better than rejected",
        "That the observed behavior is final product behavior",
        "That client-facing documentation can describe final ignored or rejected semantics",
    ]

    for claim in prohibited_final_claims:
        assert claim in text


def test_product_classification_decision_gate_requires_future_contract_constraints():
    text = _doc()

    required_constraints = [
        "It must distinguish evidence from product intent",
        "It must not pretend that the current observation already defines final product behavior",
        "It must state whether `.txt`, `.exe`, and other non-media files are ignored, rejected, separately classified, or policy-configured",
        "It must state whether the behavior is user-visible, report-visible, log-only, or internal-only",
        "It must state whether the behavior applies only to this controlled scenario or to the general scanner product",
        "It must state whether migration or compatibility concerns exist for previous reports",
        "It must state whether any runtime implementation phase is required",
        "It must require a separate QA gate before runtime behavior changes",
    ]

    for constraint in required_constraints:
        assert constraint in text


def test_product_classification_decision_gate_keeps_runtime_and_media_processing_out_of_scope():
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


def test_product_classification_decision_gate_keeps_saas_and_financial_surfaces_out_of_scope():
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


def test_product_classification_decision_gate_completion_criteria_are_bounded():
    text = _doc()

    assert "The staged diff contains only this decision gate document and its unit test" in text
    assert "Repository guards pass" in text
    assert "The decision gate validates `PRODUCT_CLASSIFICATION_DECISION_REQUIRED`" in text


def test_product_classification_decision_gate_remains_consistent_with_upstream_contract():
    text = _doc()
    contract_text = _contract_doc()

    assert "Product semantics for ignored versus rejected remain undecided" in text
    assert "Product behavior for ignored versus rejected extensions remains undecided" in contract_text
    assert "does not decide that rejected is the final product behavior" in contract_text
    assert "does not decide that ignored is the final product behavior" in contract_text
