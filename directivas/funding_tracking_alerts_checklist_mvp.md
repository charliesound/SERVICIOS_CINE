# Directiva: Funding Tracking, Alerts & Checklist MVP

## Objetivo
Transformar el dashboard de oportunidades en un pipeline operativo real con:
- Tracking de oportunidades
- Checklist interactivo
- Alertas in-app persistidas
- Autocompletado básico desde documentos/RAG
- Vista "Mis solicitudes"

## Alcance Estricto
- Tracking de oportunidad
- Checklist interactivo
- Alertas in-app persistidas
- Autocompletado básico desde documentos/RAG
- Vista "Mis solicitudes"
- Sin automatización de aplicación
- Sin conectores externos
- Sin billing

## Decisión de Modelo
No crear entidad "FinancialOpportunity" nueva. Reutilizar:
- `funding_calls`
- `project_funding_matches`

Crear tablas mínimas necesarias:
1. `opportunity_trackings`
2. `requirement_checklist_items`
3. `notifications`

### Modelo: opportunity_trackings
- id (PK)
- project_id (FK)
- organization_id (FK)
- funding_call_id (FK)
- project_funding_match_id (FK, opcional)
- status (interested, gathering_docs, ready, submitted, rejected, won, archived)
- priority
- owner_user_id (opcional)
- notes
- created_at
- updated_at

### Modelo: requirement_checklist_items
- id (PK)
- tracking_id (FK)
- organization_id (FK)
- label
- requirement_type
- is_fulfilled (boolean)
- auto_detected (boolean)
- linked_project_document_id (opcional)
- evidence_excerpt (opcional)
- due_date (opcional)
- notes
- created_at
- updated_at

### Modelo: notifications
- id (PK)
- organization_id (FK)
- project_id (FK)
- tracking_id (FK, opcional)
- level (info, warning, critical)
- title
- body
- is_read
- created_at

## Backend - Tracking
Endpoints mínimos en `project_funding_routes.py`:
- POST /api/projects/{project_id}/funding/tracking
- GET /api/projects/{project_id}/funding/tracking
- GET /api/projects/{project_id}/funding/tracking/{tracking_id}
- PATCH /api/projects/{project_id}/funding/tracking/{tracking_id}
- DELETE /api/projects/{project_id}/funding/tracking/{tracking_id}

Comportamiento:
- Crear tracking a partir de una oportunidad/match
- Evitar duplicados activos equivalentes
- Permitir cambio de estado
- Permitir notas simples

## Backend - Checklist
Endpoints:
- GET /api/projects/{project_id}/funding/tracking/{tracking_id}/checklist
- PATCH /api/projects/{project_id}/funding/tracking/{tracking_id}/checklist/{item_id}

Al crear tracking:
- Generar checklist inicial desde:
  - missing_requirements del matcher
  - blocking_reasons si aplica
  - requirements estructurados de la convocatoria si existen
- Autocompletado MVP:
  - Intentar enlazar checklist con ProjectDocument y/o evidencia RAG
  - Si se detecta documento/fragmento útil: marcar auto_detected = true
  - Si confianza suficiente: opcionalmente is_fulfilled = true
  - Si no hay confianza suficiente: dejar evidencia sugerida pero no afirmar cumplimiento

## Backend - Alertas
Endpoints:
- GET /api/projects/{project_id}/funding/notifications
- PATCH /api/projects/{project_id}/funding/notifications/{notification_id}/read

Base de job/check diario o función reusable que:
- Revise trackings activos
- Detecte deadlines próximas
- Genere notificaciones:
  - warning si faltan <= 14 días
  - critical si faltan <= 7 días
- Evite duplicados obvios

Reutilizar infraestructura de jobs existente si está disponible.

## Frontend - Dashboard / Tracking
Extender dashboard actual:
- Convertir stub "Trackear" en acción real
- Feedback claro al usuario
- Refresco de estado tras crear tracking

Vista nueva: "Mis solicitudes"
- Ruta: /projects/:projectId/funding/pipeline (o equivalente)
- Mostrar:
  - Agrupación por estado
  - Lista o kanban simple
  - Deadlines visibles
  - Acceso al checklist
  - Alertas relevantes

## Frontend - Checklist
Detalle de solicitud con:
- Estado actual
- Resumen de oportunidad
- Checklist interactivo
- Indicador visual:
  - Cumplido
  - Sugerido por documentos
  - Faltante
- Deadline y urgencia

Prioridad: claridad, acción, estado visual.

## Frontend - Alertas
Panel sencillo de alertas:
- En sección funding o panel simple accesible
- Mostrar:
  - Unread/read
  - Level
  - Mensaje
  - Vínculo al tracking correspondiente

## Seguridad
- Tenant B no puede ver tracking/checklist/alertas de A
- Filtros por organization_id y project_id en todas las consultas
- No romper auth ni ownership actuales

## Validación
Tests de integración estables que validen:
- Crear tracking desde oportunidad
- Checklist generado
- Autocompletado básico usando documentos/RAG cuando exista evidencia
- Cambio de estado
- Generación de alertas por deadline
- Tenant B bloqueado
- No regresión en:
  - Dashboard funding
  - Matcher
  - Dossier
  - Presentation

## No hacer todavía
- Aplicación automática a convocatorias
- Envío de emails masivo
- Conectores Drive/Dropbox
- Matcher v3
- Billing
- Automatización documental compleja

## Criterios de aceptación
- Existe pipeline de oportunidades trackeadas
- Existe checklist interactivo
- Existen alertas in-app persistidas
- Hay sinergia básica con documentos/RAG
- Tenant-safe confirmado
- Listo para siguiente bloque de conectores o automatización posterior

## Próximos pasos
1. Implementar modelos de base de datos
2. Añadir endpoints backend
3. Extender frontend con nuevas vistas y componentes
4. Añadir pruebas de integración
5. Documentar cambios