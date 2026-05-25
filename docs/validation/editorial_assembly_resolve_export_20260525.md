# EDITORIAL.2B - Resolve FCPXML Export Adapter

**Date:** 2026-05-25
**Workspace:** `/opt/SERVICIOS_CINE`
**Status:** GO

## Objective

Connect the CID Editorial Assembly neutral core to the existing DaVinci/Resolve FCPXML export services without changing frontend code, without replacing the legacy editorial endpoints, and without implementing real Premiere, Avid or AAF export.

## Scope Implemented

- `ResolveExportAdapter` now converts `AssemblyTimeline` into the existing `assembly_cut` dictionary shape expected by `fcpxml_export_service`.
- Resolve export now generates FCPXML through `fcpxml_export_service.build_fcpxml(...)` instead of the temporary internal XML scaffold.
- Resolve export validates generated FCPXML with `fcpxml_validation_service.validate(...)` before returning the response.
- `NLEExportRequest` accepts `media_assets` so the Resolve adapter can resolve media URIs and generate relink metadata from the neutral request payload.
- `NLEExportResult` includes optional `artifact_path` and `artifact_url` fields for suggested destination metadata when `destination_root_path` is provided.
- Neutral assembly construction now keeps deterministic scene/shot/take order and derives basic dual-system audio fields:
  - `audio_media_asset_id`
  - `timecode_offset_frames`
  - `assigned_tracks`
- Route tests cover real Resolve FCPXML response validation and relink report metadata.

## Files Modified

- `src/schemas/editorial_assembly_schema.py`
- `src/services/editorial_assembly_core_service.py`
- `src/services/editorial_export_adapter_service.py`
- `tests/unit/test_editorial_assembly_core_service.py`
- `tests/unit/test_editorial_export_adapter_service.py`
- `tests/unit/test_editorial_assembly_routes.py`

## Existing Services Reused

- `src/services/fcpxml_export_service.py`
- `src/services/fcpxml_validation_service.py`
- `src/services/davinci_platform_package_service.py`
- `src/services/editorial_assembly_core_service.py`

No existing `src/routes/editorial_routes.py` or legacy DaVinci flow was modified.

## Fixtures Inspected

Requested non-Windows fixture directories were not present. Available Windows fixture ZIPs were inspected without extraction or mutation:

- `docs/validation/production_real_20260428_windows/CID_Production_Synthetic_Validation_20260428_WINDOWS.zip`
  - Contains `fcpxml/assembly_windows.fcpxml`, camera/sound reports, `media_relink_report_windows.json`, and synthetic media files.
- `docs/validation/davinci_manual_20260428_windows/CID_DaVinci_Validation_20260428_WINDOWS.zip`
  - Contains `assembly_windows.fcpxml`, `media_relink_report_windows.json`, summary JSON, recommended takes JSON, notes, and small media placeholders.

These fixtures remain useful as manual Resolve reference artifacts, but EDITORIAL.2B validation used deterministic unit fixtures to avoid extracting or committing runtime media.

## What Remains Stubbed Or Out Of Scope

- Premiere remains a controlled stub with warning `premiere_export_stub_controlled`.
- Avid remains a controlled ALE stub with warning `avid_export_stub_controlled`.
- AAF remains explicitly unimplemented.
- No frontend changes were made.
- No creative final edit or NLE timeline editing feature was added.
- `artifact_path` is returned as suggested destination metadata; the endpoint still returns the FCPXML payload as base64 and does not write files to disk.

## Risks And Notes

- Dual-system audio remains conservative. The FCPXML contains external audio metadata/resource notes, not native Resolve Sync Clips.
- Media URI resolution is request-driven. Accurate `destination_root_path` and `target_platform` remain required to avoid offline media in real editorial workstations.
- Route-level report lookup is still non-persisted from EDITORIAL.2A.
- Full Resolve import validation still requires manual import in DaVinci Resolve 21.

## Validation

Commands:

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
python -m py_compile src/services/editorial_assembly_core_service.py src/services/editorial_export_adapter_service.py src/routes/editorial_assembly_routes.py
PYTHONPATH=src python -m pytest tests/unit/test_editorial_assembly_core_service.py -q
PYTHONPATH=src python -m pytest tests/unit/test_editorial_export_adapter_service.py -q
PYTHONPATH=src python -m pytest tests/unit/test_editorial_assembly_routes.py -q
PYTHONPATH=src python -m pytest tests/unit -q
```

Results:

- `py_compile`: PASS.
- `tests/unit/test_editorial_assembly_core_service.py -q`: PASS, `4 passed, 2 warnings`.
- `tests/unit/test_editorial_export_adapter_service.py -q`: PASS, `3 passed, 2 warnings`.
- `tests/unit/test_editorial_assembly_routes.py -q`: PASS, `4 passed, 237 warnings`.
- `tests/unit -q`: PASS, `665 passed, 1554 warnings`.

## GO / NO-GO

GO for review.

Rationale:

- Resolve export now uses the existing FCPXML export and validation services.
- The neutral adapter boundary remains intact.
- Existing legacy editorial/DaVinci routes were preserved.
- Premiere/Avid/AAF scope boundaries were not expanded.
- Targeted and full unit validation passed.
