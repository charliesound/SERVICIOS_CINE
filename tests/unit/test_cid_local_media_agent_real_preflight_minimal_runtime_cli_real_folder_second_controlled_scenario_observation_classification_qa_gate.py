from pathlib import Path


QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_qa_gate_v1.md"
)

CONTRACT_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract_v1.md"
)

CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract.py"
)


def _qa_doc() -> str:
    return QA_GATE_DOC_PATH.read_text(encoding="utf-8")


def _contract_doc() -> str:
    return CONTRACT_DOC_PATH.read_text(encoding="utf-8")


def test_observation_classification_qa_gate_document_exists():
    assert QA_GATE_DOC_PATH.exists()


def test_observation_classification_qa_gate_depends_on_upstream_contract_artifacts():
    assert CONTRACT_DOC_PATH.exists()
    assert CONTRACT_TEST_PATH.exists()


def test_observation_classification_qa_gate_links_to_stable_contract_baseline():
    text = _qa_doc()

    assert "252d7b4de89cd8ea3374b0e7e4f54223d71cd254" in text
    assert (
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-"
        "second-controlled-scenario-observation-classification-contract-v1-20260619"
    ) in text
    assert (
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER."
        "SECOND.CONTROLLED.SCENARIO.OBSERVATION.CLASSIFICATION.CONTRACT.V1"
    ) in text


def test_observation_classification_qa_gate_declares_active_observation_result():
    text = _qa_doc()

    assert "QA_GATE_PASS_WITH_ACTIVE_OBSERVATION" in text
    assert "The observation remains active" in text
    assert "must not be converted into unconditional `PASS`" in text
    assert "must not be hidden by later QA language" in text


def test_observation_classification_qa_gate_preserves_contract_pass_with_observation():
    qa_text = _qa_doc()
    contract_text = _contract_doc()

    assert "PASS_WITH_OBSERVATION" in contract_text
    assert "PASS_WITH_OBSERVATION" in qa_text
    assert "does not convert `PASS_WITH_OBSERVATION` into unconditional `PASS`" in contract_text


def test_observation_classification_qa_gate_preserves_execution_metrics():
    qa_text = _qa_doc()
    contract_text = _contract_doc()

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
        assert metric in qa_text
        assert metric in contract_text


def test_observation_classification_qa_gate_preserves_rejected_not_ignored_facts():
    qa_text = _qa_doc()
    contract_text = _contract_doc()

    assert ".txt` and `.exe` were classified as rejected" in qa_text
    assert ".txt` and `.exe` were not classified as ignored" in qa_text
    assert "`ignored_extension_counts` remained empty" in qa_text

    assert ".txt` was classified as rejected" in contract_text
    assert ".exe` was classified as rejected" in contract_text
    assert "`.txt` and `.exe` were not classified as ignored" in contract_text


def test_observation_classification_qa_gate_separates_privacy_boundary_from_classification_semantics():
    qa_text = _qa_doc()
    contract_text = _contract_doc()

    assert "This is not a privacy failure" in qa_text
    assert "This is not a sanitization failure" in qa_text
    assert "This is not an execution boundary failure" in qa_text
    assert "classification semantics observation" in qa_text

    assert "not a failure of privacy, sanitization, or execution boundary guarantees" in contract_text
    assert "classification semantics, not media leakage" in contract_text


def test_observation_classification_qa_gate_keeps_product_semantics_undecided():
    qa_text = _qa_doc()
    contract_text = _contract_doc()

    assert "Product semantics for ignored versus rejected remain undecided" in qa_text
    assert "Ignored versus rejected product semantics remain undecided" in qa_text

    assert "Product behavior for ignored versus rejected extensions remains undecided" in contract_text
    assert "does not decide that rejected is the final product behavior" in contract_text
    assert "does not decide that ignored is the final product behavior" in contract_text


def test_observation_classification_qa_gate_requires_future_product_contract_for_client_claims():
    qa_text = _qa_doc()
    contract_text = _contract_doc()

    assert "A future product classification contract is required" in qa_text
    assert "before making client-facing claims" in qa_text

    assert "A future product classification contract is required" in contract_text
    assert "Any client-facing claim about ignored or rejected extension behavior requires a separate product contract" in contract_text


def test_observation_classification_qa_gate_blocks_clean_classification_pass_without_future_contract():
    text = _qa_doc()

    assert "blocks any future phase from claiming a clean pass for extension classification" in text
    assert "unless a later authorized product classification contract explicitly resolves ignored versus rejected behavior" in text
    assert "It only blocks misrepresentation of the classification semantics" in text


def test_observation_classification_qa_gate_does_not_block_validated_boundary_result():
    text = _qa_doc()

    assert "does not block the already validated preflight, privacy, leak-check, and boundary result" in text
    assert "The controlled scenario remains passed for preflight, privacy, and boundary purposes" in text


def test_observation_classification_qa_gate_keeps_runtime_and_media_processing_out_of_scope():
    text = _qa_doc()

    forbidden_scope_items = [
        "Runtime code changes",
        "Scanner behavior changes",
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


def test_observation_classification_qa_gate_keeps_saas_and_financial_surfaces_out_of_scope():
    text = _qa_doc()

    forbidden_scope_items = [
        "SaaS application changes",
        "Database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe, AI Jobs, credits, or ledger changes",
    ]

    for item in forbidden_scope_items:
        assert item in text


def test_observation_classification_qa_gate_completion_criteria_are_bounded():
    text = _qa_doc()

    assert "The staged diff contains only this QA gate document and its unit test" in text
    assert "Repository guards pass" in text
    assert "The QA gate validates `QA_GATE_PASS_WITH_ACTIVE_OBSERVATION`" in text
