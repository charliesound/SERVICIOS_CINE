# Directiva: CID Script Analysis Pro — Demo Readiness

## Objetivo

Preparar la demo guiada y reproducible de Script Analysis Pro para venta/presentación: guía paso a paso, script smoke, helper visual y documentación de readiness.

## Contexto

Commit 4 del Sprint 2 del roadmap modular. La auditoría (CID_SCRIPT_ANALYSIS_PRO_AUDIT.md) identificó que faltaba demo guiada (gap #4). Los commits 1-3 (enforcement, export, frontend) están completados. Este commit es solo documentación + script smoke + helper visual mínimo — no toca backend funcional, Docker, migraciones, AGENTS.md, billing, ni datos reales.

## Archivos afectados

### Creados
- `docs/demo/CID_SCRIPT_ANALYSIS_PRO_DEMO_GUIDE.md` — guía de demo paso a paso
- `scripts/smoke_script_analysis_pro.sh` — smoke bash para validar endpoints
- `docs/product/CID_SCRIPT_ANALYSIS_PRO_DEMO_READINESS.md` — documentación de readiness
- `directivas/cid_script_analysis_pro_demo.md` — esta directiva

### Modificados
- `src_frontend/src/pages/ScriptAnalysisProPage.tsx` — +1 caja "Cómo probar este módulo"

## Entradas

- `ScriptAnalysisProPage.tsx` — página actual del módulo
- `intake_routes.py` — endpoints de análisis y export
- `modules.yml` — definición de script_analysis con `feature_flag_key`
- Patrones de smoke existentes: `smoke_cid_dev.sh`, `smoke_budget_estimator.py`

## Salidas

- Guía de demo con 10 pasos, GO/NO-GO checklist, troubleshooting, comandos curl
- Smoke script con 7 checks, configurable via entorno, sin side effects
- Helper visual en frontend para guiar al usuario
- Documentación de readiness con limitaciones conocidas

## Flujo de trabajo

1. Crear `docs/demo/` si no existe
2. Escribir guía de demo: objetivo, prerequisitos, pasos, qué ver, GO/NO-GO, troubleshooting, curl
3. Crear `scripts/smoke_script_analysis_pro.sh`:
   - Validar health
   - Validar catalog (script_analysis existe + feature_flag_key correcto)
   - Validar my modules (si TOKEN presente)
   - Validar analysis summary (si TOKEN + PROJECT_ID)
   - Validar export JSON (parseable + campos esperados)
   - Validar export MD (header esperado)
   - Salir con código de error = número de fallos
4. Añadir caja "Cómo probar" en `ScriptAnalysisProPage.tsx`:
   - Visible cuando no hay analysis
   - Mensaje instructivo
   - Sin datos sensibles
5. Escribir readiness doc
6. Escribir directiva
7. Validar: compileall, pytest, npm run build, git status

## Validaciones

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"

python -m compileall src/
python -m pytest tests/unit/ -q
python -m pytest tests/integration/test_script_analysis_export.py -q
python -m pytest tests/integration/test_script_analysis_enforcement.py -q

cd src_frontend && npm run build

git status --short
git diff --stat
```

## Casos borde

- Smoke sin TOKEN: checks 1-3 corren, 4-7 muestran SKIP, exit 0
- Smoke sin PROJECT_ID: checks 1-4 corren, 5-7 muestran SKIP
- Export sin análisis: endpoint devuelve 200 con `has_analysis: false` y warnings — el smoke valida que el JSON sea parseable
- Health caído: smoke falla temprano (check 1), reporta 1 failure, continúa con resto
- Backend no accesible: curl devuelve código vacío, se maneja con `|| true` para no romper el script

## Restricciones conocidas

- NO tocar backend funcional
- NO tocar Docker, migraciones, AGENTS.md
- NO introducir datos reales de cliente
- NO crear billing
- NO modificar `modules.yml` ni `plans.yml`
- El smoke NO ejecuta `POST /analysis/run` para evitar modificar DB del target
- El helper visual es una caja de texto estática, no un onboarding interactivo

## Errores aprendidos

- La caja "Cómo probar" debe estar visible solo cuando no hay análisis — si ya hay análisis, el usuario ya sabe usar el módulo
- El smoke script debe usar `|| true` en captura de HTTP_CODE para evitar `set -euo pipefail` rompiendo el script si curl falla
- Los nombres de archivo export usan `CID_script_analysis_` (underscore, no guion) para consistencia con backend

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
./scripts/smoke_script_analysis_pro.sh
TOKEN=xxx PROJECT_ID=yyy ./scripts/smoke_script_analysis_pro.sh
cd src_frontend && npm run build
git diff --stat
git status --short
```
