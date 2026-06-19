# CID Local Media Agent - Real Test Scope Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.V1`

## Purpose

Define the exact scope of the first internal real-material test for CID Local Media Agent before any real media execution, real preflight implementation, scanner integration, transcription, synchronization, subtitle generation, NLE export, packaging or client-facing workflow.

This phase is documentation/test-only.

It does not execute real media, does not call ffprobe/ffmpeg on real files, does not implement a real scanner workflow, does not generate a real report, and does not modify runtime code.

## Stable baseline

- Stable HEAD before this phase: `ac9e168`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.PACKAGING.READINESS.QA.GATE.V1`.
- Current synthetic wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current synthetic preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current synthetic renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Current scanner remains out of this phase: `scripts/cid_media_agent_scan.py`.

## First real test intent

The first real test must be an internal laboratory test only.

It is intended to answer only this question:

> Can CID Local Media Agent safely inspect a small local folder of real audiovisual files in a controlled internal environment without uploading, modifying, deleting, moving, transcoding or exposing the material?

## Allowed future real test material

The future real test may use only:

- material owned or explicitly authorized by the developer;
- a small local-only folder created specifically for the test;
- copied test media, never original camera masters;
- non-client material unless a later explicit client authorization gate exists;
- a manually selected input folder;
- a manually selected output folder;
- read-only inspection as the default safety posture.

## Explicit first test exclusions

The first real test must not include:

- client material;
- confidential productions;
- original camera masters;
- destructive operations;
- moving files;
- deleting files;
- renaming files;
- transcoding;
- upload;
- cloud processing;
- external API calls;
- sync;
- transcription;
- translation;
- subtitle generation;
- DaVinci Resolve export;
- Avid export;
- packaging;
- installable entry point;
- shell launcher;
- desktop app;
- licensing;
- SaaS/backend/frontend/database/Docker/Alembic work;
- Stripe, AI Jobs, credits or ledger work.

## Minimum future test success criteria

A later real execution phase may be considered only if future gates confirm:

- input folder is local;
- output folder is local;
- no upload path exists;
- no external network dependency is required;
- original media files are not modified;
- no files are moved, deleted or renamed;
- sensitive full paths are not exposed in user-facing reports by default;
- human review is mandatory before considering the result usable.

## Required next gates before real execution

Before any first real execution, the following phases are still required:

1. `CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.QA.GATE.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.MEDIA.PRIVACY.SAFETY.GATE.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1`
5. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1`
6. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1`
7. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1`
8. `CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1`

## Explicitly blocked in this phase

This contract does not authorize:

- real media execution;
- ffprobe or ffmpeg execution on real files;
- scanner integration;
- real report generation;
- runtime implementation;
- packaging implementation;
- installable entry point;
- shell launcher;
- client delivery;
- SaaS/backend/frontend/database/Docker/Alembic work;
- Stripe, AI Jobs, credits or ledger work.

## Decision

`REAL_TEST_SCOPE_CONTRACT_READY_FOR_QA_GATE_WITH_RESTRICTIONS`

A future phase may audit this scope contract. No real media execution is authorized by this document.
