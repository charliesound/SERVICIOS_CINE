from pathlib import Path

DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_non_customer_fixture_pack_plan_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC.exists(), f"Missing document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_phase_identity_and_result_token_are_declared():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.PLAN.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_PLAN_GATE_V1_CLOSED" in text
    assert "CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN" in text


def test_gate_is_doc_test_only_and_does_not_create_fixtures():
    text = _doc_text()
    assert "documentation and QA only" in text
    assert "this gate does not create it" in text
    assert "This gate does not create the manifest" in text
    assert "no fixtures are created" in text
    assert "Closing this gate does not authorize fixture creation" in text


def test_future_fixture_root_and_manifest_are_planned():
    text = _doc_text()
    assert "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack/v1/" in text
    assert "manifest.controlled.json" in text
    assert "fixture pack version" in text
    assert "relative paths" in text
    assert "non-customer provenance statement" in text


def test_planned_fixture_entries_are_explicit():
    text = _doc_text()
    fixture_ids = [
        "CONTROLLED_NON_CUSTOMER_FIXTURE_VIDEO_MINIMAL_V1",
        "CONTROLLED_NON_CUSTOMER_FIXTURE_AUDIO_MINIMAL_V1",
        "CONTROLLED_NON_CUSTOMER_FIXTURE_NON_MEDIA_REJECT_V1",
        "CONTROLLED_NON_CUSTOMER_FIXTURE_MANIFEST_ONLY_METADATA_V1",
    ]
    for fixture_id in fixture_ids:
        assert fixture_id in text
    assert "controlled_non_customer_minimal_video_v1.mp4" in text
    assert "controlled_non_customer_minimal_audio_v1.wav" in text
    assert "controlled_non_customer_non_media_reject_v1.txt" in text
    assert "controlled_non_customer_manifest_notes_v1.json" in text


def test_integrity_policy_requires_hashes_and_sizes():
    text = _doc_text()
    assert "byte size" in text
    assert "SHA256" in text
    assert "stable relative path" in text
    assert "stable filename" in text
    assert "must fail closed" in text


def test_customer_and_production_material_remain_blocked():
    text = _doc_text()
    assert "use customer material" in text
    assert "use real production material" in text
    assert "customer material" in text
    assert "production rushes" in text
    assert "non-customer" in text
    assert "non-production" in text


def test_ffprobe_ffmpeg_and_scanner_remain_blocked():
    text = _doc_text()
    assert "execute ffprobe" in text
    assert "execute FFmpeg" in text
    assert "run scanner logic" in text
    assert "avoid invoking scanner runtime" in text
    assert "avoid invoking ffprobe or FFmpeg" in text


def test_runtime_pyproject_saas_database_and_frontend_backend_are_blocked():
    text = _doc_text()
    blocked_terms = [
        "modify CLI entrypoints",
        "modify `pyproject.toml`",
        "touch SaaS code",
        "touch database code",
        "touch backend code",
        "touch frontend code",
        "touch installer code",
        "touch `.env`",
    ]
    for term in blocked_terms:
        assert term in text


def test_future_creation_gate_is_separate():
    text = _doc_text()
    assert "later fixture creation gate" in text
    assert "Recommended next phase" in text
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.READINESS.GATE.V1" in text


def test_allowed_use_is_limited_after_future_creation():
    text = _doc_text()
    assert "read-only single-file metadata chain development" in text
    assert "visible report development over controlled fixture files" in text
    assert "future scanner boundary tests limited to the fixture root" in text
    assert "safety and privacy validation" in text


def test_forbidden_use_remains_broad_after_future_creation():
    text = _doc_text()
    forbidden = [
        "external client delivery",
        "broad folder scanning",
        "installation outside the controlled environment",
        "SaaS upload",
        "database ingestion",
        "commercial claim of product readiness",
        "pilot execution",
    ]
    for term in forbidden:
        assert term in text


def test_acceptance_criteria_cover_guards_and_scope():
    text = _doc_text()
    assert "Acceptance criteria for this plan gate" in text
    assert "WSL/repo/secrets guard passes" in text
    assert "PostgreSQL-only regression guard passes" in text
    assert "runtime, pyproject, SaaS, database, backend, frontend, and installer changes blocked" in text
