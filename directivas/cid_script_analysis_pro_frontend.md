# Directiva: CID Script Analysis Pro — Frontend

## Objetivo

Crear una experiencia frontend propia para CID Script Analysis Pro: página dedicada con ruta propia, API client, tipos, navegación contextual y documentación.

## Contexto

Commit 3 del Sprint 2 del roadmap modular. La auditoría (CID_SCRIPT_ANALYSIS_PRO_AUDIT.md) identificó que Script Analysis no tenía pantalla propia (gap #2). Los commits 1 (enforcement) y 2 (export) ya están completados. Este commit es solo frontend — no toca Docker, migraciones, AGENTS.md ni contratos backend.

## Archivos afectados

### Creados
- `src_frontend/src/types/scriptAnalysis.ts` — tipos del módulo
- `src_frontend/src/api/scriptAnalysis.ts` — API client
- `src_frontend/src/pages/ScriptAnalysisProPage.tsx` — página principal
- `docs/product/CID_SCRIPT_ANALYSIS_PRO_FRONTEND.md` — documentación
- `directivas/cid_script_analysis_pro_frontend.md` — esta directiva

### Modificados
- `src_frontend/src/App.tsx` — +1 import, +1 ruta
- `src_frontend/src/pages/ProjectDetailPage.tsx` — +1 link en header
- `src_frontend/src/pages/ModulesCatalogPage.tsx` — helperText mejorado para script_analysis

## Entradas

- Endpoints backend existentes:
  - `POST /api/projects/{id}/analysis/run`
  - `GET /api/projects/{id}/analysis/summary`
  - `GET /api/projects/{id}/analysis/export?format=json|md`
  - `GET /api/projects/{id}`
- Patrón de página de proyecto: `ProjectFundingPage.tsx`
- Patrón de client API: `projects.ts`, `storyboard.ts`
- Tipos existentes: `modules.ts`, `user.ts`

## Salidas

- Página en `/projects/:projectId/script-analysis`
- API client con métodos: `runAnalysis`, `getSummary`, `exportAnalysis`, `getModuleStatus`
- Tipos: `ScriptAnalysisExportFormat`, `ScriptAnalysisStatus`, `ScriptAnalysisSummary`, `ScriptAnalysisExportPayload`
- Navegación contextual desde ProjectDetailPage y ModulesCatalogPage

## Flujo de trabajo

1. Crear tipos en `types/scriptAnalysis.ts`
2. Crear API client en `api/scriptAnalysis.ts` con blob download para export
3. Crear página `pages/ScriptAnalysisProPage.tsx`:
   - Carga proyecto + resumen de análisis
   - Estados: loading, error, blocked (403), empty, data
   - Botones: Analizar, Export JSON, Export MD
   - Secciones: resumen, qué entregas, módulos downstream
4. Añadir ruta en `App.tsx`
5. Añadir link en `ProjectDetailPage.tsx` header
6. Mejorar helperText en `ModulesCatalogPage.tsx`
7. Validar: npm run build, pytest backend legacy, git status
8. Documentar

## Validaciones

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"

# Frontend
cd src_frontend && npm run build

# Backend tests legacy
python -m pytest tests/unit/ -q
python -m pytest tests/integration/test_project_script_analysis_flow.py -q
python -m pytest tests/integration/test_script_analysis_export.py -q
git status --short
git diff --stat
```

## Casos borde

- **403 MODULE_ACCESS_BLOCKED**: La página detecta este error en carga de proyecto y muestra pantalla de bloqueo con link a planes. También se detecta en analyze y export.
- **Proyecto sin guion**: Los botones de análisis se deshabilitan. Empty state guía a cargar guion.
- **Análisis en progreso**: El botón "Analizar" se deshabilita durante el análisis. Polling cada 2s hasta completar.
- **Export sin análisis**: Los botones de export se deshabilitan si `hasAnalysis` es falso.
- **Blob download**: Se usa `window.URL.createObjectURL` con limpieza posterior. Compatible con todos los navegadores modernos.
- **ProyectoId ausente**: La página renderiza mensaje de error con link a `/projects`.

## Restricciones conocidas

- NO tocar backend, Docker, migraciones, AGENTS.md
- NO romper ProjectDetailPage — el link nuevo convive con los existentes
- NO eliminar flujos legacy — la nueva página complementa, no reemplaza, la pestaña de análisis en ProjectDetailPage
- Sin ESLint configurado en el proyecto — no validar con `npm run lint`
- Sin test runner frontend — no añadir tests frontend

## Errores aprendidos

- El error 403 MODULE_ACCESS_BLOCKED viene envuelto en `data.details.code` dentro de la respuesta de axios. La detección requiere navegar por `err.response.data.details.code`.
- Los nombres de archivo para export deben usar underscore (`CID_script_analysis_`) por consistencia con el backend.
- El análisis puede tardar tiempo — el polling se hace cada 2s, mismo patrón que ProjectDetailPage.

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
cd src_frontend && npm run build
git diff --stat
git status --short
```
