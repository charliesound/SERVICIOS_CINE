from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_contract_qa_gate_v1.md"
)

CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_contract_v1.md"
)

FIXTURE_QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_fixture_json_create_qa_gate_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")

BLUEPRINT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_standalone_product_blueprint_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def read_contract() -> str:
    return CONTRACT_DOC.read_text(encoding="utf-8")


def test_qa_gate_document_exists():
    assert DOC.exists()


def test_referenced_files_exist():
    assert CONTRACT_DOC.exists()
    assert FIXTURE_QA_GATE_DOC.exists()
    assert FIXTURE.exists()
    assert BLUEPRINT_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Contract QA Gate v1" in text


def test_qa_gate_is_documentation_only_and_blocks_artifacts():
    text = read_doc()
    required = [
        "documentation/test-only",
        "It validates an existing visible report contract.",
        "It does not create a visible report file.",
        "It does not create HTML.",
        "It does not create PDF.",
        "It does not create DOCX.",
        "It does not create XLSX.",
        "It does not create a renderer.",
        "It does not create a generator.",
        "It does not create a fixture loader.",
        "It does not create runtime code.",
        "It does not modify scanner runtime.",
        "It does not modify SaaS runtime.",
        "It does not execute ffprobe.",
        "It does not execute ffmpeg.",
        "It does not process real media.",
        "It does not create installer behavior.",
        "It does not create licensing behavior.",
    ]
    for item in required:
        assert item in text


def test_baseline_and_audited_phase_are_recorded():
    text = read_doc()
    assert "429ac7e" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.V1" in text
    assert "SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_QA" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.JSON.CREATE.QA.GATE.V1" in text
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_VALIDATED_FOR_VISIBLE_REPORT_CONTRACT" in text
    assert "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json" in text
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1" in text


def test_qa_scope_is_complete():
    text = read_doc()
    scope = [
        "declares a stakeholder-readable report purpose",
        "keeps synthetic demo status clear",
        "defines target audiences",
        "defines required report sections in order",
        "includes a local-first privacy statement",
        "includes a synthetic inventory summary",
        "includes a department review overview",
        "includes a sync candidate overview",
        "includes a warning and human review queue",
        "includes suggested folder organization",
        "separates demo proof from runtime capability",
        "lists what the demo does not prove yet",
        "lists next product steps as planning only",
        "includes a validation appendix",
        "requires Spanish-first readable language",
        "uses production-facing wording",
        "requires visible disclaimers",
        "blocks unsafe public claims",
        "preserves assisted-workflow positioning",
        "allows only a next documentation/test-only QA or template contract step",
    ]
    for item in scope:
        assert item in text


def test_required_visible_disclaimers_are_repeated():
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


def test_required_product_framing_is_repeated():
    text = read_doc()
    required = [
        "CID Local Media Agent muestra, con datos sintéticos",
        "sin subir vídeo ni audio",
        "Este reporte no demuestra todavía análisis real de material",
        "enseñar el valor del producto a contactos de confianza",
        "La herramienta está orientada a asistir al equipo",
        "no a sustituir el criterio del montador, DIT, sonidista o productor",
    ]
    for item in required:
        assert item in text


def test_pass_criteria_are_complete():
    text = read_doc()
    criteria = [
        "is documentation/test-only",
        "references the correct baseline",
        "references the visible report contract phase",
        "references the fixture JSON QA gate",
        "references the standalone product blueprint",
        "defines report status as contract-only",
        "lists target audiences",
        "defines all required report sections",
        "includes section order",
        "blocks identity leaks",
        "uses fixture counts correctly",
        "preserves local-first privacy language",
        "defines minimum inventory columns",
        "defines department review language",
        "blocks synchronization completion claims",
        "includes required warning coverage",
        "defines suggested folders as a plan only",
        "limits demo proof to demo-readiness",
        "lists non-proven runtime capabilities",
        "keeps next steps as planning only",
        "requires visible disclaimers",
        "blocks public overclaims",
        "preserves safe commercial framing",
        "points to a next gated template contract phase",
    ]
    for item in criteria:
        assert item in text


def test_fail_criteria_block_artifacts_and_runtime():
    text = read_doc()
    fail_items = [
        "creates or permits a real report artifact",
        "creates or permits HTML, PDF, DOCX or XLSX output",
        "creates or permits a renderer",
        "creates or permits a generator",
        "creates or permits a loader",
        "creates or permits runtime code",
        "creates or authorizes scanner runtime changes",
        "creates or authorizes SaaS integration",
        "creates or authorizes ffprobe execution",
        "creates or authorizes ffmpeg execution",
        "creates or authorizes real media processing",
        "creates or authorizes installer behavior",
        "creates or authorizes licensing behavior",
    ]
    for item in fail_items:
        assert item in text


def test_fail_criteria_block_public_overclaims():
    text = read_doc()
    blocked = [
        "claims real footage was scanned",
        "claims real sound was synchronized",
        "claims real clips were transcribed",
        "claims real subtitles were translated",
        "claims real media was organized on disk",
        "claims export to DaVinci is complete",
        "claims export to Avid is complete",
        "claims export to Premiere is complete",
        "claims the tool is production-certified",
        "claims the tool is legally certified",
        "claims the tool replaces the editor",
        "claims the tool replaces the assistant editor",
        "claims the tool replaces the DIT",
        "claims the tool replaces the sound team",
        "claims the tool replaces human review",
    ]
    for item in blocked:
        assert item in text


def test_qa_review_declares_pass_reasons():
    text = read_doc()
    reasons = [
        "it is documentation/test-only",
        "it defines a stakeholder-readable report contract",
        "it preserves the synthetic demo boundary",
        "it uses the validated JSON fixture as a data source reference",
        "it keeps report generation blocked",
        "it keeps renderer implementation blocked",
        "it keeps loader implementation blocked",
        "it keeps runtime changes blocked",
        "it keeps scanner changes blocked",
        "it keeps SaaS integration blocked",
        "it keeps external binary execution blocked",
        "it keeps real media processing blocked",
        "it uses production-facing language",
        "it defines required disclaimers",
        "it blocks unsafe public claims",
        "it preserves local-first privacy language",
        "not a replacement",
    ]
    for item in reasons:
        assert item in text


def test_controlled_reservations_remain_active():
    text = read_doc()
    reservations = [
        "no visible report artifact exists yet",
        "no template exists yet",
        "no renderer exists yet",
        "no generator exists yet",
        "no loader exists yet",
        "no runtime capability exists from this phase",
        "no real media processing is allowed",
        "no external presentation should happen before a later human review gate",
        "These reservations do not block proceeding to the next documentation/test-only contract phase.",
    ]
    for item in reservations:
        assert item in text


def test_gate_result_and_next_phase_are_declared():
    text = read_doc()
    assert "PASS_SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_TEMPLATE_CONTRACT" in text
    assert "authorizes only the next documentation/test-only synthetic visible report template contract phase" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.CONTRACT.V1" in text


def test_gate_result_keeps_implementation_blocked():
    text = read_doc()
    blocked = [
        "keeps visible report artifact creation blocked",
        "keeps renderer implementation blocked",
        "keeps generator implementation blocked",
        "keeps loader implementation blocked",
        "keeps runtime changes blocked",
        "keeps scanner runtime changes blocked",
        "keeps SaaS integration blocked",
        "keeps ffprobe execution blocked",
        "keeps ffmpeg execution blocked",
        "keeps real media processing blocked",
    ]
    for item in blocked:
        assert item in text


def test_next_phase_is_template_contract_only():
    text = read_doc()
    next_phase_rules = [
        "The next phase should define a template contract only.",
        "It must not create a real report.",
        "It must not create HTML.",
        "It must not create PDF.",
        "It must not create DOCX.",
        "It must not create XLSX.",
        "It must not create a renderer.",
        "It must not create a generator.",
        "It must not create a loader.",
        "It must not create runtime code.",
        "It must not process client media.",
    ]
    for item in next_phase_rules:
        assert item in text


def test_audited_contract_contains_required_contract_decision():
    text = read_contract()
    assert "SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_QA" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1" in text


def test_audited_contract_is_contract_only():
    text = read_contract()
    required = [
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
    ]
    for item in required:
        assert item in text


def test_audited_contract_contains_required_visible_sections():
    text = read_contract()
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
    for section in sections:
        assert section in text


def test_fixture_qa_gate_authorized_visible_report_contract():
    text = FIXTURE_QA_GATE_DOC.read_text(encoding="utf-8")
    assert "PASS_SYNTHETIC_DEMO_REPORT_FIXTURE_JSON_VALIDATED_FOR_VISIBLE_REPORT_CONTRACT" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.V1" in text


def test_blueprint_still_confirms_local_first_standalone_product():
    text = BLUEPRINT_DOC.read_text(encoding="utf-8")
    assert "standalone local-first product within CID" in text
    assert "must not depend on CID SaaS to work" in text
    assert "must not upload customer video or audio by default" in text


def test_no_output_artifacts_are_created_by_this_phase():
    forbidden = [
        Path("reports"),
        Path("outputs"),
        Path("docs/product/local_media_agent/synthetic_visible_report_v1.html"),
        Path("docs/product/local_media_agent/synthetic_visible_report_v1.pdf"),
        Path("docs/product/local_media_agent/synthetic_visible_report_v1.docx"),
        Path("docs/product/local_media_agent/synthetic_visible_report_v1.xlsx"),
    ]
    for path in forbidden:
        assert not path.exists()


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
