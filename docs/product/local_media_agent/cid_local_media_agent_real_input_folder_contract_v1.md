# CID Local Media Agent - Real Input Folder Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1`

## Purpose

Define the local-only input-folder contract required before CID Local Media Agent may proceed toward any real preflight contract, real preflight implementation, scanner integration or real media execution.

This phase is documentation/test-only.

It does not execute real media, does not call ffprobe/ffmpeg on real files, does not implement real preflight, does not implement scanner integration, does not generate a real report, and does not modify runtime code.

## Stable baseline

- Stable HEAD before this phase: `101f267`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.REAL.MEDIA.PRIVACY.SAFETY.GATE.V1`.
- Privacy safety gate: `docs/product/local_media_agent/cid_local_media_agent_real_media_privacy_safety_gate_v1.md`.
- Real test scope contract: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_v1.md`.
- Real test scope QA gate: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md`.
- Current synthetic wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current synthetic preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current synthetic renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Current scanner remains out of this phase: `scripts/cid_media_agent_scan.py`.

## Input folder position

The first real input folder must be a manually selected local directory created specifically for internal laboratory testing.

The input folder must contain only copied test media owned or explicitly authorized by the developer.

The input folder must not contain client material, confidential productions, original camera masters or whole-drive material.

## Required local-only folder rules

A future real preflight must require that the input folder:

- is manually selected by the user;
- exists before execution;
- is a directory, not a file;
- is local to the machine running the tool;
- is not a drive root;
- is not the user home directory root;
- is not a system directory;
- is not a hidden application/cache/temp directory;
- is not a cloud-sync root by default;
- is not a network share by default;
- is readable by the current user;
- is treated as read-only input by CID Local Media Agent.

## First real test size limits

The first real input-folder test must stay intentionally small:

- maximum file count: 25 media files;
- maximum total selected media size: 10 GB;
- maximum scan depth: 3 directory levels;
- no automatic scan of a whole disk, user profile, media library or project archive;
- no batch processing of multiple unrelated projects.

These limits are conservative and may be revised only by a later explicit capacity gate.

## First real test extension allowlist

The first real input-folder contract may allow only the following media extensions:

- video: `.mov`, `.mp4`, `.mxf`;
- audio: `.wav`, `.aif`, `.aiff`.

All other extensions must be ignored or rejected by future preflight behavior until a later explicit format-support gate exists.

## Output folder separation

A future real preflight must require a manually selected local output folder.

The output folder must:

- exist before execution or be created only by a later explicit implementation phase;
- be local to the machine running the tool;
- be separated from the input folder by default;
- not overwrite source media;
- not copy source media by default;
- contain only future generated metadata/report artifacts, never modified source media.

## Path privacy requirements

Any future real preflight or report must preserve path privacy:

- no full private paths in user-facing reports by default;
- no user home directory exposure by default;
- no client names or project names in logs by default;
- no telemetry containing file names, full paths, client names or project names;
- errors must fail closed when path privacy cannot be guaranteed.

## Required future gates before real execution

This input folder contract does not authorize real execution. Before any first real execution, the following phases are still required:

1. `CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.QA.GATE.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1`
5. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1`
6. `CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1`

## Explicitly blocked in this phase

This input folder contract does not authorize:

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

## Contract decision

`REAL_INPUT_FOLDER_CONTRACT_READY_FOR_QA_GATE_WITH_RESTRICTIONS`

A future phase may audit this input folder contract. No real media execution is authorized by this document.
