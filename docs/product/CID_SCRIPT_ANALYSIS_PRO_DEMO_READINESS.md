# CID Script Analysis Pro — Demo Readiness

## Resumen ejecutivo

Commit 4 del Sprint 2. Se preparó la demo guiada y reproducible de Script Analysis Pro para venta/presentación. Se creó guía de demo, script smoke, y se añadió helper visual en la página del módulo.

**Estado anterior**: El módulo era funcional y tenía pantalla propia pero sin guía de demostración, sin smoke validable y sin onboarding visible en la UI.

**Estado actual**: Demo documentada, smoke script disponible, página con helper "Cómo probar". El módulo es demostrable de principio a fin.

---

## Qué se preparó

| Elemento | Archivo | Propósito |
|----------|---------|-----------|
| Demo guide | `docs/demo/CID_SCRIPT_ANALYSIS_PRO_DEMO_GUIDE.md` | Guía paso a paso para demostrar el módulo |
| Smoke script | `scripts/smoke_script_analysis_pro.sh` | Smoke bash que valida health, catalog, summary, exports |
| Readiness doc | `docs/product/CID_SCRIPT_ANALYSIS_PRO_DEMO_READINESS.md` | Esta documentación |
| Directive | `directivas/cid_script_analysis_pro_demo.md` | Directiva técnica |
| Frontend helper | `src/pages/ScriptAnalysisProPage.tsx` | Pequeña caja "Cómo probar" visible sin análisis |

---

## Smoke script

`scripts/smoke_script_analysis_pro.sh`

### Checks

| # | Check | Dependencia |
|---|-------|-------------|
| 1 | Health (`/health`) | Ninguna |
| 2 | Module catalog — `script_analysis` existe | Ninguna |
| 3 | Module catalog — `feature_flag_key: module_script_analysis` | Ninguna |
| 4 | My modules (`/modules/me`) | `TOKEN` |
| 5 | Analysis summary (`/analysis/summary`) | `TOKEN` + `PROJECT_ID` |
| 6 | Export JSON (`/analysis/export?format=json`) | `TOKEN` + `PROJECT_ID` |
| 7 | Export Markdown (`/analysis/export?format=md`) | `TOKEN` + `PROJECT_ID` |

### Usage

```bash
# Basic (health + catalog)
./scripts/smoke_script_analysis_pro.sh

# Full (with auth + project)
TOKEN=xxx PROJECT_ID=yyy ./scripts/smoke_script_analysis_pro.sh

# Custom URL
BASE_URL=https://demo.example.com TOKEN=xxx PROJECT_ID=yyy ./scripts/smoke_script_analysis_pro.sh
```

### Reglas de diseño
- No hardcodea tokens
- Lee `BASE_URL`, `TOKEN`, `PROJECT_ID` de entorno
- Si faltan variables, muestra SKIP y continúa (no rompe)
- No modifica base de datos
- No depende de datos sensibles

---

## Demo guide

`docs/demo/CID_SCRIPT_ANALYSIS_PRO_DEMO_GUIDE.md`

### Cubre

1. **Start the stack** — backend + frontend
2. **Login** — acceso a la app
3. **Entry from Modules Catalog** — ruta `/modules` → `/projects`
4. **Entry from Project** — link "Script Analysis Pro" en header
5. **Check current state** — reconoce sin guion / sin análisis / con análisis
6. **Upload a script** — pegar o subir archivo
7. **Run analysis** — click + polling
8. **Export JSON** — descarga blob
9. **Export Markdown** — descarga blob
10. **Verify blocked state** — 403 MODULE_ACCESS_BLOCKED
11. **GO/NO-GO checklist** — 11 criterios GO, 6 NO-GO
12. **Troubleshooting** — problemas frecuentes + soluciones
13. **Curl commands** — API-level demo snippets
14. **Routes summary** — tabla de endpoints

---

## Frontend: demo helper

Se añadió una caja informativa "Cómo probar este módulo" en `ScriptAnalysisProPage.tsx` que aparece cuando no hay análisis. Incluye:

- Mensaje claro de primer paso
- Icono info/luz
- Sin datos sensibles
- Sin enlaces rotos

---

## Validaciones

```bash
python -m compileall src/                          # sin errores
python -m pytest tests/unit/ -q                    # 331 passed
python -m pytest tests/integration/test_script_analysis_export.py -q   # 7 passed
python -m pytest tests/integration/test_script_analysis_enforcement.py -q  # 6 passed
cd src_frontend && npm run build                   # OK
git status --short                                 # solo archivos esperados
```

---

## Limitaciones

1. **Sin landing con datos semilla**: La demo requiere un proyecto real con guion cargado. No hay página de demostración autónoma con datos ficticios precargados (gap #4 de la auditoría).
2. **Sin test runner frontend**: No hay tests automatizados para la UI del módulo.
3. **Smoke no cubre análisis real**: El smoke valida endpoints pero no ejecuta `POST /analysis/run` — evitaría modificar DB del target.
4. **Sin onboarding interactivo**: No hay tutorial guiado dentro de la página (tooltips, walkthrough).
5. **El helper visual es mínimo**: Una caja de texto, no un onboarding completo.

---

## Siguiente commit recomendado

**Commit 5 — Landing / demo autónoma con datos semilla**

Crear endpoint de datos semilla para Script Analysis Pro que permita al usuario explorar el módulo sin cargar un guion real. Alternativa: crear una página `/demo/script-analysis` con un payload precargado de ejemplo.
