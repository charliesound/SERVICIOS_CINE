import json
from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_contract_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")

FIXTURE_QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_json_create_qa_gate_v1.md"
)

BLUEPRINT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_standalone_product_blueprint_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_visible_report_contract_document_exists():
    assert DOC.exists()


def test_referenced_baseline_files_exist():
    assert FIXTURE.exists()
    assert FIXTURE_QA_GATE_DOC.exists()
    assert BLUEPRINT_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Contract v1" in text


def test_phase_is_documentation_only_and_blocks_runtime():
    text = read_doc()
    required = [
        "documentation/test-only",
        "It does not create a report file.",
        "It does not create a report generator.",
        "It does not create a report renderer.",
        "It does not create a fixture loader.",
        "It does not create runtime code.",
        "It does not modify the scanner.",
        "It does not modify SaaS code.",
        "It does not execute ffprobe.",
        "It does not execute ffmpeg.",
        "It does not process real media.",
        "It does not create installer or licensing behavior.",
    ]
    for item in required:
        assert item in text


def test_baseline_and_previous_gate_are_recorded():
    text = read_doc()
    assert "683785d" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.QA.GATE.V1" in text
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_VALIDATED_FOR_VISIBLE_REPORT_CONTRACT" in text
    assert "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json" in text
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1" in text


def test_report_status_and_required_safety_phrases_are_declared():
    text = read_doc()
    required = [
        "SYNTHETIC_VISIBLE_DEMO_REPORT_CONTRACT_ONLY",
        "synthetic demo data",
        "local-first product direction",
        "no real media analysis",
        "no client media processed",
        "no cloud upload",
        "no external binary execution",
        "no synchronization completed",
        "no transcription completed",
        "no subtitle translation completed",
        "no DaVinci export completed",
        "human review required before public-facing use",
    ]
    for item in required:
        assert item in text


def test_target_audience_is_declared():
    text = read_doc()
    audience = [
        "producers",
        "post supervisors",
        "editors",
        "assistant editors",
        "DITs",
        "sound teams",
        "subtitle/localization teams",
        "film school stakeholders",
        "trusted early contacts",
    ]
    for item in audience:
        assert item in text


def test_required_report_sections_are_in_order():
    text = read_doc()
    sections = [
        "Cover / Demo identity",
        "Executive summary",
        "Local-first privacy statement",
        "Synthetic project inventory summary",
        "Department review overview",
        "Sync candidate overview",
        "Warnings and human review queue",
        "Suggested folder organization",
        "What this demo proves",
        "What this demo does not prove yet",
        "Next product steps",
        "Appendix: synthetic fixture validation",
    ]

    positions = []
    for section in sections:
        assert section in text
        positions.append(text.index(section))

    assert positions == sorted(positions)


def test_cover_contract_blocks_identity_leaks():
    text = read_doc()
    required = [
        "fixture id: `SYNTHETIC_LOCAL_DEMO_001`",
        "fixture version: `v1`",
        "privacy level: `synthetic_safe_labels_only`",
        "status label: `synthetic demo, not real media analysis`",
        "client name",
        "project title",
        "production title",
        "real path",
        "raw filename",
        "real person name",
        "real location",
    ]
    for item in required:
        assert item in text


def test_executive_summary_uses_fixture_counts():
    text = read_doc()
    fixture = load_fixture()
    summary = fixture["project_summary"]

    assert f"{summary['total_items']} synthetic items" in text
    assert f"{summary['video_like_count']} video-like items" in text
    assert f"{summary['audio_like_count']} audio-like items" in text
    assert f"{summary['still_like_count']} still-image-like item" in text
    assert f"{summary['document_like_count']} document-like item" in text
    assert f"{summary['ignored_or_unsupported_count']} ignored/unsupported item" in text
    assert f"{summary['sync_candidate_group_count']} sync candidate groups" in text
    assert f"{summary['items_requiring_human_review_count']} items requiring human review" in text


def test_local_first_privacy_statement_is_complete():
    text = read_doc()
    required = [
        "customer media stays local by default",
        "video and audio are not uploaded by default",
        "cloud upload is false in the synthetic fixture",
        "external binary execution is false in the synthetic fixture",
        "the fixture uses synthetic safe labels only",
        "no private paths are present",
        "no raw filenames are present",
        "no client names are present",
        "no person names are present",
        "no real locations are present",
        "no script content is present",
        "no dialogue content is present",
        "no transcription content is present",
    ]
    for item in required:
        assert item in text


def test_inventory_summary_contract_has_minimum_columns():
    text = read_doc()
    required_columns = [
        "safe item label",
        "category",
        "duration hint",
        "technical hint",
        "sync group",
        "review status",
        "department review",
    ]
    for item in required_columns:
        assert item in text


def test_department_review_overview_contract_is_complete():
    text = read_doc()
    reviews = [
        "editorial review",
        "assistant editor review",
        "DIT review",
        "sound review",
        "subtitle review",
        "production review",
        "ignore/archive review",
    ]
    for item in reviews:
        assert item in text


def test_acceptable_and_blocked_review_wording_are_declared():
    text = read_doc()
    allowed = [
        "Needs assistant editor review",
        "Needs DIT review",
        "Needs sound review",
        "Ready for subtitle review",
        "Review before ingest",
        "Archive or ignore candidate",
    ]
    blocked = [
        "Automatically synchronized",
        "Automatically transcribed",
        "Automatically translated",
        "Ready for final delivery",
        "Validated for broadcast",
        "Budget-safe",
        "Legally cleared",
    ]
    for item in allowed + blocked:
        assert item in text


def test_sync_candidate_contract_blocks_completion_claims():
    text = read_doc()
    allowed = [
        "Candidate sync group",
        "Possible double-system sound",
        "Needs human sync review",
        "Timecode appears unavailable in synthetic metadata",
        "Frame-rate mismatch warning",
        "Sample-rate mismatch warning",
    ]
    blocked = [
        "Synced",
        "Matched",
        "Locked",
        "Conformed",
        "Ready for edit without review",
        "Waveform sync complete",
        "Timecode sync complete",
        "Clap sync complete",
    ]
    for item in allowed + blocked:
        assert item in text


def test_warning_coverage_matches_fixture():
    text = read_doc()
    required_warnings = {
        "MISSING_TIMECODE",
        "POSSIBLE_DOUBLE_SYSTEM_SOUND",
        "FRAME_RATE_MISMATCH",
        "SAMPLE_RATE_MISMATCH",
        "NEEDS_HUMAN_REVIEW",
        "READY_FOR_EDITOR_REVIEW",
        "READY_FOR_DIT_REVIEW",
        "READY_FOR_SOUND_REVIEW",
        "READY_FOR_SUBTITLE_REVIEW",
        "UNSUPPORTED_CONTAINER_HINT",
    }
    fixture_warnings = {
        warning
        for item in load_fixture()["items"]
        for warning in item["warning_codes"]
    }

    assert required_warnings.issubset(fixture_warnings)

    for warning in required_warnings:
        assert warning in text


def test_warning_grouping_is_practical_for_production():
    text = read_doc()
    groups = [
        "editorial organization",
        "DIT/media management",
        "sound/sync review",
        "subtitle/localization review",
        "unsupported/archive review",
    ]
    for item in groups:
        assert item in text


def test_suggested_folders_match_fixture_and_are_not_file_operations():
    text = read_doc()
    folders = load_fixture()["suggested_folders"]
    for folder in folders:
        assert folder in text

    required = [
        "suggested organization plan",
        "not an executed file operation",
        "must not claim files were moved",
        "must not claim files were copied",
        "must not claim files were renamed",
    ]
    for item in required:
        assert item in text


def test_demo_proves_only_demo_readiness_not_runtime_capability():
    text = read_doc()
    allowed_claims = [
        "the product direction is understandable",
        "synthetic inventory can be structured safely",
        "review queues can be explained to postproduction roles",
        "department-oriented reporting can be designed",
        "local-first privacy language can be preserved",
        "a future visible report can be generated from safe synthetic data after implementation",
        "demo-readiness claims, not runtime capability claims",
    ]
    for item in allowed_claims:
        assert item in text


def test_demo_does_not_prove_runtime_capabilities_yet():
    text = read_doc()
    not_proven = [
        "real media scanning",
        "real metadata extraction",
        "ffprobe integration",
        "ffmpeg integration",
        "waveform synchronization",
        "timecode synchronization",
        "clap synchronization",
        "transcription",
        "speaker detection",
        "language detection",
        "subtitle translation",
        "DaVinci export",
        "Avid export",
        "Premiere export",
        "installer behavior",
        "license activation",
        "customer deployment",
        "SaaS synchronization",
    ]
    for item in not_proven:
        assert item in text


def test_next_product_steps_are_planning_only():
    text = read_doc()
    steps = [
        "visible report QA gate",
        "synthetic report template contract",
        "synthetic report renderer contract",
        "local fixture loader contract",
        "visible report generator implementation gate",
        "local-only demo packaging plan",
        "human review before external presentation",
        "These are planning steps only.",
    ]
    for item in steps:
        assert item in text


def test_appendix_contract_is_complete():
    text = read_doc()
    appendix_items = [
        "fixture path",
        "schema version",
        "fixture id",
        "item count",
        "category distribution",
        "warning coverage",
        "department review coverage",
        "privacy assertions",
        "validation rules",
        "known limitations",
        "clearly separated from the producer-facing summary",
    ]
    for item in appendix_items:
        assert item in text


def test_visual_and_language_rules_are_declared():
    text = read_doc()
    required = [
        "readable in Spanish first",
        "English labels may remain for technical fixture identifiers",
        "production language",
        "montaje",
        "ayudante de montaje",
        "DIT",
        "sonido",
        "subtítulos",
        "revisión humana",
        "organización de material",
        "cola de revisión",
        "candidatos de sincronía",
        "privacidad local",
        "avoid exaggerated claims",
        "avoid SaaS claims",
        "avoid AI replacement claims",
        "assisted workflow, not creative replacement",
    ]
    for item in required:
        assert item in text


def test_required_visible_disclaimers_are_declared():
    text = read_doc()
    disclaimers = [
        "Datos sintéticos de demostración",
        "No se ha analizado material real",
        "No se ha subido vídeo ni audio",
        "No se ha ejecutado ffprobe ni ffmpeg",
        "No se ha sincronizado material real",
        "No se ha transcrito material real",
        "No se ha traducido subtítulos reales",
        "Revisión humana obligatoria",
        "No usar como informe técnico final",
    ]
    for item in disclaimers:
        assert item in text


def test_blocked_public_claims_are_declared():
    text = read_doc()
    blocked_claims = [
        "real footage has been scanned",
        "real sound has been synchronized",
        "real clips have been transcribed",
        "real subtitles have been translated",
        "real media has been organized on disk",
        "export to DaVinci is complete",
        "export to Avid is complete",
        "export to Premiere is complete",
        "the tool is production-certified",
        "the tool is legally certified",
        "the tool is ready for unattended customer deployment",
        "the tool replaces the editor",
        "the tool replaces the assistant editor",
        "the tool replaces the DIT",
        "the tool replaces the sound team",
        "the tool replaces human review",
    ]
    for item in blocked_claims:
        assert item in text


def test_safe_commercial_framing_is_declared():
    text = read_doc()
    required = [
        "CID Local Media Agent muestra, con datos sintéticos",
        "sin subir vídeo ni audio",
        "Este reporte no demuestra todavía análisis real de material",
        "enseñar el valor del producto a contactos de confianza",
        "asistir al equipo",
        "no a sustituir el criterio del montador, DIT, sonidista o productor",
    ]
    for item in required:
        assert item in text


def test_contract_decision_and_next_gate_are_declared():
    text = read_doc()
    assert "SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_QA" in text
    assert "allows only the next documentation/test-only QA gate" in text
    assert "keeps renderer implementation blocked" in text
    assert "keeps generator implementation blocked" in text
    assert "keeps loader implementation blocked" in text
    assert "keeps scanner runtime changes blocked" in text
    assert "keeps SaaS integration blocked" in text
    assert "keeps external binary execution blocked" in text
    assert "keeps real media processing blocked" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1" in text


def test_previous_fixture_qa_gate_authorizes_visible_report_contract():
    text = FIXTURE_QA_GATE_DOC.read_text(encoding="utf-8")
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_VALIDATED_FOR_VISIBLE_REPORT_CONTRACT" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.V1" in text


def test_blueprint_still_confirms_standalone_local_first_product():
    text = BLUEPRINT_DOC.read_text(encoding="utf-8")
    assert "standalone local-first product within CID" in text
    assert "must not depend on CID SaaS to work" in text
    assert "must not upload customer video or audio by default" in text


def test_fixture_is_still_synthetic_and_local_safe():
    fixture = load_fixture()
    assert fixture["privacy_level"] == "synthetic_safe_labels_only"
    assert fixture["cloud_upload"] is False
    assert fixture["external_binary_execution"] is False
    assert fixture["client_material_used"] is False
    assert fixture["human_review_required"] is True
    assert fixture["privacy_assertions"]["contains_private_paths"] is False
    assert fixture["privacy_assertions"]["contains_raw_filenames"] is False
    assert fixture["privacy_assertions"]["contains_dialogue_content"] is False
    assert fixture["privacy_assertions"]["contains_transcription_content"] is False


def test_test_file_does_not_import_external_command_modules():
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "import " + "o" + "s",
        "from " + "o" + "s",
        "P" + "open(",
        "shell" + "=",
    ]
    for item in forbidden:
        assert item not in source
