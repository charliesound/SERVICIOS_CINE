from pathlib import Path

DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_non_customer_fixture_pack_creation_readiness_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC.exists(), f"Missing document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_phase_identity_result_and_decision_are_declared():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_CREATION_READINESS_GATE_V1_CLOSED" in text
    assert "CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN" in text
    assert "READY_FOR_SEPARATE_CONTROLLED_FIXTURE_PACK_CREATION_GATE_WITH_BOUNDARIES" in text


def test_gate_is_doc_test_only_and_does_not_create_fixtures():
    text = _doc_text()
    assert "documentation and QA only" in text
    assert "This gate may add only" in text
    assert "This gate reviews whether" in text
    assert "Closing this gate does not create fixtures" in text
    assert "does not authorize or perform fixture creation" in text


def test_contract_and_plan_dependencies_are_reviewed():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CONTRACT.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.PLAN.GATE.V1" in text
    assert "Contract input" in text
    assert "Plan input" in text


def test_future_fixture_root_and_manifest_remain_explicit():
    text = _doc_text()
    assert "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack/v1/" in text
    assert "manifest.controlled.json" in text
    assert "Required future root" in text
    assert "Required future manifest" in text
    assert "must fail closed if it attempts to create fixtures outside this root" in text


def test_planned_fixture_ids_and_roles_are_preserved():
    text = _doc_text()
    fixture_ids = [
        "CONTROLLED_NON_CUSTOMER_FIXTURE_VIDEO_MINIMAL_V1",
        "CONTROLLED_NON_CUSTOMER_FIXTURE_AUDIO_MINIMAL_V1",
        "CONTROLLED_NON_CUSTOMER_FIXTURE_NON_MEDIA_REJECT_V1",
        "CONTROLLED_NON_CUSTOMER_FIXTURE_MANIFEST_ONLY_METADATA_V1",
    ]
    for fixture_id in fixture_ids:
        assert fixture_id in text
    assert "minimal video metadata target" in text
    assert "minimal audio metadata target" in text
    assert "non-media reject target" in text
    assert "manifest-only metadata notes target" in text


def test_integrity_requirements_are_ready_for_creation_gate():
    text = _doc_text()
    assert "exact byte size" in text
    assert "SHA256" in text
    assert "stable relative path" in text
    assert "stable filename" in text
    assert "Any mismatch between manifest and bytes must fail closed" in text


def test_customer_production_and_sensitive_material_remain_blocked():
    text = _doc_text()
    blocked = [
        "non-customer",
        "non-production",
        "client material",
        "production rushes",
        "customer material",
        "voices",
        "faces",
        "identifying metadata",
    ]
    for term in blocked:
        assert term in text


def test_ffprobe_ffmpeg_scanner_and_runtime_remain_blocked():
    text = _doc_text()
    assert "execute ffprobe" in text
    assert "execute FFmpeg" in text
    assert "run scanner logic" in text
    assert "scanner execution blocked" in text
    assert "runtime metadata extraction" in text


def test_runtime_pyproject_saas_database_and_ui_surfaces_remain_blocked():
    text = _doc_text()
    blocked_terms = [
        "runtime, pyproject, SaaS, database, backend, frontend, and installer changes blocked",
        "modify `pyproject.toml`",
        "touch SaaS code",
        "touch database code",
        "touch backend code",
        "touch frontend code",
        "touch installer code",
    ]
    for term in blocked_terms:
        assert term in text


def test_creation_gate_requirements_are_separate_and_complete():
    text = _doc_text()
    requirements = [
        "exact file list",
        "exact fixture root",
        "exact manifest path",
        "generation method",
        "integrity calculation method",
        "cleanup and rollback rules",
        "staged scope check",
        "QA integrity tests",
    ]
    for requirement in requirements:
        assert requirement in text
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1" in text


def test_allowed_and_forbidden_future_uses_are_bounded():
    text = _doc_text()
    assert "read-only single-file metadata chain development" in text
    assert "visible report development over controlled fixture files" in text
    assert "future scanner boundary tests limited to the fixture root" in text
    assert "broad folder scanning" in text
    assert "SaaS upload" in text
    assert "database ingestion" in text
    assert "pilot execution" in text


def test_acceptance_criteria_cover_guards_scope_and_non_authorization():
    text = _doc_text()
    assert "Acceptance criteria for this readiness gate" in text
    assert "the QA test passes" in text
    assert "WSL/repo/secrets guard passes" in text
    assert "PostgreSQL-only regression guard passes" in text
    assert "Closing this gate only authorizes preparing a later" in text
