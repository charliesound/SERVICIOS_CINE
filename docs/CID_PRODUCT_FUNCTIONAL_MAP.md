# CID Product Functional Map

## A. Visión General

**CID (Cine Infrastructure Database)** es una plataforma integral para acompañar un proyecto audiovisual desde el guion hasta la venta y la postproducción.

## B. Módulos Principales

### 1. CID Script Intelligence (EXISTE - PARTIAL)

**Backend:** `script_intake_service.py`
**Frontend:** En `ProjectDetailPage.tsx` / `NewProjectPage.tsx`

Funcionalidades:
- Análisis de guion
- Extracción de escenas, personajes, localizaciones
- Tone detection
- Scoring de potencial comercial

**Estado:** PARTIAL — Análisis activo, integración completa en proceso.

### 2. CID Production Breakdown (STUB)

**Backend:** No existe servicio dedicado
**Frontend:** No existe página

Funcionalidades requeridas:
- Desglose por escenas
- Requisitos de localizaciones
- Necesidades de personajes
- VFX/Sonido/Arte

**Estado:** MISSING — Necesita desarrollo.

### 3. CID Budget Estimator (EXISTE)

**Backend:** `budget_estimator_service.py`
**Backend Route:** `budget_routes.py`

Funcionalidades:
- Estimación de presupuesto por partidas
- Costes de producción
- Postproducción

**Estado:** CLOSED — Servicio operacional.

### 4. CID Funding & Grants (EXISTE - PARTIAL)

**Backend:** 
- `funding_routes.py`
- `funding_catalog_routes.py`
- `funding_ingestion_service.py`
- `funding_matcher_service.py`
- `funding_dossier_service.py`
- `funding_alert_service.py`

**Frontend:** `ProjectFundingPage.tsx`

Funcionalidades:
- Catálogo de ayudas
- Búsqueda de oportunidades
- Scoring de encaje
- Documentación

**Estado:** PARTIAL — Catálogo existe, scoring limitado.

### 5. CID Producer Pack (EXISTE - PARTIAL)

**Backend:** 
- `project_document_service.py`
- `presentation_service.py`

**Frontend:** `ProjectDetailPage.tsx`

Funcionalidades:
- Dossier para productores
- Logline, sinopsis, nota de intención
- Presupuesto estimado
- Storyboard

**Estado:** PARTIAL — PDF export existe.

### 6. CID Storyboard (EXISTE - CLOSED)

**Backend:** 
- `storyboard_service.py`
- `storyboard_routes.py`

**Frontend:** `StoryboardBuilderPage.tsx`

**Estado:** CLOSED — Completo y operacional.

### 7. CID Distribution Pack (MISSING)

**Backend:** No existe servicio dedicado
**Frontend:** No existe página

Funcionalidades requeridas:
- Presentación a distribuidoras
- Propuesta comercial
- Comparables

**Estado:** MISSING — Necesita desarrollo.

### 8. CID Cinemas & Exhibitors Pack (MISSING)

**Backend:** No existe servicio dedicado
**Frontend:** No existe página

**Estado:** MISSING — Necesita desarrollo.

### 9. CID Platforms Pack (MISSING)

**Backend:** No existe servicio dedicado
**Frontend:** No existe página

**Estado:** MISSING — Necesita desarrollo.

### 10. CID CRM Comercial (STUB)

**Backend:** 
- `producer_catalog.py` (catálogo de productores)
- `demo_service.py` (demo requests)

**Frontend:** 
- `ProducerPage.tsx` NO EXISTE
- `ReportsPage.tsx` (reportsrud)

Funcionalidades:
- Contactos de productoras
- Historial de comunicación
- Estado de oportunidades

**Estado:** STUB — Catálogo parcial existe.

### 11. CID Editorial (EXISTE - CLOSED)

**Backend:** 
- `editorial_routes.py`
- `fcpxml_export_service.py`
- `assembly_service.py`
- `editorial_reconciliation_service.py`
- `take_scoring_service.py`
- `audio_metadata_service.py`
- `davinci_platform_package_service.py`

**Frontend:** `EditorialAssemblyPage.tsx`

Funcionalidades:
- Media scan/index
- Document ingestion
- Takes & Scoring
- AssemblyCut
- FCPXML export
- DaVinci multiplatform

**Estado:** CLOSED — Flujo completo validado.

### 12. CID Media Scan/Index (EXISTE - CLOSED)

**Backend:** 
- `ingest_scan_service.py`
- `ingest_service.py`

**Frontend:** 
- `IngestScansPage.tsx`
- `MediaAssetsPage.tsx`

**Estado:** CLOSED — Escanea sin mover media.

### 13. CID Document Ingestion (EXISTE - CLOSED)

**Backend:** 
- `document_understanding_service.py`
- `document_service.py`

**Frontend:** 
- `DocumentsPage.tsx`
- `ReportsPage.tsx`

**Estado:** CLOSED — PDF/CSV ingestion operacional.

## C. Flujo Principal

```
GUION
  ↓
ANÁLISIS (Script Intelligence)
  ↓
DESGLOSE (Production Breakdown) ← MISSING
  ↓
PRESUPUESTO (Budget Estimator) ← CLOSED
  ↓
AYUDAS (Funding & Grants) ← PARTIAL
  ↓
STORYBOARD ← CLOSED
  ↓
PITCH PRODUCTOR (Producer Pack) ← PARTIAL
  ↓
PITCH DISTRIBUCIÓN ← MISSING
  ↓
PITCH CINES/PLATAFORMAS ← MISSING
  ↓
CRM COMERCIAL ← STUB
  ↓
RODAJE
  ↓
REPORTS (Ingest)
  ↓
RECONCILIACIÓN (Editorial)
  ↓
SCORING
  ↓
ASSEMBLYCUT
  ↓
FCPXML / DAVINCI ← CLOSED
```

## D. Matriz de Estado

| Módulo | Backend | Frontend | Estado | Prioridad |
|-------|--------|---------|--------|----------|
| Script Intelligence | script_intake | ProjectDetail | PARTIAL | Media |
| Production Breakdown | — | — | MISSING | Alta |
| Budget Estimator | budget_estimator | — | CLOSED | — |
| Funding & Grants | funding_* | ProjectFunding | PARTIAL | Media |
| Producer Pack | project_document | ProjectDetail | PARTIAL | Media |
| Storyboard | storyboard | StoryboardBuilder | CLOSED | — |
| Distribution Pack | — | — | MISSING | Alta |
| Cinemas Pack | — | — | MISSING | Media |
| Platforms Pack | — | — | MISSING | Media |
| CRM Comercial | producer_catalog | — | STUB | Alta |
| Editorial | editorial_* | EditorialAssembly | CLOSED | — |
| Media Scan | ingest_* | IngestScans | CLOSED | — |
| Doc Ingestion | document_* | Documents | CLOSED | — |

## E. Gaps Críticos

1. **Production Breakdown** — Desglose completo no existe
2. **Distribution Pack** — Presentación comercial no existe
3. **CRM** — Contactos y oportunidades no integrados
4. **Funding Scoring** — Matching limitado

## F. Recomendaciones

### Sprint Siguiente: PRODUCT DASHBOARD UNIFICADO

- Dashboard mostrando estado del proyecto en todas las fases
- Accesos rápidos a módulos existentes
- Progreso visual

### Sprint Después: BUDGET ESTIMATOR FROM SCRIPT

- Presupuesto automático desde análisis de guion
- Partidas configurables
- Export PDF/XLSX

### Sprint Después: FUNDING & GRANTS HARDENING

- Scoring de encaje mejorado
- Checklist documental
- Alertas de plazos