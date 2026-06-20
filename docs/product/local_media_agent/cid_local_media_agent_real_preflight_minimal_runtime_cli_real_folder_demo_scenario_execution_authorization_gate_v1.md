# CID Local Media Agent — Demo Scenario Execution Authorization Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.EXECUTION.AUTHORIZATION.GATE.V1`

## Objective

Authorize a future controlled scanner execution against the approved local synthetic demo fixture only.

This phase is docs/test-only.

This phase does not execute the scanner.

This phase does not execute ffprobe.

This phase does not execute ffmpeg.

This phase does not use real client material.

This phase does not change runtime code.

## Required prior phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.FIXTURE.QA.GATE.V1`

Required prior result:

`LOCAL_MEDIA_AGENT_DEMO_SCENARIO_FIXTURE_QA_GATE_PASS_READY_FOR_EXECUTION_AUTHORIZATION_GATE`

## Authorization evidence

- repo status before authorization gate: `CLEAN`
- HEAD approved lineage: `73070f5b74c932ce9f64b04c35818490bca20518`
- origin/main alignment: `PASS`
- fixture QA gate tag alignment: `PASS`
- fixture root exists: `PASS`
- expected fixture tree exists: `PASS`
- scanner execution before this gate: `NOT_EXECUTED`
- ffprobe execution before this gate: `NOT_EXECUTED`
- ffmpeg execution before this gate: `NOT_EXECUTED`
- real client material: `NOT_USED`

## Authorized fixture root

`/tmp/cid_local_media_agent_synthetic_demo_001/`

Authorized input root:

`/tmp/cid_local_media_agent_synthetic_demo_001/input`

Authorized output root:

`/tmp/cid_local_media_agent_synthetic_demo_001/output`

## Authorized future command

`python scripts/cid_media_agent_scan.py --input-root /tmp/cid_local_media_agent_synthetic_demo_001/input --output-root /tmp/cid_local_media_agent_synthetic_demo_001/output --json`

No `--ffprobe-preflight` flag is authorized.

No ffmpeg command is authorized.

No network call is authorized.

No SaaS call is authorized.

No database write is authorized.

## Authorized expected result for next phase

- `exit_code=1`
- `status=completed_with_warnings`
- `candidate_media_count=5`
- `warnings_count=1`
- `human_review_required_count=1`
- `accepted_extension_counts={".mov":1,".mp4":2,".wav":1}`
- `rejected_extension_counts={".exe":1,".txt":2}`
- `ignored_extension_counts={}`
- `ffprobe_preflight.requested=false`
- `ffprobe_preflight.status=skipped`

## Required future output files

- `00_project/processing_status.json`
- `01_media_catalog/media_catalog.json`
- `02_audio_sync/README.txt`
- `03_transcription/README.txt`
- `04_subtitles/README.txt`
- `05_reports/README.txt`
- `06_exports/README.txt`

## Future execution abort conditions

The next controlled execution must abort if repo is not clean, HEAD is not approved lineage, fixture root is missing, fixture root is outside `/tmp/cid_local_media_agent_synthetic_demo_001/`, input root is missing, output root is missing, real media is detected, real client material is detected, Windows paths are detected, `/mnt/` paths are detected, scanner exits with code `2`, required JSON fields are missing, semantic counts differ, scanner writes outside output root, or privacy checks fail.

## Explicit no-goals

This phase does not authorize public demo, client-facing demo, sales demo, real client-material demo, media probing, media decoding, ffprobe execution, ffmpeg execution, transcription, translation, subtitles, sync, NLE export, SaaS calls, database writes, network calls, or report-expansion scope.

## Protected scope still blocked

This phase does not authorize SaaS backend/frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, ledger, frontend, backend, or media-processing implementation.

## Recommended next phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTROLLED.EXECUTION.V1`

## Authorization gate result

`LOCAL_MEDIA_AGENT_DEMO_SCENARIO_EXECUTION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION`
