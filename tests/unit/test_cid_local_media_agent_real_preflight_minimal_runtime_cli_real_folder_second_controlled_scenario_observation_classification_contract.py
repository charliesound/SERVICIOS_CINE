from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract_v1.md"
)

UPSTREAM_QA_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_post_execution_boundary_qa_gate_v1.md"
)

UPSTREAM_QA_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_post_execution_boundary_qa_gate.py"
)


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_observation_classification_contract_document_exists():
    assert DOC_PATH.exists()


def test_observation_classification_contract_links_to_stable_upstream_baseline():
    text = _doc()

    assert "6b34c8e565c08e9a771a5d25e4da352ca1356347" in text
    assert (
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-"
        "second-controlled-scenario-post-execution-boundary-qa-gate-v1-20260619"
    ) in text
    assert (
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER."
        "SECOND.CONTROLLED.SCENARIO.POST.EXECUTION.BOUNDARY.QA.GATE.V1"
    ) in text


def test_observation_classification_contract_depends_on_existing_upstream_artifacts():
    assert UPSTREAM_QA_DOC_PATH.exists()
    assert UPSTREAM_QA_TEST_PATH.exists()


def test_observation_classification_contract_preserves_pass_with_observation():
    text = _doc()

    assert "PASS_WITH_OBSERVATION" in text
    assert "does not convert `PASS_WITH_OBSERVATION` into unconditional `PASS`" in text
    assert "must not be silently normalized into a clean pass" in text


def test_observation_classification_contract_preserves_execution_result():
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


def test_observation_classification_contract_captures_rejected_not_ignored_observation():
    text = _doc()

    assert ".txt` was classified as rejected" in text
    assert ".exe` was classified as rejected" in text
    assert "`.txt` and `.exe` were not classified as ignored" in text
    assert "`ignored_extension_counts` remained empty" in text


def test_observation_classification_contract_keeps_privacy_result_separate_from_classification_semantics():
    text = _doc()

    assert "not a failure of privacy, sanitization, or execution boundary guarantees" in text
    assert "classification semantics, not media leakage" in text


def test_observation_classification_contract_does_not_freeze_product_semantics():
    text = _doc()

    assert "does not decide that rejected is the final product behavior" in text
    assert "does not decide that ignored is the final product behavior" in text
    assert "Product behavior for ignored versus rejected extensions remains undecided" in text


def test_observation_classification_contract_requires_future_product_contract():
    text = _doc()

    assert "A future product classification contract is required" in text
    assert "Any client-facing claim about ignored or rejected extension behavior requires a separate product contract" in text


def test_observation_classification_contract_blocks_runtime_changes():
    text = _doc()

    assert "does not change product behavior, runtime behavior, scanner behavior" in text
    assert "Any runtime change to classification behavior requires a separate authorized implementation phase" in text
    assert "It must not add product functionality" in text


def test_observation_classification_contract_keeps_scope_docs_and_unit_test_only():
    text = _doc()

    assert "documentation and unit-test only" in text
    assert "The staged diff contains only this document and its unit test" in text


def test_observation_classification_contract_keeps_media_processing_out_of_scope():
    text = _doc()

    forbidden_scope_items = [
        "Real client media",
        "Personal data processing",
        "Scanner execution",
        "Media probing or decoding",
        "FFmpeg or ffprobe execution",
        "Report generation",
        "Transcription",
        "Translation",
        "Subtitle generation",
        "Synchronization",
        "DaVinci Resolve, Avid, NLE, export, or upload workflows",
    ]

    for item in forbidden_scope_items:
        assert item in text


def test_observation_classification_contract_keeps_saas_and_financial_surfaces_out_of_scope():
    text = _doc()

    forbidden_scope_items = [
        "SaaS application changes",
        "Database changes",
        "Billing, credit, or ledger changes",
        "Any runtime code change",
    ]

    for item in forbidden_scope_items:
        assert item in text
