from pathlib import Path

DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_classification_human_decision_record_fill_authorization_gate_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.CLASSIFICATION.HUMAN.DECISION.RECORD.FILL.AUTHORIZATION.GATE.V1"


def read_doc():
    assert DOC.exists()
    return DOC.read_text(encoding="utf-8")


def test_doc_exists_and_names_phase():
    text = read_doc()
    assert PHASE in text
    assert "Human Decision Record Fill Authorization Gate v1" in text


def test_authorizes_only_future_filled_record_creation():
    text = read_doc()
    assert "The next phase may create a filled human decision record." in text
    assert "It does not authorize selecting product semantics." in text


def test_preserves_no_product_option_selected_status():
    text = read_doc()
    assert "HUMAN_DECISION_RECORD_FILL_AUTHORIZATION_GATE_PASS_WITH_NO_PRODUCT_OPTION_SELECTED" in text
    assert "HUMAN_DECISION_RECORD_TEMPLATE_READY_WITH_NO_PRODUCT_OPTION_SELECTED" in text
    assert "HUMAN_DECISION_RECORD_TEMPLATE_QA_GATE_PASS_WITH_NO_PRODUCT_OPTION_SELECTED" in text


def test_keeps_product_classification_decision_required():
    text = read_doc()
    assert "PRODUCT_CLASSIFICATION_DECISION_REQUIRED" in text


def test_keeps_observation_as_product_semantics_only():
    text = read_doc()
    assert "product semantics observation only" in text
    assert "not a privacy, sanitization, leak-check, execution-boundary, scanner, ffprobe, runtime, report, or CLI failure" in text


def test_preserves_rejected_not_ignored_evidence():
    text = read_doc()
    assert "rejected_extension_counts=.exe:1,.txt:1" in text
    assert "ignored_extension_counts={}" in text
    assert "They are not classified as ignored." in text


def test_does_not_claim_selected_final_product_semantics():
    text = read_doc()
    forbidden_claims = [
        "selected product behavior: NON_MEDIA_REJECTED",
        "selected product behavior: NON_MEDIA_IGNORED",
        "selected product behavior: NON_MEDIA_SEPARATE_CATEGORY",
        "selected product behavior: NON_MEDIA_POLICY_CONFIGURABLE",
        "selected product behavior: OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]
    for claim in forbidden_claims:
        assert claim not in text


def test_lists_all_non_authorized_product_options():
    text = read_doc()
    for option in [
        "NON_MEDIA_REJECTED",
        "NON_MEDIA_IGNORED",
        "NON_MEDIA_SEPARATE_CATEGORY",
        "NON_MEDIA_POLICY_CONFIGURABLE",
        "OTHER_NAMED_PRODUCT_BEHAVIOR",
    ]:
        assert option in text


def test_blocks_behavior_changes_and_client_facing_claims():
    text = read_doc()
    for phrase in [
        "no scanner behavior change",
        "no runtime behavior change",
        "no report behavior change",
        "no CLI behavior change",
        "no client-facing claim",
        "no clean classification PASS claim",
    ]:
        assert phrase in text


def test_is_docs_test_only():
    text = read_doc()
    assert "This phase is docs/test-only." in text


def test_excludes_runtime_and_media_processing_scopes():
    text = read_doc()
    for forbidden_scope in [
        "runtime",
        "scanner",
        "CLI",
        "ffprobe",
        "ffmpeg",
        "media probing",
        "media decoding",
        "report generation",
        "transcription",
        "translation",
        "subtitles",
        "sync",
        "NLE export",
        "SaaS backend",
        "SaaS frontend",
        "database",
        "Docker",
        "Alembic",
        "Stripe",
        "AI Jobs",
        "credits",
        "ledger",
    ]:
        assert forbidden_scope in text
