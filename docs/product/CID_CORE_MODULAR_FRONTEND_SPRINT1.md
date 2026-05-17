# CID Core Modular Frontend Sprint 1

## Pantallas creadas

- `src_frontend/src/pages/ModulesCatalogPage.tsx`
  - Nueva pantalla principal de catálogo modular.
  - Muestra plan actual, módulos disponibles, módulos bloqueados y CTA comercial.

## Servicios frontend añadidos

- `src_frontend/src/api/moduleCatalog.ts`
  - `getModuleCatalog()`
  - `getMyModules()`
  - `getModuleDetail(moduleKey)`

- `src_frontend/src/hooks/useModules.ts`
  - `useModuleCatalog()`
  - `useMyModules()`
  - `useModuleDetail(moduleKey)`

## Tipos añadidos

- `src_frontend/src/types/modules.ts`
  - `ModuleInfo`
  - `ModuleAccessInfo`
  - `ModuleCatalogResponse`
  - `UserModulesResponse`

## Componentes nuevos

- `src_frontend/src/components/modules/ModuleCard.tsx`
- `src_frontend/src/components/modules/ModuleStatusBadge.tsx`
- `src_frontend/src/components/modules/ModuleAccessBadge.tsx`
- `src_frontend/src/components/modules/ModulePackBadge.tsx`

## Endpoints consumidos

- `GET /api/modules/catalog`
- `GET /api/modules/me`
- `GET /api/modules/{module_key}`

## Navegación añadida

- Entrada nueva en sidebar: `Módulos`
- Ruta frontend nueva: `/modules`

## Módulos con CTA mapeado

- `core` -> `/projects`
- `script_analysis` -> `/projects`
- `pitch_deck` -> `/projects`
- `storyboard_ai` -> `/projects`
- `pipeline_builder` -> `/cid/pipeline-builder`
- `breakdown` -> `/projects`
- `budget_lite` -> `/projects`
- `legal_documents` -> `/documents`
- `funding_grants` -> `/projects`
- `delivery_distribution` -> `/projects`

## Módulos marcados como próximamente

- `production_manager_lite`
- `call_sheet`
- `postproduction`
- `sound_post_ai`

## Comportamiento UX

- Si `/api/modules/me` responde bien:
  - se separan `Disponibles en tu plan` y `Bloqueados / disponibles para ampliar`.
- Si `/api/modules/me` falla:
  - se hace fallback visual a `/api/modules/catalog` y se muestra modo informativo.
- Si falla `/api/modules/catalog`:
  - se muestra estado de error con reintento.

## Limitaciones conocidas

- Los CTAs de varios módulos todavía llevan a `/projects` porque su flujo real sigue siendo project-first.
- No hay enforcement backend por módulo todavía; esta pantalla solo comunica disponibilidad comercial.
- No hay pricing final por módulo en frontend; se muestra únicamente pack recomendado y activación comercial.
- Los módulos sin workspace claro se mantienen como `Próximamente` para no inventar navegación.

## Siguiente commit recomendado

- Aplicar navegación contextual por módulo desde dashboards y páginas de proyecto.
- Después, empezar enforcement backend quirúrgico con `require_module_access()` en rutas claras como Pitch Deck, Funding, Budget y Storyboard.
