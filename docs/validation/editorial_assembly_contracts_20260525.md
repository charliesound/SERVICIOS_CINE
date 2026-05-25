# EDITORIAL.2A - Editorial Assembly Contracts

**Date:** 2026-05-25
**Workspace:** `/opt/SERVICIOS_CINE`
**Status:** GO

## Objective

Implement the base contractual layer for CID Editorial Assembly multi-NLE without breaking the existing editorial/DaVinci flow.

This phase adds neutral schemas, a neutral core service, export adapter contracts and additive API routes for:

- DaVinci Resolve 21
- Adobe Premiere Pro
- Avid Media Composer

## Files Created

- `src/schemas/editorial_assembly_schema.py`
- `src/services/editorial_assembly_core_service.py`
- `src/services/editorial_export_adapter_service.py`
- `src/routes/editorial_assembly_routes.py`
- `tests/unit/test_editorial_assembly_schema.py`
- `tests/unit/test_editorial_assembly_core_service.py`
- `tests/unit/test_editorial_export_adapter_service.py`
- `tests/unit/test_editorial_assembly_routes.py`

## Files Modified

- `src/core/app_factory.py` registers the additive `editorial_assembly_router`.

## Endpoints Added

- `POST /api/projects/{project_id}/editorial/scan-media`
- `POST /api/projects/{project_id}/editorial/import-reports`
- `POST /api/projects/{project_id}/editorial/match-takes`
- `POST /api/projects/{project_id}/editorial/build-assembly`
- `POST /api/projects/{project_id}/editorial/export/resolve`
- `POST /api/projects/{project_id}/editorial/export/premiere`
- `POST /api/projects/{project_id}/editorial/export/avid`
- `GET /api/projects/{project_id}/editorial/reports/{report_id}`

## Services Reused Or Preserved

Existing services were not deleted or replaced:

- `src/services/assembly_service.py`
- `src/services/editorial_reconciliation_service.py`
- `src/services/fcpxml_export_service.py`
- `src/services/fcpxml_validation_service.py`
- `src/services/davinci_platform_package_service.py`
- `src/routes/editorial_routes.py`

The new Resolve adapter records compatibility with:

- `fcpxml_export_service`
- `davinci_platform_package_service`

No existing DaVinci export endpoint was modified.

## What Is Real In This Phase

- Pydantic contracts for media assets, reports, notes, matching, sync candidates, take decisions, neutral assembly timelines, NLE export requests/results, relink and missing media reports.
- Safe filesystem media scanning for known media extensions.
- JSON report ingestion contract and import count response.
- Deterministic report-based slate matching and basic take scoring.
- Neutral assembly timeline construction from recommended take decisions.
- Relink report generation from neutral timeline and media assets.
- Resolve adapter returns an FCPXML contract payload and manifest.
- Routes are registered and return controlled responses without 500s.

## What Is Stub In This Phase

- Premiere adapter is a controlled stub returning XML-shaped payload, manifest `stub_controlled`, and warning `premiere_export_stub_controlled`.
- Avid adapter is a controlled ALE stub returning manifest `stub_controlled`, warning `avid_export_stub_controlled`, and explicit warning `aaf_not_implemented_in_editorial_2a`.
- `GET /reports/{report_id}` returns a contract-only non-persisted report placeholder.
- No AAF implementation exists.
- No creative final edit is attempted.
- No frontend integration exists in this phase.

## Risks

- Current matching is deterministic contract logic, not the final reconciliation algorithm from production editorial data.
- Filesystem scanning is intentionally simple and metadata-light; BWF/iXML and camera metadata parsing remain for later integration.
- Resolve adapter output is contract-compatible FCPXML scaffolding; full production-grade export remains in existing DaVinci services until encapsulation in a later phase.
- Premiere and Avid imports need real NLE validation in future phases.
- Avid AAF remains explicitly out of scope.

## Next Phase

- Encapsulate existing DaVinci FCPXML/package behavior behind the Resolve adapter without changing current endpoints.
- Add concrete Premiere FCPXML normalization for audio channel routing.
- Add ALE generator and EDL CMX 3600 generator for Avid.
- Persist assembly reports and expose real report lookup/download.
- Integrate BWF/iXML and camera metadata parsers into neutral `scan_media_roots`.

## Validation

Commands:

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
python -m py_compile \
  src/schemas/editorial_assembly_schema.py \
  src/services/editorial_assembly_core_service.py \
  src/services/editorial_export_adapter_service.py \
  src/routes/editorial_assembly_routes.py
PYTHONPATH=src python -m pytest tests/unit/test_editorial_assembly_schema.py -q
PYTHONPATH=src python -m pytest tests/unit/test_editorial_assembly_core_service.py -q
PYTHONPATH=src python -m pytest tests/unit/test_editorial_export_adapter_service.py -q
PYTHONPATH=src python -m pytest tests/unit/test_editorial_assembly_routes.py -q
```

Result:

- `py_compile`: PASS.
- Targeted EDITORIAL.2A tests: PASS, `11 passed`.

Full unit suite:

```bash
PYTHONPATH=src python -m pytest tests/unit -q
```

Result: PASS, `663 passed, 1518 warnings`.

## GO / NO-GO

GO for commit after review.

Rationale:

- All new contracts and additive endpoints validate.
- Existing editorial routes/services are preserved.
- Resolve is primary and real enough for contract FCPXML scaffolding.
- Premiere/Avid are controlled stubs, not accidental 500s.
- No AAF, frontend, creative edit, or destructive changes were introduced.
