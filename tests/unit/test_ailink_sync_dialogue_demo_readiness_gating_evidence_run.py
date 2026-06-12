from pathlib import Path


DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_readiness_gating_evidence_run_v1.md")
DOC = DOC_PATH.read_text(encoding="utf-8")


def test_evidence_run_doc_exists():
    assert DOC_PATH.exists()
    assert "AILink Sync Dialogue — Demo Readiness Gating Evidence Run v1" in DOC


def test_phase_is_documental_record_only():
    required = [
        "Esta fase es documental y de registro de evidencias",
        "No implementa código",
        "no modifica scanner",
        "no modifica matching",
        "no modifica exports",
        "no modifica reportes",
        "no crea UI real",
        "no crea backend",
        "no crea frontend",
        "no crea instalador",
        "no crea n8n",
        "no crea CRM",
        "no toca PostgreSQL real",
        "no toca Docker",
        "no toca runtime",
        "no toca configuración",
        "no modifica CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_uses_real_phase_dependencies_and_head():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1",
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.PHASE7.2",
        "baa6f0c",
        "ailink-dev-stable-sync-dialogue-demo-gating-evidence-phase7-2-20260612",
    ]
    for text in required:
        assert text in DOC


def test_records_controlled_tmp_execution_scope():
    required = [
        "/tmp/ailink_sync_dialogue_evidence_run_phase7_3",
        "La ejecución no dejó archivos nuevos dentro del repo",
        "scripts/demo/create_sync_dialogue_metadata_demo.py",
        "scripts/demo/run_sync_dialogue_demo_e2e.py",
        "No se usó material audiovisual de cliente",
        "No se usaron datos personales reales",
        "No se usó GPU",
        "No se usó n8n",
        "No se usó Docker",
        "No se usó CID SaaS",
    ]
    for text in required:
        assert text in DOC


def test_metadata_demo_evidence_is_recorded():
    required = [
        "Video count: 3",
        "Audio count: 4",
        "Match suggestions count: 5",
        "High confidence count: 2",
        "scan_result.json: 5767 bytes",
        "media_files.csv: 823 bytes",
        "match_suggestions.csv: 858 bytes",
        "report.html: 4375 bytes",
        "EV-TECH-001 pasa para metadata demo controlada",
    ]
    for text in required:
        assert text in DOC


def test_e2e_demo_evidence_is_recorded():
    required = [
        "total files: 7",
        "video count: 3",
        "audio count: 3",
        "unsupported count: 1",
        "match suggestions count: 0",
        "AILink Sync Dialogue demo completed",
        "dummy files sin metadata real",
        "EV-TECH-001 pasa para demo e2e local",
    ]
    for text in required:
        assert text in DOC


def test_report_and_privacy_evidence_are_recorded():
    required = [
        "media_rows: 7",
        "match_rows: 5",
        "html_contains_AILink: True",
        "html_contains_client_forbidden_word: False",
        "html_contains_personal_forbidden_word: False",
        "scene01_take01.mov",
        "scene01_take01.wav",
        "No hay indicio de material de cliente",
        "No hay indicio de datos personales reales",
    ]
    for text in required:
        assert text in DOC


def test_safety_grep_false_positive_is_documented():
    required = [
        "shared_name_tokens",
        "falso positivo técnico aceptado",
        "No es un token secreto",
        "No es una credencial",
        "No se detectaron secretos evidentes",
    ]
    for text in required:
        assert text in DOC


def test_gating_decision_is_limited_pass():
    required = [
        "Resultado: LIMITED PASS",
        "GATE-PRIVACY-001",
        "GATE-PRIVACY-002",
        "GATE-TECH-001",
        "GATE-TECH-002",
        "GATE-COMM-001",
        "GATE-COMM-002",
        "GATE-COMM-003",
        "Los gates técnicos y de privacidad pasan",
        "Falta todavía validar guion",
        "Persona de confianza muy cercana",
        "LinkedIn público como demo final",
    ]
    for text in required:
        assert text in DOC


def test_next_action_is_script_refinement_not_more_features():
    required = [
        "AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.3",
        "Preparar el guion real de demo de 5 a 7 minutos",
        "evitar vender sincronización automática final",
        "explicación de por qué e2e dummy puede tener 0 matches",
        "El siguiente paso no debe ser añadir funcionalidad",
    ]
    for text in required:
        assert text in DOC


def test_document_does_not_include_runtime_implementation_commands():
    forbidden = [
        "CREATE TABLE",
        "ALTER TABLE",
        "DROP TABLE",
        "op.create_table",
        "Base.metadata.create_all",
        "docker compose",
        "n8n import",
        "npm install",
        "pnpm install",
        "ffmpeg -i",
        "uvicorn",
        "FastAPI(",
        "@router.",
        "app.post(",
        "useState(",
        "useEffect(",
    ]
    lower_doc = DOC.lower()
    for text in forbidden:
        assert text.lower() not in lower_doc
