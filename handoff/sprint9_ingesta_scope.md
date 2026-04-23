# Sprint 9 - Ingesta Federada Scope

## 1) Contexto de apertura

Sprint 8 queda en baseline tecnica PASS (backend importable/arrancable y frontend buildable).
Sprint 9 abre un modulo nuevo en AILinkCinema Core, sin mezclar cambios de Sprint 8.

Este documento define solo alcance de Sprint 9. No habilita implementacion automatica por si mismo.

## 2) Objetivo de Sprint 9

Construir un MVP operativo de:

- Ingesta federada sobre storage del cliente (sin mover material si no es necesario).
- Registro de fuentes, autorizaciones, watch paths, scans y assets.
- Ingesta documental multiformato con extraccion y clasificacion asistida.
- Revision humana obligatoria antes de consolidar estructuras documentales.
- Reportes estructurados (camera, sound, script, director) conectados a proyecto.

## 3) Alcance incluido

### 3.1 Ingesta federada

- Storage sources: alta, listado, detalle, edicion.
- Validacion de conectividad.
- Autorizacion y revocacion explicita del cliente.
- Watch paths por source.
- Escaneo manual.
- Indexacion basica de assets.
- Trazabilidad por eventos.

### 3.2 Document understanding MVP

- Formatos: JPG, PNG, HEIC, PDF, DOC, DOCX, TXT, CSV, XLS, XLSX.
- Registro de documentos.
- Extraccion textual/tabular best-effort.
- OCR solo si runtime disponible; si no, estado parcial explicito.
- Clasificacion documental sugerida.
- Propuesta de payload estructurado.
- Aprobacion humana del payload.

### 3.3 Reportes estructurados

- camera_reports
- sound_reports
- script_notes
- director_notes

Creacion manual y opcion de derivacion desde documento aprobado.

## 4) No alcance (fuera de Sprint 9)

- Integraciones por API propietaria de marcas NAS (Synology/QNAP/etc).
- Automatizacion avanzada con IA generativa de alta precision.
- Polling complejo continuo con optimizacion avanzada.
- Migracion de DB a Postgres o storage a S3 (solo preparacion de compatibilidad).
- Refactor global de UI/arquitectura no necesario para MVP.

## 5) Dependencias ya resueltas de Sprint 8

- Backend base en FastAPI operativo.
- Frontend base en React/Vite buildable.
- Rutas de auth disponibles y cliente frontend con interceptor 401.
- Navegacion principal estable para extender con nuevas paginas.

## 6) Restricciones tecnicas para Sprint 9

- No mezclar CID con logica de ingesta.
- Mantener arquitectura monolitica actual (sin microservicios).
- Implementacion incremental y validable por fases.
- Seguridad por ownership de organization/project en cada endpoint nuevo.

## 7) Riesgos principales a vigilar

- Prometer "cualquier NAS" sin limitar a protocolos/paths soportados en MVP.
- Escaneos lentos en rutas grandes sin filtros basicos.
- Falta de validacion de scope de rutas (riesgo de lectura fuera de autorizacion).
- OCR no robusto en entorno domestico.
- Deteccion de formato/doc type con baja precision sin revision humana.

## 8) Primer entregable tecnico de Sprint 9

Vertical slice minimo: backend Fase 1 de `storage_sources`.

Incluye:

- Modelo + schema + rutas:
  - POST /api/storage-sources
  - GET /api/storage-sources
  - GET /api/storage-sources/{source_id}
  - POST /api/storage-sources/{source_id}/validate
- Ownership minimo y evento de auditoria create/validate.
- Validacion por comandos (import, startup, OpenAPI, curl).
