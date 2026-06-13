from pathlib import Path


DOC_PATH = Path("docs/project/ailink_cid_codex_skills_roadmap_v1.md")


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_codex_skills_roadmap_document_exists():
    assert DOC_PATH.exists()
    assert "AILink/CID Codex Skills Roadmap v1" in _doc()


def test_codex_skills_roadmap_contains_required_sections():
    doc = _doc()
    required_sections = [
        "## 1. Propósito del roadmap de skills",
        "## 2. Relación con AGENTS.md, Codex Skills, OpenCode y auditorías externas",
        "## 3. Skills existentes y para qué sirven",
        "## 4. Principios para crear nuevas skills",
        "## 5. Criterios para NO crear una skill",
        "## 6. Roadmap de skills futuras",
        "## 7. Orden recomendado de implementación",
        "## 8. Skills que conviene posponer",
        "## 9. Riesgos de crear demasiadas skills demasiado pronto",
        "## 10. Cómo usar Codex y OpenCode sin que se pisen",
        "## 11. Relación con el índice maestro del proyecto",
        "## 12. Próximas fases recomendadas",
        "## 13. Criterios de aceptación",
    ]

    for section in required_sections:
        assert section in doc, f"missing section: {section}"


def test_codex_skills_roadmap_records_baseline_and_required_terms():
    doc = _doc()
    required = [
        "AILinkCinema",
        "CID — Cinematic Intelligence Direction",
        "AILink Sync Dialogue",
        "Codex Skills",
        "OpenCode",
        "PostgreSQL-only",
        "No runtime changes",
        "No production public release",
        "No promises of unimplemented features",
        "un agente escribe, otro audita",
        "no crear nuevas skills todavía",
        ".agents/skills",
        "8de2215",
        "ailink-cid-dev-stable-project-state-index-phase2-20260613",
    ]

    for text in required:
        assert text in doc


def test_codex_skills_roadmap_states_documental_scope_and_limits():
    doc = _doc()
    required = [
        "No implementa skills nuevas",
        "no crea directorios bajo `.agents/skills`",
        "no modifica runtime",
        "Este roadmap no autoriza tocar backend/frontend/Docker/Alembic/.env/modelos/DB/pagos/configuración",
        "Las skills futuras deben crearse por fases pequeñas y probadas",
        "Separar CID SaaS de AILink Sync Dialogue",
        "PostgreSQL-only como política obligatoria de CID SaaS",
        "no sustituyen tests reales, guards ni auditoría humana",
    ]

    for text in required:
        assert text in doc


def test_codex_skills_roadmap_covers_future_skill_categories():
    doc = _doc()
    required = [
        "seguridad base WSL/PostgreSQL",
        "backend SaaS CID",
        "AI Jobs / credit ledger / billing",
        "FastAPI / rutas / permisos / tenant safety",
        "AILink Sync Dialogue",
        "comercial / claims / demo / beta",
        "landing / legal / RGPD",
        "marketing leads / n8n / CRM",
        "VPS / Docker / despliegue",
        "frontend / UX / i18n",
        "testing / QA / release",
    ]

    for text in required:
        assert text in doc


def test_codex_skills_roadmap_defines_each_future_skill_contract_shape():
    doc = _doc()
    required = [
        "cid-wsl-postgresql-safety",
        "cid-backend-saas-contract",
        "cid-ai-jobs-credit-billing-safety",
        "cid-fastapi-route-tenant-permission-safety",
        "ailink-sync-dialogue-local-first",
        "ailink-commercial-claims-demo-beta",
        "ailink-landing-legal-rgpd",
        "ailink-marketing-leads-n8n-crm-safety",
        "cid-vps-docker-deploy-readiness",
        "cid-frontend-ux-i18n-boundary",
        "cid-testing-qa-release-discipline",
        "Archivos que podría tocar",
        "Archivos que no debe tocar",
        "Riesgos que evita",
        "Prioridad",
        "Fase recomendada de implementación",
    ]

    for text in required:
        assert text in doc


def test_codex_skills_roadmap_does_not_create_skills_in_this_phase():
    doc = _doc()
    required = [
        "no se deben crear nuevos directorios bajo `.agents/skills` en esta fase",
        "Las skills futuras listadas aquí son propuestas de roadmap, no autorización para implementarlas todas",
        "no crear más de 1 skill por fase",
        "no crear la siguiente skill hasta validar uso real de la anterior",
        "prioriza control y aprendizaje progresivo sobre cantidad de skills",
        "Regla operativa: un agente escribe, otro audita",
    ]

    for text in required:
        assert text in doc


def test_codex_skills_roadmap_avoids_runtime_implementation_claims():
    doc = _doc().lower()
    forbidden = [
        "fase implementa backend",
        "fase implementa frontend",
        "se ha refactorizado",
        "se ha corregido runtime",
        "produccion publica completa: si",
        "production public release: yes",
        "payment lifecycle exists",
        "commit creado",
        "tag creado",
        "push realizado",
        "fastapi(",
        "@router.",
        "app.post(",
        "app.get(",
        "usestate(",
        "useeffect(",
    ]

    for text in forbidden:
        assert text not in doc, (
            f"unsafe claim or implementation fragment found: {text}"
        )
