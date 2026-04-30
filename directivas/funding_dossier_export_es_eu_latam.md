# FUNDING DOSSIER EXPORT ES/EU/LATAM MVP

## Objetivo
- Consolidar en un dossier exportable el perfil financiable, breakdown, presupuesto, funding gap y mejores convocatorias institucionales.
- Reutilizar el stack actual de HTML/Jinja/WeasyPrint y la persistencia de deliverables ya existente.
- Mantener salida JSON usable + PDF exportable + persistencia tenant-safe.

## Arquitectura minima
- Servicio central: `funding_dossier_service`.
- Render PDF: mismo stack `Jinja2 + WeasyPrint` ya usado por presentation export.
- Persistencia: `delivery_service.create_project_file_deliverable`.
- Seguridad: mismas reglas project/tenant ya existentes en rutas funding.

## Inputs reutilizados
- `funding_matcher_service`: profile, matches, checklist.
- `budget_estimator_service`: presupuesto y top sheet.
- `project_funding_service`: resumen privado y funding gap.
- `production_breakdowns`: snapshot de produccion.
- `deliverables`: almacenamiento y descarga segregada por `organization_id`.

## JSON minimo del dossier
- `project_profile`
- `production_breakdown_summary`
- `budget_summary`
- `private_funding_summary`
- `funding_match_summary`
- `top_matches`
- `checklist`
- `generated_at`
- `dossier_version`

## Reglas de presentacion
- Priorizar solo `high` y `medium` en recomendaciones principales.
- Mostrar `low` y `blocked` como senales de cautela, no como recomendacion.
- Exponer funding gap actual y optimista.
- Explicar bloqueos, documentos faltantes y siguientes acciones.

## Endpoints MVP
- `GET /api/projects/{project_id}/funding/dossier`
- `GET /api/projects/{project_id}/funding/dossier/export/pdf`
- `POST /api/projects/{project_id}/funding/dossier/export/pdf/persist`

## Persistencia
- `format_type = FUNDING_DOSSIER_PDF`
- categoria de storage: `funding_dossier_pdf`
- `delivery_payload` incluye referencia al JSON consolidado y manifest summary

## Seguridad
- Tenant-safe absoluto por `project_id + organization_id`.
- Tenant B no puede ver, exportar ni persistir el dossier de A.
- Admin conserva acceso segun reglas actuales del proyecto.

## Cierre esperado
- JSON dossier usable por proyecto.
- PDF valido y descargable.
- Deliverable persistido y descargable.
- Sin regresion en matcher, catalogo, presupuesto ni presentation export.

## Metadata
- created: 2026-04-22
- status: MVP
- owner: full-stack/document export
