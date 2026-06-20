# CID Local Media Agent — Demo Scenario Fixture QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.FIXTURE.QA.GATE.V1`

## Objective

Validate that the controlled local synthetic demo fixture exists in the approved temporary root and remains safe for a future controlled scanner execution gate.

This phase is docs/test-only.

This phase does not execute the scanner.

This phase does not execute ffprobe.

This phase does not execute ffmpeg.

This phase does not use real client material.

This phase does not change runtime code.

## Required prior phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CREATE.FIXTURE.V1`

Required prior result:

`LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CREATE_FIXTURE_PASS_SYNTHETIC_PLACEHOLDERS_ONLY`

## Fixture root validated

`/tmp/cid_local_media_agent_synthetic_demo_001/`

## QA evidence

- repo status before QA gate: `CLEAN`
- HEAD approved lineage: `72d2031de2c1d34a1d95e9d5fba2e3eb1263f5b2`
- origin/main alignment: `PASS`
- create fixture tag alignment: `PASS`
- fixture root exists: `PASS`
- expected directory tree exists: `PASS`
- expected file count: `7`
- placeholder-only content policy: `PASS`
- forbidden path policy: `PASS`
- scanner execution: `NOT_EXECUTED`
- ffprobe execution: `NOT_EXECUTED`
- ffmpeg execution: `NOT_EXECUTED`
- real client material: `NOT_USED`

## Required fixture files

- `input/camera/A001_SC001_TK001.mov`
- `input/camera/A001_SC001_TK002.mp4`
- `input/sound/A001_SC001_TK001.wav`
- `input/proxies/A001_SC001_TK001_PROXY.mp4`
- `input/non_media/notes.txt`
- `input/non_media/installer.exe`
- `input/UNKNOWN/UNKNOWN_ASSET.txt`
- `output/`

## Fixture content policy

Every file must contain exactly:

`synthetic placeholder only`

## Execution authorization boundary

This QA gate does not authorize scanner execution by itself.

A later execution authorization gate is still required before running `python scripts/cid_media_agent_scan.py` against the fixture.

## Explicit no-goals

This phase does not authorize public demo, client-facing demo, sales demo, real client-material demo, media probing, media decoding, ffprobe execution, ffmpeg execution, transcription, translation, subtitles, sync, NLE export, SaaS calls, database writes, network calls, or report-expansion scope.

## Protected scope still blocked

This phase does not authorize SaaS backend/frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, ledger, frontend, backend, or media-processing implementation.

## Recommended next phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.EXECUTION.AUTHORIZATION.GATE.V1`

## QA gate result

`LOCAL_MEDIA_AGENT_DEMO_SCENARIO_FIXTURE_QA_GATE_PASS_READY_FOR_EXECUTION_AUTHORIZATION_GATE`
