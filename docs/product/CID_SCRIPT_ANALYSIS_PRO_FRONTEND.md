# CID Script Analysis Pro — Frontend

## Resumen ejecutivo

Commit 3 del Sprint 2. Se creó una experiencia frontend propia para CID Script Analysis Pro: página dedicada, API client, tipos, ruta, navegación contextual desde ProjectDetailPage y actualización del CTA en ModulesCatalogPage.

**Estado anterior**: Script Analysis solo existía como tabs embebidas en `ProjectDetailPage.tsx`. No había workspace dedicado, onboarding propio ni ruta específica.

**Estado actual**: Ruta `/projects/:projectId/script-analysis` con página propia que incluye análisis, export, estados loading/error/blocked y conexión con módulos downstream.

---

## Ruta creada

| Ruta | Página | Propósito |
|------|--------|-----------|
| `/projects/:projectId/script-analysis` | `ScriptAnalysisProPage.tsx` | Workspace dedicado del módulo |

## Archivos creados

| Archivo | Propósito |
|---------|-----------|
| `src/types/scriptAnalysis.ts` | Tipos: `ScriptAnalysisExportFormat`, `ScriptAnalysisStatus`, `ScriptAnalysisSummary`, `ScriptAnalysisExportPayload` |
| `src/api/scriptAnalysis.ts` | API client: `runAnalysis()`, `getSummary()`, `exportAnalysis()`, `getModuleStatus()` |
| `src/pages/ScriptAnalysisProPage.tsx` | Página principal del módulo (~280 líneas) |

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `src/App.tsx` | +1 import de `ScriptAnalysisProPage`, +1 ruta `/projects/:projectId/script-analysis` |
| `src/pages/ProjectDetailPage.tsx` | +1 link "Script Analysis Pro" en header junto a Dashboard/Funding |
| `src/pages/ModulesCatalogPage.tsx` | HelperText actualizado para `script_analysis` mencionando el workspace dedicado |

---

## Página: ScriptAnalysisProPage

### Secciones

1. **Header comercial** — Título "CID Script Analysis Pro", subtítulo, badge de estado (análisis completado / sin análisis)
2. **Back navigation** — Link "Volver al proyecto"
3. **Action cards** — 3 botones principales:
   - "Analizar guion" (POST `/analysis/run`, polling hasta completar)
   - "Exportar JSON" (GET `/analysis/export?format=json`, descarga blob)
   - "Exportar Markdown" (GET `/analysis/export?format=md`, descarga blob)
4. **Resumen del análisis** — Grid con escenas, personajes, localizaciones, secuencias (si existe)
5. **Empty state** — Si no hay análisis, guía al usuario a cargar guion o analizar
6. **"Qué entrega este análisis"** — Lista de 10 entregables del módulo
7. **Conecta con otros módulos** — Breakdown, Pitch Deck, Storyboard, Budget Lite

### Estados

| Estado | Condición | UX |
|--------|-----------|----|
| Loading | Carga inicial de proyecto + análisis | Spinner + mensaje |
| Error | Error de red o backend | Mensaje + botón reintentar |
| Blocked | 403 MODULE_ACCESS_BLOCKED | Lock icon + link a planes |
| Ready (empty) | Proyecto cargado, sin análisis | Guía: subir guion o analizar |
| Ready (data) | Análisis completado | Grid de resumen + botones export |

### Export behavior

- JSON: `GET /api/projects/{projectId}/analysis/export?format=json` → blob → `CID_script_analysis_{projectId}.json`
- Markdown: `GET /api/projects/{projectId}/analysis/export?format=md` → blob → `CID_script_analysis_{projectId}.md`

Ambos se descargan como archivo adjunto vía `window.URL.createObjectURL`.

---

## Navegación contextual

### Desde ProjectDetailPage
Se añadió un link "Script Analysis Pro" en el header de la página de detalle del proyecto, junto a los enlaces existentes de Dashboard, Funding, Premontaje, etc. Usa icono `Sparkles` y color `text-amber-300` para destacar.

### Desde ModulesCatalogPage
El CTA de `script_analysis` mantenía `href: '/projects'` (correcto, no hay projectId en contexto de catálogo) pero se actualizó el helperText para mencionar que desde cualquier proyecto se accede al workspace dedicado.

---

## Endpoints consumidos

| Método | Endpoint | Uso |
|--------|----------|-----|
| POST | `/api/projects/{id}/analysis/run` | Lanzar análisis |
| GET | `/api/projects/{id}/analysis/summary` | Consultar estado/resumen |
| GET | `/api/projects/{id}/analysis/export?format=json\|md` | Exportar análisis |
| GET | `/api/projects/{id}` | Obtener datos del proyecto |

---

## Tests y validaciones

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"

# Frontend build
cd src_frontend && npm run build

# Backend tests legacy
python -m pytest tests/unit/ -q
python -m pytest tests/integration/test_project_script_analysis_flow.py -q
python -m pytest tests/integration/test_script_analysis_export.py -q
```

---

## Limitaciones conocidas

1. **Sin ESLint configurado**: `npm run lint` no pasa porque no hay configuración de ESLint en el proyecto (devDependencies no incluye eslint config). El build con `tsc && vite build` valida tipos y compilación.
2. **Polling manual**: El análisis usa `setTimeout` recursivo para polling (cada 2s). No hay WebSocket ni Server-Sent Events. Esto coincide con el patrón de `ProjectDetailPage.tsx`.
3. **Sin test runner frontend**: El proyecto no tiene configurado Vitest ni Jest. No se añadieron tests frontend para no añadir dependencias.
4. **Sin manejo de cancelación**: No hay abort controller en las solicitudes de export. Mejora futura.
5. **Export sin feedback de progreso**: El blob download no muestra progreso de descarga. Es instantáneo para payloads pequeños.

---

## Siguiente commit recomendado

**Commit 4 — Landing / demo guiada del módulo**

Crear una página de demostración de Script Analysis Pro con datos semilla, permitiendo al usuario explorar el módulo sin necesidad de tener un proyecto real con guion cargado. Esto cierra el gap #4 de la auditoría.
