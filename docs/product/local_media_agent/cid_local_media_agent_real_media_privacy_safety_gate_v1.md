# CID Local Media Agent - Real Media Privacy Safety Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.MEDIA.PRIVACY.SAFETY.GATE.V1`

## Purpose

Define the privacy and safety guarantees required before CID Local Media Agent may proceed toward any real input-folder contract, real preflight contract, real preflight implementation, scanner integration or real media execution.

This phase is documentation/test-only.

It does not execute real media, does not call ffprobe/ffmpeg on real files, does not implement real preflight, does not implement scanner integration, does not generate a real report, and does not modify runtime code.

## Stable baseline

- Stable HEAD before this phase: `b878466`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.QA.GATE.V1`.
- Real test scope contract: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_v1.md`.
- Real test scope QA gate: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md`.
- Current synthetic wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current synthetic preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current synthetic renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Current scanner remains out of this phase: `scripts/cid_media_agent_scan.py`.

## Privacy position

CID Local Media Agent must treat real audiovisual files as private production assets.

The privacy position for the first real-material path is:

- media files remain on the local disk;
- media files are not uploaded;
- media files are not sent to cloud services;
- media files are not sent to external APIs;
- media files are not copied outside the selected output area;
- media files are not modified, renamed, moved, deleted or transcoded;
- full private paths are not exposed in user-facing reports by default;
- client material remains excluded until a later explicit client authorization gate exists.

## Local-only safety requirements

Before any real execution phase, future contracts must require:

- manually selected local input folder;
- manually selected local output folder;
- output folder separated from the input folder unless a later explicit safe exception exists;
- no automatic recursive scan of a whole drive;
- no hidden upload path;
- no external network dependency;
- no telemetry containing media names, full paths, client names or project names;
- no log line containing sensitive full local paths by default;
- no destructive filesystem operation;
- human review before marking any real test result usable.

## Report privacy requirements

Any future real report contract must default to privacy-preserving output:

- show file basenames only when needed;
- avoid full absolute paths in user-facing reports;
- avoid user home directory exposure;
- avoid client, production or project identifiers unless explicitly authorized;
- avoid embedding private source media;
- avoid thumbnails, waveform previews or frame captures unless a later explicit visual-output gate exists;
- clearly mark reports as internal test output until reviewed by a human.

## Audit and logging requirements

Any future real execution path must keep audit/logging conservative:

- logs may record phase, status, counts and generic error codes;
- logs must not contain raw private media content;
- logs must not contain full private paths by default;
- logs must not contain client names or project names by default;
- errors must fail closed when privacy cannot be guaranteed;
- no analytics or telemetry may be introduced in the first real test path.

## Required future gates before real execution

This privacy safety gate does not authorize real execution. Before any first real execution, the following phases are still required:

1. `CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1`
5. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1`
6. `CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1`

## Explicitly blocked in this phase

This privacy safety gate does not authorize:

- real media execution;
- ffprobe or ffmpeg execution on real files;
- real preflight implementation;
- scanner integration;
- real report generation;
- thumbnail, waveform or frame extraction;
- sync;
- transcription;
- translation;
- subtitle generation;
- NLE export;
- runtime implementation;
- packaging implementation;
- installable entry point;
- shell launcher;
- desktop app;
- licensing;
- client delivery;
- SaaS/backend/frontend/database/Docker/Alembic work;
- Stripe, AI Jobs, credits or ledger work.

## Safety decision

`REAL_MEDIA_PRIVACY_SAFETY_GATE_READY_FOR_INPUT_FOLDER_CONTRACT_WITH_RESTRICTIONS`

A future phase may define the real input-folder contract. No real media execution is authorized by this privacy safety gate.
