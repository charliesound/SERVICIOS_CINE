# Sprint 9 - Execution Order

## Objetivo

Definir orden de implementacion en pasos pequenos, verificables y sin mezclar alcance.

## Regla de control

No iniciar una fase nueva hasta validar la anterior con:

1. import check backend
2. backend startup
3. frontend build (si aplica)
4. smoke minimo de endpoints/paginas de la fase

## Fase 1 - Backend Ingesta Federada (minimo)

### Entregables

- Modelos/tablas:
  - storage_sources
  - storage_authorizations
  - storage_watch_paths
  - ingest_scans
  - media_assets
  - asset_links
  - ingest_events
- Schemas pydantic minimos
- Servicios minimos:
  - validar source
  - normalizar ruta
  - scan manual
  - indexacion basica
  - trazabilidad
- Rutas API de storage/scans/assets de fase 1

### Validacion salida de fase

- `python -c "import app"`
- backend arranca
- `/docs` contiene endpoints de fase 1
- curl happy path: create source -> validate -> authorize -> watch path -> scan -> list assets

## Fase 2 - UI Ingesta Federada

### Entregables

- Rutas frontend de storage sources, scans, assets
- Pagina list/detail de source
- Formularios: create/edit/validate/authorize/revoke/watch-path/scan
- Pagina list/detail de assets
- Formularios: edit/classify/link/archive
- Filtros y badges de estado

### Validacion salida de fase

- `npm run build`
- Navegacion funcional desde menu principal
- Flujo UI conectado a API real (sin hardcodes)

## Fase 3 - Backend Documental

### Entregables

- Modelos/tablas:
  - document_assets
  - document_extractions
  - document_classifications
  - document_structured_data
  - document_links
- Rutas `/api/ingest/documents*`
- Extraccion multimformato best-effort
- Clasificacion + structure + approve
- Eventos audit

### Validacion salida de fase

- import/startup backend
- smoke por formatos clave: JPG/PDF/DOCX/TXT/CSV/XLSX

## Fase 4 - UI Documental + Revision Humana

### Entregables

- Paginas list/detail/review de documentos
- Acciones: upload/edit/extract/classify/structure/approve
- Vista texto extraido + preview tabular + payload estructurado
- Filtros y badges

### Validacion salida de fase

- frontend build
- flujo E2E documental con aprobacion humana

## Fase 5 - Reportes Estructurados

### Entregables

- Modelos/schemas/rutas de:
  - camera_reports
  - sound_reports
  - script_notes
  - director_notes
- UI minima list/create/edit
- Filtros por proyecto/dia/escena/toma

### Validacion salida de fase

- CRUD por cada tipo
- referencia opcional a document_asset_id y media_asset_id

## Secuencia de trabajo recomendada por bloques de commit

1. DB + models + schemas (fase actual)
2. services
3. routes + registro en app
4. smoke tecnico
5. frontend api/types
6. frontend pages/components
7. smoke funcional E2E

## Criterio de stop

Si una fase rompe baseline (import/startup/build), parar y reparar antes de continuar.
