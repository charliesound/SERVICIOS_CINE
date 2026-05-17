# CID Core Modular Backend Sprint 1

## Que se ha implementado

- Catalogo backend central de modulos en `src/config/modules.yml`.
- Servicio singleton de lectura y validacion en `src/services/module_catalog_service.py`.
- Endpoints de solo lectura para catalogo modular en `src/routes/module_catalog_routes.py`.
- Schemas de respuesta para catalogo y acceso por plan en `src/schemas/module_catalog_schema.py`.
- Helper reusable de enforcement modular en `src/dependencies/module_access.py`.
- Integracion minima con `src/config/plans.yml` mediante features `module_*` sin eliminar features heredadas.

## Modulos definidos

- `core`
- `script_analysis`
- `pitch_deck`
- `storyboard_ai`
- `pipeline_builder`
- `breakdown`
- `budget_lite`
- `production_manager_lite`
- `call_sheet`
- `legal_documents`
- `funding_grants`
- `postproduction`
- `sound_post_ai`
- `delivery_distribution`

## Endpoints nuevos

- `GET /api/modules/catalog`
  - Devuelve todos los modulos visibles del catalogo.
- `GET /api/modules/me`
  - Devuelve modulos disponibles y bloqueados segun el plan efectivo del usuario.
  - Si no hay usuario resuelto, usa fallback `free`.
- `GET /api/modules/{module_key}`
  - Devuelve detalle de un modulo concreto.

## Relacion con plans.yml

- El catalogo no sustituye a `plans.yml`; lo complementa.
- `plans.yml` sigue siendo la fuente de verdad de planes, limites y features comerciales.
- Cada modulo ahora puede mapearse a una feature `module_*`.
- `studio` y `enterprise` siguen aprovechando `all_lower_features`, y el servicio modular expande esas herencias al resolver acceso.
- `core` queda habilitado por `default_enabled: true` para mantener compatibilidad y no introducir bloqueos inesperados.

## Como se bloquearan modulos en futuros commits

- Este commit no aplica enforcement masivo sobre endpoints existentes.
- El helper `require_module_access(module_key)` ya permite empezar a proteger rutas de forma gradual.
- El siguiente paso recomendado es aplicar enforcement solo en superficies claras y no ambiguas:
  - routes de Pitch Deck
  - routes de Funding
  - routes de Budget
  - routes de Storyboard
  - dashboard/catalogos de modulos
- Antes de proteger rutas legacy, conviene decidir la matriz exacta `plan -> modulo -> endpoint` para no romper demos actuales.

## Limites conocidos

- El catalogo modular es de lectura; todavia no controla menus frontend.
- Los endpoints existentes siguen funcionando como antes salvo los nuevos endpoints de catalogo.
- No hay migraciones ni nuevas tablas en este sprint.
- La resolucion de acceso modular se basa en plan efectivo y dependencias declaradas, no en overrides por organizacion o licencias individuales.
- `GET /api/modules/me` hace fallback a `free` si no puede resolver usuario autenticado; esto es deliberado para mantener una respuesta segura y estable.

## Siguiente commit recomendado

- Frontend menu/pantalla de modulos.
- Objetivo: consumir `GET /api/modules/catalog` y `GET /api/modules/me` para pintar tarjetas, estados bloqueado/disponible y narrativa comercial por modulo.
