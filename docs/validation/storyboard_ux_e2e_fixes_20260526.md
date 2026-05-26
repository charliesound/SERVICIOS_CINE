# STORYBOARD.UX.2 - E2E fixes validation

Date: 2026-05-26

## Scope

- Integrated `StoryboardSequenceSelectorModal` in `StoryboardBuilderPage.tsx`.
- Added explicit sequence selection, sequence planning, and guarded sequence generation actions.
- Added visible sequence counters and selected-sequence confirmation copy.
- Preserved authenticated blob-based Storyboard Sheet downloads and verified no internal `artifact_path` is rendered in the export UI.
- Improved storyboard shot image attempts by treating asset IDs and metadata image paths as valid authenticated image candidates.
- Improved sequence terminology and metadata traceability display for generated shots.

## Files changed

- `src_frontend/src/pages/StoryboardBuilderPage.tsx`
- `src_frontend/src/components/storyboard/ShotCard.tsx`

## Validation

Commands run from `/opt/SERVICIOS_CINE` unless noted.

```bash
bash scripts/smoke_storyboard_sequence_selection_ux.sh
```

Result: PASS. All 13 checks passed.

```bash
bash scripts/smoke_storyboard_visual_cycle.sh
```

Result: PASS. Backend/frontend visual-cycle checks and Python compilation passed.

```bash
bash scripts/smoke_scene_breakdown_ux.sh
```

Result: PASS. All 7 checks passed.

```bash
source .venv/bin/activate && python -m py_compile \
  src/routes/storyboard_routes.py \
  src/routes/shot_routes.py \
  src/services/storyboard_service.py \
  src/services/storyboard_shot_planner_service.py \
  src/services/storyboard_asset_repair_service.py
```

Result: PASS.

```bash
source .venv/bin/activate && PYTHONPATH=src python -m pytest tests/unit/test_storyboard_*.py -q
```

Result: PASS. `175 passed, 141 warnings in 14.34s`.

```bash
cd /opt/SERVICIOS_CINE/src_frontend && npm run build
```

Result: PASS. Vite build completed successfully. Existing chunk-size/dynamic-import warnings were reported.

Note: `npm --prefix src_frontend run build` from the Windows UNC working directory failed before TypeScript compilation because `cmd.exe` cannot use a UNC path as current directory. The build was rerun from the native WSL path and passed.

```bash
git diff --check
```

Result: PASS. Only existing line-ending warnings were printed by Git.

## Outcome

STORYBOARD.UX.2 critical UX checks are green. The implementation remains frontend-first and does not modify Editorial Assembly, ComfyUI, backend contracts, routes, workflows, models, or custom nodes.
