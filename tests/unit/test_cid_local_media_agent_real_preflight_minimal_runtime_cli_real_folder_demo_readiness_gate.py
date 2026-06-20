from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_readiness_gate_v1.md"
)

BOUNDED_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_bounded_implementation_qa_gate_v1.md"
)

BOUNDED_IMPL_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_bounded_implementation_v1.md"
)

SCANNER_SCRIPT = Path("scripts/cid_media_agent_scan.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.READINESS.GATE.V1"


def read(path: Path) -> str:
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_demo_readiness_doc_exists_and_names_phase():
    text = read(DOC)
    assert PHASE in text
    assert "Real Folder Demo Readiness Gate v1" in text


def test_demo_readiness_depends_on_bounded_implementation_qa_gate():
    text = read(DOC)
    qa_text = read(BOUNDED_QA_DOC)

    assert "PRODUCT.SEMANTICS.BOUNDED.IMPLEMENTATION.QA.GATE.V1" in text
    assert "PRODUCT_SEMANTICS_BOUNDED_IMPLEMENTATION_QA_GATE_PASS" in text
    assert "PRODUCT_SEMANTICS_BOUNDED_IMPLEMENTATION_QA_GATE_PASS" in qa_text


def test_demo_readiness_result_is_controlled_local_synthetic_only():
    text = read(DOC)
    assert "LOCAL_MEDIA_AGENT_DEMO_READINESS_GATE_PASS_CONTROLLED_LOCAL_SYNTHETIC_ONLY" in text
    assert "controlled local technical demo preparation" in text


def test_readiness_gate_is_not_the_demo_and_does_not_execute_scanner():
    text = read(DOC)
    for required in [
        "This readiness gate is not the demo itself.",
        "This readiness gate does not execute the scanner.",
        "This readiness gate does not create demo media.",
        "This readiness gate does not use real client material.",
        "This readiness gate is docs/test-only.",
    ]:
        assert required in text


def test_current_demo_ready_capabilities_are_declared():
    text = read(DOC)
    for required in [
        "local-only folder scan",
        "sanitized local path policy",
        "scanner-safe output folders",
        "JSON summary output",
        "processing status output",
        "media catalog output",
        "accepted media extension counts",
        "rejected non-media extension counts",
        "ignored extension counts remaining empty",
    ]:
        assert required in text


def test_non_media_rejected_demo_capability_is_preserved():
    text = read(DOC)
    impl_text = read(BOUNDED_IMPL_DOC)

    for required in [
        "`.mov` and `.wav` accepted as media",
        "`.txt` and `.exe` rejected as non-media",
        "rejected non-media files excluded from the media catalog",
        "legacy `UNKNOWN` synthetic placeholder `.txt` still requiring human review",
    ]:
        assert required in text

    assert "PRODUCT_SEMANTICS_BOUNDED_IMPLEMENTATION_PASS_NON_MEDIA_REJECTED" in impl_text


def test_demo_material_boundary_allows_only_synthetic_placeholders():
    text = read(DOC)
    for required in [
        "synthetic placeholder files",
        "local temporary folders",
        "sanitized folder names",
        "fake project names",
        "fake clip names",
        "fake media placeholders created for testing",
    ]:
        assert required in text


def test_demo_material_boundary_blocks_real_private_material():
    text = read(DOC)
    for blocked in [
        "real client material",
        "real shoot material",
        "private production names",
        "private locations",
        "private people names",
        "real scripts",
        "real audio",
        "real video",
        "real subtitles",
        "real transcripts",
    ]:
        assert blocked in text


def test_demo_execution_requires_separate_later_phase():
    text = read(DOC)
    assert "This readiness gate does not authorize demo execution." in text
    assert "A later demo scenario phase must separately authorize any local scanner execution." in text
    assert "DEMO.SCENARIO.CONTRACT.V1" in text


def test_later_demo_scenario_contract_requirements_are_defined():
    text = read(DOC)
    for required in [
        "exact synthetic folder shape",
        "exact allowed placeholder file names",
        "exact command shape",
        "expected sanitized output",
        "expected JSON summary fields",
        "expected output folders",
        "expected privacy checks",
        "expected no-goals",
        "abort conditions",
        "validation chain",
    ]:
        assert required in text


def test_product_claim_boundary_blocks_client_facing_claims():
    text = read(DOC)
    for blocked in [
        "client-facing clean classification PASS claims",
        "production-ready claims",
        "commercial release claims",
        "public demo claims",
        "sales deck claims",
        "product launch claims",
    ]:
        assert blocked in text


def test_runtime_boundary_changes_no_code():
    text = read(DOC)
    for required in [
        "This readiness gate changes no runtime files.",
        "No scanner behavior is changed by this readiness gate.",
        "No report behavior is changed by this readiness gate.",
        "No CLI behavior is changed by this readiness gate.",
    ]:
        assert required in text


def test_protected_scope_remains_blocked():
    text = read(DOC)
    for blocked in [
        "SaaS backend changes",
        "SaaS frontend changes",
        "database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe changes",
        "AI Jobs changes",
        "credits changes",
        "ledger changes",
        "frontend changes",
        "backend changes",
        "media-processing implementation",
    ]:
        assert blocked in text


def test_media_processing_and_nle_scope_remains_blocked():
    text = read(DOC)
    for blocked in [
        "ffmpeg execution",
        "ffprobe execution beyond existing availability preflight",
        "transcription",
        "translation",
        "subtitles",
        "sync",
        "NLE export",
        "report-expansion scope",
    ]:
        assert blocked in text


def test_required_validation_evidence_is_declared():
    text = read(DOC)
    for required in [
        "demo readiness gate test passes",
        "bounded implementation QA gate passes",
        "bounded implementation tests pass",
        "scanner safe baseline passes",
        "scanner execution hardening passes",
        "scanner CLI contract passes",
        "WSL guard passes",
        "SQLite regression guard passes",
        "`git diff --check` passes",
    ]:
        assert required in text


def test_scanner_script_still_exposes_semantic_counts_for_demo_readiness():
    source = read(SCANNER_SCRIPT)
    for required in [
        "accepted_extension_counts",
        "rejected_extension_counts",
        "ignored_extension_counts",
        "NON_MEDIA_REJECTED_EXTENSIONS",
    ]:
        assert required in source


def test_scanner_script_still_excludes_txt_from_report_extensions():
    source = read(SCANNER_SCRIPT)
    assert 'REPORT_EXTENSIONS = {".json", ".csv"}' in source
    assert 'NON_MEDIA_REJECTED_EXTENSIONS = {".txt", ".exe"}' in source


def test_gate_result_blocks_real_client_material_demo():
    text = read(DOC)
    assert "The repository is ready to prepare a controlled local synthetic demo scenario." in text
    assert "The repository is not yet authorized for public/client-facing demo claims." in text
    assert "The repository is not yet authorized to run a real client-material demo." in text
