# CID Core Scope Feature Flags - PRODUCT.2A

**Date:** 2026-05-21
**Workspace:** `/opt/SERVICIOS_CINE`
**Status:** GO

## Objective

Complete CID Core commercial scoping so non-core post/audio/restoration surfaces are hidden from customer-facing catalogues while internal modules, routes and workflows remain available for future lab products.

## Flags Added

- Backend: `feature_cid_core_scope = True` in `src/core/config.py`.
- Frontend: `CID_CORE_SCOPE_ENABLED = true` in `src_frontend/src/config/cidCoreScope.ts`.

## Backend Modules Hidden

Catalog keys checked in `src/config/modules.yml`:

- `dubbing`: not present.
- `dubbing_audio`: not present.
- `dubbing_take`: not present.
- `dubbingtake_studio_ai`: not present.
- `restoration`: not present.
- `image_restoration`: not present.
- `restoration_lab`: not present.
- `sound_post_ai`: present and hidden from public visible module lists when `feature_cid_core_scope=true`.
- `sound_repair`: not present.

Final hidden backend module set:

- `sound_post_ai`

The internal module catalogue remains unchanged at 14 modules. Public visible catalogue returns 13 modules under CID Core scope.

## Frontend Slugs Hidden

Real slugs checked in `src_frontend/src/data/solutionsContent.ts`:

- `cid`
- `script-breakdown`
- `storyboard`
- `production-planner`
- `dubbing`
- `sound-post`
- `promo-video`
- `vfx`
- `director`
- `producer`

No `restoration`, `image-restoration` or `restoration-lab` slugs exist today.

Final hidden customer-facing solution slugs:

- `dubbing`
- `sound-post`

## Frontend Impact

- `/solutions` filters lab slugs from the visible customer catalogue.
- Direct `/solutions/dubbing` and `/solutions/sound-post` routes remain reachable but are degraded to `Laboratorio interno / futuro producto` with `noindex, nofollow`.
- Workflow category `dubbing` is hidden from the visible workflow browser.
- Pipeline modes `dubbing` and `sound` are hidden from the visible selector.
- `PipelinePromptBox` uses only visible options, falls back to a safe visible mode when the current mode is hidden, and never renders an empty select.

## Backend Impact

- `get_visible_modules()`, `get_modules_for_plan()` and `get_locked_modules_for_plan()` no longer expose `sound_post_ai` when `feature_cid_core_scope=true`.
- `get_module_catalog()` and `get_module_by_key()` still retain `sound_post_ai` internally.
- No backend module definitions were deleted.
- No persistence, tenancy, authorization or ComfyUI registry behavior was changed.

## Routes Not Removed

No routes were deleted. The following non-core/internal surfaces remain available for internal use and future products:

- `/api/dubbing`
- `/api/postproduction/status`
- `/solutions/dubbing`
- `/solutions/sound-post`

## Rollback

To roll back CID Core scoping without deleting code:

- Set backend `feature_cid_core_scope=false` through configuration or revert the default in `src/core/config.py`.
- Set frontend `CID_CORE_SCOPE_ENABLED=false` in `src_frontend/src/config/cidCoreScope.ts`.
- Rebuild frontend and rerun backend unit tests.

## Validation

- `python -m py_compile src/core/config.py src/services/module_catalog_service.py`: PASS.
- `PYTHONPATH=src python -m pytest tests/unit -q`: PASS, `652 passed, 1386 warnings`.
- `cd src_frontend && npm run build`: PASS when run inside WSL from `/opt/SERVICIOS_CINE/src_frontend`; Vite emitted existing chunk-size/dynamic-import warnings only.

## GO / NO-GO

GO for commit after review.

Rationale:

- CID Core customer-facing catalogues now exclude non-core audio/post lab surfaces.
- Internal catalogue and routes remain intact.
- Backend unit tests and frontend build pass.
- No commit was created.
