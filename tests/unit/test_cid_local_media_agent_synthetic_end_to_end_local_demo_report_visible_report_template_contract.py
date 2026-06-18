from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_v1.md"
)

VISIBLE_REPORT_QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_contract_qa_gate_v1.md"
)

VISIBLE_REPORT_CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_contract_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")

BLUEPRINT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_standalone_product_blueprint_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_template_contract_document_exists():
    assert DOC.exists()


def test_referenced_files_exist():
    assert VISIBLE_REPORT_QA_GATE_DOC.exists()
    assert VISIBLE_REPORT_CONTRACT_DOC.exists()
    assert FIXTURE.exists()
    assert BLUEPRINT_DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.CONTRACT.V1" in text
    assert "CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Template Contract v1" in text


def test_phase_is_documentation_only_and_blocks_outputs():
    text = read_doc()
    required = [
        "documentation/test-only",
        "It defines a template contract.",
        "It does not create a report artifact.",
        "It does not create HTML.",
        "It does not create PDF.",
        "It does not create DOCX.",
        "It does not create XLSX.",
        "It does not create a Markdown report.",
        "It does not create a renderer.",
        "It does not create a generator.",
        "It does not create a fixture loader.",
        "It does not create runtime code.",
        "It does not modify scanner runtime.",
        "It does not modify SaaS runtime.",
        "It does not execute external binaries.",
        "It does not process client media.",
    ]
    for item in required:
        assert item in text


def test_baseline_and_previous_gate_are_recorded():
    text = read_doc()
    assert "08f5c4c" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1" in text
    assert "PASS_SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_TEMPLATE_CONTRACT" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.V1" in text
    assert "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json" in text
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1" in text


def test_template_status_is_contract_only():
    text = read_doc()
    assert "SYNTHETIC_VISIBLE_REPORT_TEMPLATE_CONTRACT_ONLY" in text
    assert "does not generate one" in text
    assert "future report artifact remains blocked" in text
    assert "future renderer remains blocked" in text
    assert "future generator remains blocked" in text
    assert "future loader remains blocked" in text
    assert "Runtime behavior remains blocked" in text


def test_future_output_family_is_listed_but_not_created():
    text = read_doc()
    outputs = [
        "Markdown report",
        "HTML report",
        "PDF report",
        "DOCX report",
        "XLSX summary",
        "console preview",
        "internal QA snapshot",
        "Only the contract exists in this phase.",
    ]
    for item in outputs:
        assert item in text


def test_language_rules_are_spanish_first():
    text = read_doc()
    required = [
        "Spanish-first",
        "non-engineering stakeholders",
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
        "inventario sintético",
        "informe de demostración",
    ]
    for item in required:
        assert item in text


def test_template_layout_sections_are_mandatory_and_ordered():
    text = read_doc()
    sections = [
        "Portada",
        "Resumen ejecutivo",
        "Aviso de privacidad local",
        "Inventario sintético del proyecto",
        "Resumen por departamentos",
        "Candidatos de sincronía",
        "Alertas y cola de revisión humana",
        "Organización sugerida de carpetas",
        "Qué demuestra esta demo",
        "Qué no demuestra todavía",
        "Siguientes pasos de producto",
        "Apéndice técnico de validación sintética",
    ]

    positions = []
    for section in sections:
        assert section in text
        positions.append(text.index(section))

    assert positions == sorted(positions)
    assert "The order is mandatory." in text


def test_cover_section_contract_is_complete():
    text = read_doc()
    required = [
        "`Producto`: `CID Local Media Agent`",
        "`Ecosistema`: `CID — Cinematic Intelligence Direction`",
        "`Tipo de informe`: `Synthetic End-to-End Local Demo Report`",
        "`Fixture`: `SYNTHETIC_LOCAL_DEMO_001`",
        "`Versión fixture`: `v1`",
        "`Privacidad`: `synthetic_safe_labels_only`",
        "`Estado`: `Datos sintéticos de demostración`",
        "`Uso`: `No usar como informe técnico final`",
        "client name",
        "project title",
        "production title",
        "private path",
        "raw filename",
        "person name",
        "real location",
        "dialogue excerpt",
        "transcription excerpt",
        "script excerpt",
    ]
    for item in required:
        assert item in text


def test_executive_summary_template_has_counts_and_limits():
    text = read_doc()
    required = [
        "Este informe muestra, con datos sintéticos",
        "sin subir vídeo ni audio",
        "10 elementos sintéticos",
        "4 elementos tipo vídeo",
        "3 elementos tipo audio",
        "1 imagen fija",
        "1 documento de producción",
        "1 elemento ignorado/no soportado",
        "6 grupos candidatos de sincronía",
        "10 elementos requieren revisión humana",
        "No se ha analizado material real.",
    ]
    for item in required:
        assert item in text


def test_privacy_section_template_is_complete():
    text = read_doc()
    required = [
        "producto local-first",
        "no se sube vídeo ni audio",
        "no se analizan rutas privadas",
        "no se muestran nombres reales",
        "no se procesa material de cliente",
        "Vídeo/audio subido: No",
        "Material real analizado: No",
        "Rutas privadas incluidas: No",
        "Nombres reales incluidos: No",
        "Contenido de guion incluido: No",
        "Diálogo incluido: No",
        "Transcripción incluida: No",
        "Ejecución ffprobe/ffmpeg: No",
        "Revisión humana: Sí",
    ]
    for item in required:
        assert item in text


def test_inventory_section_template_is_complete():
    text = read_doc()
    required = [
        "Etiqueta segura",
        "Tipo",
        "Duración orientativa",
        "Pista técnica",
        "Grupo de sincronía",
        "Estado de revisión",
        "Revisión recomendada",
        "video",
        "audio",
        "still_image",
        "production_document",
        "ignored_non_media",
        "safe display labels only",
    ]
    for item in required:
        assert item in text


def test_department_section_template_is_complete():
    text = read_doc()
    required = [
        "Montaje",
        "Ayudante de montaje",
        "DIT / media management",
        "Sonido",
        "Subtítulos / localización",
        "Producción",
        "Ignorar o archivar",
        "Revisar antes de ingesta",
        "Revisar candidatos de sincronía",
        "Comprobar metadatos sintéticos",
        "Preparar cola de revisión humana",
        "Valorar archivo o descarte",
    ]
    for item in required:
        assert item in text


def test_blocked_department_language_is_declared():
    text = read_doc()
    blocked = [
        "Validado automáticamente",
        "Sincronizado automáticamente",
        "Transcrito automáticamente",
        "Traducido automáticamente",
        "Preparado para entrega final",
        "Aprobado legalmente",
        "Certificado para emisión",
    ]
    for item in blocked:
        assert item in text


def test_sync_template_is_candidate_only():
    text = read_doc()
    required = [
        "Grupo candidato",
        "Elementos asociados",
        "Motivo de revisión",
        "Riesgo técnico",
        "Acción humana recomendada",
        "candidato de sincronía",
        "posible doble sistema",
        "revisión humana necesaria",
        "timecode no disponible en metadatos sintéticos",
        "posible discrepancia de frame rate",
        "posible discrepancia de sample rate",
    ]
    for item in required:
        assert item in text


def test_sync_completion_claims_are_blocked():
    text = read_doc()
    blocked = [
        "sincronizado",
        "bloqueado",
        "conformado",
        "listo para montaje sin revisión",
        "waveform sync complete",
        "timecode sync complete",
        "clap sync complete",
    ]
    for item in blocked:
        assert item in text


def test_warning_section_template_has_required_codes_and_groups():
    text = read_doc()
    required = [
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
        "Montaje / organización",
        "DIT / gestión de media",
        "Sonido / sincronía",
        "Subtítulos / localización",
        "Archivo / descarte",
        "human action",
    ]
    for item in required:
        assert item in text


def test_folder_section_template_is_plan_only():
    text = read_doc()
    folders = [
        "01_VIDEO",
        "02_AUDIO",
        "03_STILLS",
        "04_DOCUMENTS",
        "05_REPORTS",
        "06_REVIEW_NEEDED",
        "07_EXPORTS_FOR_EDIT",
    ]
    for folder in folders:
        assert folder in text

    required = [
        "No implica que se hayan movido, copiado o renombrado archivos.",
        "files moved",
        "files copied",
        "files renamed",
        "folder structure created on disk",
        "ingest completed",
    ]
    for item in required:
        assert item in text


def test_demo_proves_section_is_limited_to_demo_claims():
    text = read_doc()
    allowed = [
        "La estructura del informe es comprensible.",
        "Los datos sintéticos permiten explicar el valor del producto.",
        "La cola de revisión humana se puede presentar por departamentos.",
        "La promesa local-first se puede comunicar de forma clara.",
        "El reporte futuro puede ayudar a montaje, DIT, sonido, subtítulos y producción.",
        "must not claim runtime capability",
    ]
    for item in allowed:
        assert item in text


def test_demo_does_not_prove_section_is_complete():
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


def test_next_steps_are_planning_only():
    text = read_doc()
    steps = [
        "QA del contrato de template",
        "contrato de renderer sintético",
        "contrato de loader local sintético",
        "implementación controlada de generador visible",
        "revisión humana del reporte generado",
        "preparación de demo local-only",
        "plan de packaging comercial",
        "Estos pasos son planificación; no son capacidades implementadas en esta fase.",
    ]
    for item in steps:
        assert item in text


def test_appendix_template_is_complete():
    text = read_doc()
    appendix = [
        "fixture path",
        "schema version",
        "fixture id",
        "fixture version",
        "item count",
        "category distribution",
        "warning coverage",
        "department review coverage",
        "privacy assertions",
        "validation rules",
        "known limitations",
        "next gated phase",
        "visually separated from the main producer-facing body",
    ]
    for item in appendix:
        assert item in text


def test_data_binding_contract_is_safe():
    text = read_doc()
    allowed = [
        "validated fixture JSON fields",
        "contract-approved static text",
        "contract-approved derived counts",
        "contract-approved warning groups",
        "contract-approved department groups",
        "contract-approved disclaimers",
    ]
    blocked = [
        "raw paths",
        "raw filenames",
        "real media metadata",
        "dialogue text",
        "transcript text",
        "client names",
        "person names",
        "real locations",
        "credentials",
        "secrets",
        "cloud URLs",
    ]
    for item in allowed + blocked:
        assert item in text


def test_fixture_derived_fields_are_declared():
    text = read_doc()
    fields = [
        "fixture_id",
        "fixture_version",
        "privacy_level",
        "fixture_kind",
        "items",
        "project_summary",
        "suggested_folders",
        "privacy_assertions",
        "validation_rules",
        "next_recommended_phase",
        "safe_item_id",
        "safe_display_label",
        "category",
        "duration_hint",
        "container_hint",
        "codec_hint",
        "sync_candidate_group",
        "warning_codes",
        "recommended_department_review",
        "report_notes",
    ]
    for item in fields:
        assert item in text


def test_template_blocks_sensitive_display_fields():
    text = read_doc()
    blocked = [
        "private local path",
        "raw filename",
        "original filename",
        "absolute path",
        "card name",
        "real production name",
        "real location name",
        "real person name",
    ]
    for item in blocked:
        assert item in text


def test_human_review_contract_is_mandatory():
    text = read_doc()
    labels = [
        "Pendiente de revisión humana",
        "Revisar antes de usar en demo pública",
        "Revisar antes de cualquier claim técnico",
        "Revisión de montaje requerida",
        "Revisión DIT requerida",
        "Revisión de sonido requerida",
        "Revisión de subtítulos requerida",
        "No section may say that the tool replaces human judgment.",
    ]
    for item in labels:
        assert item in text


def test_commercial_demo_contract_is_safe():
    text = read_doc()
    assert "controlled commercial demo for trusted contacts only after a later human review gate" in text
    assert "CID Local Media Agent ayuda a ordenar y explicar material local" in text
    assert "manteniendo el material del cliente en local por defecto" in text
    assert "CID Local Media Agent ya sincroniza, transcribe, traduce y exporta material real de forma automática." in text


def test_accessibility_and_readability_rules_exist():
    text = read_doc()
    required = [
        "laptop screen",
        "projector",
        "shared PDF preview",
        "printed one-page summary",
        "producer-facing review call",
        "short paragraphs",
        "clear headings",
        "practical labels",
        "visible disclaimers",
        "no dense engineering blocks in the main body",
        "appendix for technical validation",
    ]
    for item in required:
        assert item in text


def test_contract_decision_and_next_phase_are_declared():
    text = read_doc()
    assert "SYNTHETIC_VISIBLE_REPORT_TEMPLATE_CONTRACT_READY_FOR_QA" in text
    assert "allows only the next documentation/test-only template contract QA gate" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.CONTRACT.QA.GATE.V1" in text


def test_implementation_remains_blocked():
    text = read_doc()
    blocked = [
        "keeps report artifact creation blocked",
        "keeps HTML/PDF/DOCX/XLSX creation blocked",
        "keeps renderer implementation blocked",
        "keeps generator implementation blocked",
        "keeps loader implementation blocked",
        "keeps runtime changes blocked",
        "keeps scanner runtime changes blocked",
        "keeps SaaS integration blocked",
        "keeps external binary execution blocked",
        "keeps real media processing blocked",
    ]
    for item in blocked:
        assert item in text


def test_previous_qa_gate_authorized_template_contract():
    text = VISIBLE_REPORT_QA_GATE_DOC.read_text(encoding="utf-8")
    assert "PASS_SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_TEMPLATE_CONTRACT" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.CONTRACT.V1" in text


def test_visible_report_contract_is_validated_and_referenced():
    text = VISIBLE_REPORT_CONTRACT_DOC.read_text(encoding="utf-8")
    assert "SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_QA" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1" in text


def test_blueprint_confirms_standalone_local_first_product():
    text = BLUEPRINT_DOC.read_text(encoding="utf-8")
    assert "standalone local-first product within CID" in text
    assert "must not depend on CID SaaS to work" in text
    assert "must not upload customer video or audio by default" in text


def test_no_report_or_template_artifacts_created_by_this_phase():
    forbidden = [
        Path("reports"),
        Path("outputs"),
        Path("docs/product/local_media_agent/synthetic_visible_report_v1.html"),
        Path("docs/product/local_media_agent/synthetic_visible_report_v1.pdf"),
        Path("docs/product/local_media_agent/synthetic_visible_report_v1.docx"),
        Path("docs/product/local_media_agent/synthetic_visible_report_v1.xlsx"),
        Path("docs/product/local_media_agent/synthetic_visible_report_template_v1.html"),
        Path("docs/product/local_media_agent/synthetic_visible_report_template_v1.md"),
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
