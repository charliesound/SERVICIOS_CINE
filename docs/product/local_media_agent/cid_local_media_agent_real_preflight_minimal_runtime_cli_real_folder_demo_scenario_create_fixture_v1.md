# CID Local Media Agent — Demo Scenario Create Fixture v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CREATE.FIXTURE.V1`

## Objective

Record that the controlled local synthetic demo fixture was created under the approved temporary root.

This phase created only synthetic placeholder files under `/tmp/cid_local_media_agent_synthetic_demo_001/`.

This phase did not execute the scanner.

This phase did not execute ffprobe.

This phase did not execute ffmpeg.

This phase did not use real client material.

This phase does not change runtime code.

## Required prior contract

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTRACT.V1`

Required prior result:

`LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CONTRACT_PASS_SYNTHETIC_LOCAL_ONLY`

## Fixture root

`/tmp/cid_local_media_agent_synthetic_demo_001/`

## Created fixture shape

- `input/camera/A001_SC001_TK001.mov`
- `input/camera/A001_SC001_TK002.mp4`
- `input/sound/A001_SC001_TK001.wav`
- `input/proxies/A001_SC001_TK001_PROXY.mp4`
- `input/non_media/notes.txt`
- `input/non_media/installer.exe`
- `input/UNKNOWN/UNKNOWN_ASSET.txt`
- `output/`

## Fixture content

Every file contains exactly:

`synthetic placeholder only`

## Creation validation evidence

- approved synthetic demo root: `PASS`
- file count: `7`
- placeholder content check: `PASS`
- forbidden path check: `PASS`
- scanner execution: `NOT_EXECUTED`
- ffprobe execution: `NOT_EXECUTED`
- ffmpeg execution: `NOT_EXECUTED`
- real client material: `NOT_USED`
- git status after fixture creation: `CLEAN`

## Explicit no-goals

This phase does not authorize scanner execution, public demo, client-facing demo, real client-material demo, media probing, media decoding, transcription, translation, subtitles, sync, NLE export, SaaS calls, database writes, network calls, or report-expansion scope.

## Protected scope still blocked

This phase does not authorize SaaS backend/frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, ledger, frontend, backend, or media-processing implementation.

## Recommended next phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.FIXTURE.QA.GATE.V1`

## Fixture creation result

`LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CREATE_FIXTURE_PASS_SYNTHETIC_PLACEHOLDERS_ONLY`
