# EDITORIAL.2C - Resolve Real Fixture Smoke

**Date:** 2026-05-25
**Workspace:** `/opt/SERVICIOS_CINE`
**Status:** GO for manual Resolve 21 import smoke

## Objective

Run a real smoke of the new CID Editorial Assembly neutral core plus `ResolveExportAdapter` using the existing `production_real_20260428` fixture and generate fresh Resolve FCPXML validation artifacts.

## Fixture Used

Primary fixture:

- `docs/validation/production_real_20260428`

Media roots scanned:

- `docs/validation/production_real_20260428/media_roots/camera`
- `docs/validation/production_real_20260428/media_roots/sound`

Reports loaded:

- `docs/validation/production_real_20260428/reports/camera_report.csv`
- `docs/validation/production_real_20260428/reports/sound_report.csv`
- `docs/validation/production_real_20260428/reports/script_notes.csv`
- `docs/validation/production_real_20260428/reports/director_notes.md`
- `docs/validation/production_real_20260428/metadata_manifest.json`

Reference fixtures also present but not used as the primary smoke input:

- `docs/validation/production_real_20260428_windows`
- `docs/validation/davinci_manual_20260428`
- `docs/validation/davinci_manual_20260428_windows`

## Generated Artifacts

Output directory:

- `docs/validation/editorial_assembly_resolve_smoke_20260525/`

Generated files:

- FCPXML: `docs/validation/editorial_assembly_resolve_smoke_20260525/CID_Editorial_Resolve_Smoke_assembly.fcpxml`
- Relink report: `docs/validation/editorial_assembly_resolve_smoke_20260525/media_relink_report.json`
- Manifest: `docs/validation/editorial_assembly_resolve_smoke_20260525/manifest.json`
- Neutral timeline snapshot: `docs/validation/editorial_assembly_resolve_smoke_20260525/neutral_timeline.json`

## Results

- Camera media found: `6`
- Sound media found: `6`
- Camera report rows imported: `6`
- Sound report rows imported: `6`
- Script notes generated/loaded: `6`
- Director notes generated/loaded: `6`
- Slate matches: `6`
- Take decisions: `6`
- Sync candidates: `6`
- Sequences assembled: `2`
- Clips assembled: `6`
- Total duration: `2352` frames at 24 fps
- FCPXML size: `4528` bytes
- FCPXML validation: `valid=true`, `errors=[]`, `asset_count=12`, `clip_count=6`, `fps=24.0`
- Relink report: `resolved_media_count=12`, `missing_media_count=0`, `offline_media_count=0`

## Clips / Takes Detected

- `S1_SH1_TK1`: video + dual-system sound, tracks `V1/A1/A2`, duration `360` frames
- `S1_SH1_TK2`: video + dual-system sound, tracks `V1/A1/A2`, duration `288` frames
- `S1_SH2_TK1`: video + dual-system sound, tracks `V1/A1/A2`, duration `432` frames
- `S1_SH2_TK2`: video + dual-system sound, tracks `V1/A1/A2`, duration `360` frames
- `S2_SH1_TK1`: video + dual-system sound, tracks `V1/A1/A2`, duration `480` frames
- `S2_SH1_TK2`: video + dual-system sound, tracks `V1/A1/A2`, duration `432` frames

## Warnings

- `dual_system_audio_export_partial` appears once per clip.

Interpretation:

CID generated a conservative Resolve-compatible FCPXML with external audio resources and relink metadata. It does not create native Resolve Sync Clips or final audio grouping.

## Smoke Finding Fixed In This Phase

The real fixture exposed that matching sound reports by only `scene + take` is ambiguous when a scene has multiple shots sharing the same take number.

Fix applied:

- `SoundReportEntry` now supports optional `shot`.
- `EditorialAssemblyCoreService._find_sound_report(...)` first matches `scene + shot + take` when `shot` is available.
- Legacy `scene + take` fallback remains only for sound reports without a shot value.

This preserves compatibility while preventing cross-shot audio assignment in the production fixture.

## Limitations

- This is a backend smoke; no frontend was touched.
- Premiere remains a controlled stub.
- Avid remains a controlled stub.
- AAF remains out of scope.
- The FCPXML file is generated and validated structurally, but not imported automatically into DaVinci Resolve 21.
- The relink report points to expected destination mappings; the smoke does not copy media into the output directory.
- Dual-system audio remains conservative and manual/Resolve-assisted for final sync handling.

## Validation Commands

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
python -m py_compile \
  scripts/dev/smoke_editorial_assembly_resolve_real.py \
  src/services/editorial_assembly_core_service.py \
  src/services/editorial_export_adapter_service.py
python3 -u scripts/dev/smoke_editorial_assembly_resolve_real.py
PYTHONPATH=src python -m pytest tests/unit/test_editorial_assembly_resolve_smoke.py -q
PYTHONPATH=src python -m pytest tests/unit/test_editorial_assembly_core_service.py -q
PYTHONPATH=src python -m pytest tests/unit/test_editorial_export_adapter_service.py -q
PYTHONPATH=src python -m pytest tests/unit -q
```

Results:

- `py_compile`: PASS
- Smoke script: PASS, generated fresh FCPXML/relink/manifest/timeline artifacts
- `tests/unit/test_editorial_assembly_resolve_smoke.py -q`: PASS, `2 passed, 2 warnings`
- `tests/unit/test_editorial_assembly_core_service.py -q`: PASS, `5 passed, 2 warnings`
- `tests/unit/test_editorial_export_adapter_service.py -q`: PASS, `3 passed, 2 warnings`
- `tests/unit -q`: PASS, `668 passed, 1554 warnings`

## GO / NO-GO

GO for manual import test in DaVinci Resolve 21.

Rationale:

- The smoke uses real production fixture media/report structure.
- FCPXML exists, is non-empty and includes 12 media resources.
- Neutral timeline contains 6 clips across 2 sequences.
- Relink report resolves 12 media references and reports zero missing/offline media.
- No HTTP endpoint changes were required and no 500-class failure occurred in the adapter path.
