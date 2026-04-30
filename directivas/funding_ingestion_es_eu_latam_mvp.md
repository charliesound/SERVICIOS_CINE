# FUNDING INGESTION ES/EU/LATAM MVP

## Objetivo
- Construir el catalogo estructurado de ayudas institucionales para Espana, Europa e Iberoamerica/LatAm.
- Dejar el backend listo para carga manual admin, seeders y futura ingestión automatizada.
- Mantener este bloque separado del funding matcher, billing, reporting y dashboard final.

## Alcance cerrado
- Fuentes iniciales: ICAA, BOE, Creative Europe / MEDIA, Eurimages, Ibermedia.
- CRUD admin para `funding_sources` y `funding_calls`.
- Lectura publica controlada para catalogo base reutilizable por capas futuras.
- Seeder institucional idempotente con registros representativos reales.

## Modelo de datos

### funding_sources
- `id`, `code`, `name`, `agency_name`, `official_url`, `description`
- `region_scope`, `country_or_program`
- `source_type`, `verification_status`, `is_active`
- `last_synced_at`, `created_at`, `updated_at`

### funding_calls
- Hard schema obligatorio:
  - `id`, `source_id`, `title`, `region_scope`, `country_or_program`, `agency_name`
  - `official_url`, `status`, `open_date`, `close_date`
  - `opportunity_type`, `phase`
  - `max_award_per_project`, `total_budget_pool`, `currency`
  - `verification_status`, `created_at`, `updated_at`
- Soft schema:
  - `eligibility_json`, `requirements_json`, `collaboration_rules_json`
  - `point_system_json`, `eligible_formats_json`, `notes_json`
- Compatibilidad legacy:
  - se mantienen campos previos (`region`, `territory`, `deadline`, `amount_*`, `eligibility_summary`) para no romper matcher/dossier/alertas existentes.

### funding_requirements
- `id`, `call_id`, `category`, `requirement_text`, `is_mandatory`, `display_order`
- `notes_json`, `created_at`, `updated_at`

## Clasificaciones cerradas

### region_scope
- `spain`
- `europe`
- `iberoamerica_latam`

### opportunity_type
- `development`
- `co-development`
- `co-production`
- `production`
- `distribution_circulation`
- `training`
- `industry_support`
- `festival_market`

### phase
- `writing`
- `development`
- `production`
- `postproduction`
- `distribution`

### status
- `open`
- `upcoming`
- `closed`
- `archived`

## Endpoints

### Admin protegido
- `GET /api/admin/funding/sources`
- `POST /api/admin/funding/sources`
- `GET /api/admin/funding/calls`
- `POST /api/admin/funding/calls`
- `PATCH /api/admin/funding/calls/{call_id}`
- `GET /api/admin/funding/calls/{call_id}`
- `POST /api/admin/funding/sync/seed`
- `POST /api/admin/funding/sync/mock-refresh`

### Publico read-only
- `GET /api/funding/opportunities`
- `GET /api/funding/opportunities/{id}`

## Seguridad
- Escritura restringida a `TenantContext.is_admin == True`.
- El catalogo institucional no mezcla `organization_id` ni datos privados de productor.
- La lectura publica expone solo catalogo institucional reutilizable.
- Los modelos privados existentes (`project_funding_sources`, `private_funding_sources`) siguen aislados por tenant.

## Seeder institucional
- Registros representativos incluidos:
  - ICAA ayuda de produccion
  - BOE referencia audiovisual oficial
  - Creative Europe MEDIA development line
  - Eurimages coproduction line
  - Ibermedia coproduction line
- El seeder es idempotente y soporta `force` para refresco controlado.

## No hacer en este bloque
- Funding matcher
- Dashboard final de oportunidades
- Billing / tiers / reporting
- Dossier export especifico de ayudas
- Conectores documentales privados
- Scoring semantico complejo

## Validacion esperada
- CRUD admin operativo
- Seed institucional operativo
- Lectura publica 200
- Compatibilidad ES / EU / LATAM sin hacks por region
- Sin regresion en budget / presentation / export / builder

## Metadata
- created: 2026-04-22
- status: MVP
- owner: backend/data architecture
