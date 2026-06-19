# CID Local Media Agent — Real Preflight Minimal Runtime CLI Real Folder Authorization Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.CONTRACT.V1`

## Objective

This phase defines the authorization contract required before any future controlled real-folder dry-run may be considered.

This phase is docs/test-only.

It does not execute the CLI against a real folder. It does not authorize a real-folder smoke invocation. It does not authorize real client media. It does not authorize mounted Windows paths. It does not authorize cloud-synced folders. It does not authorize network shares. It does not authorize scanner integration. It does not authorize ffprobe or ffmpeg. It does not authorize media probing, media decoding, report generation, sync analysis, transcription, translation, subtitles, NLE export, upload, packaging, desktop app, installer, licensing, SaaS, backend, frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, or ledger work.

The only purpose is to define what must be true before a later separately authorized dry-run readiness gate can be created.

## Current clean stable prerequisite

The current clean prerequisite anchor is:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-smoke-demo-readiness-gate-v1-postgresql-only-recovery-20260619`

Expected prerequisite commit:

`2cf3d936b6f7f64cfd71bc9dc8e516f37adcd928`

The earlier tag below is superseded and must not be used as the clean stable anchor:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-smoke-demo-readiness-gate-v1-20260619`

## Authorization decision states

This contract allows only these conceptual decision states:

- `AUTHORIZATION_PASS`
- `AUTHORIZATION_FAIL`
- `AUTHORIZATION_BLOCKED`

`AUTHORIZATION_PASS` means the authorization documentation is complete enough to proceed to a later dry-run readiness gate.

`AUTHORIZATION_FAIL` means one or more authorization fields are missing, ambiguous, or inconsistent.

`AUTHORIZATION_BLOCKED` means the proposed folder, workflow, dependency, path, integration, or data exposure would cross a blocked boundary.

## Required human authorization fields

Before any later real-folder dry-run readiness gate, the operator must provide a human-readable authorization record containing:

- `authorized_by_human`;
- `authorization_timestamp`;
- `authorized_phase`;
- `approved_folder_purpose`;
- `approved_folder_location_class`;
- `approved_folder_contains_real_client_media`;
- `approved_folder_contains_sensitive_media`;
- `approved_folder_contains_personal_data`;
- `approved_expected_file_count_range`;
- `approved_expected_total_size_range`;
- `approved_allowed_extensions`;
- `approved_output_behavior`;
- `approved_no_media_decoding`;
- `approved_no_report_generation`;
- `approved_no_network_access`;
- `approved_no_scanner_integration`;
- `approved_no_ffprobe_or_ffmpeg`;
- `approved_rollback_plan`;
- `approved_stop_conditions`.

This contract does not require storing the raw approved folder path in Git.

## Eligible folder class for later dry-run consideration

A future folder may be considered only if all of the following are true:

- it is a local Linux folder visible inside WSL;
- it is intentionally selected by the human operator;
- it is not the entire disk;
- it is not the repository root;
- it is not a home directory root;
- it is not a cloud-synced directory;
- it is not a network share;
- it is not a mounted Windows path;
- it is not under `/mnt/`;
- it is not a Windows drive path such as `C:\`;
- it is not a production delivery folder;
- it is not a backup folder;
- it is not a database folder;
- it contains a small, bounded number of files;
- it can be snapshotted before the dry-run;
- it can be abandoned if stop conditions trigger.

## Real media policy

This authorization contract still does not authorize real media execution.

If a later phase proposes real media, that later phase must explicitly decide whether the approved folder contains:

- no real client media;
- controlled non-sensitive real media;
- sensitive real client media.

Sensitive real client media remains blocked until a separate privacy review explicitly authorizes it.

## Output behavior policy

The future dry-run candidate must remain:

- no report generation;
- no selected output folder writes unless separately authorized;
- sanitized stdout only;
- sanitized stderr only;
- no raw private path leakage;
- no raw filename leakage;
- no client name leakage;
- no project name leakage;
- no stack trace leakage;
- deterministic exit codes only.

## Still blocked by this contract

This contract explicitly keeps blocked:

- real-folder smoke invocation;
- broad real project scan;
- whole-disk scan;
- mounted Windows paths;
- `/mnt/` paths;
- /mnt/ paths;
- Windows drive paths;
- cloud-synced folders;
- network shares;
- scanner integration;
- ffprobe;
- ffmpeg;
- media probing;
- media decoding;
- report generation;
- visible report integration;
- waveform analysis;
- audio sync;
- clap detection;
- timecode extraction;
- transcription;
- translation;
- subtitle generation;
- DaVinci Resolve integration;
- Avid integration;
- EDL generation;
- XML generation;
- AAF generation;
- OTIO generation;
- timeline generation;
- upload;
- cloud transfer;
- desktop app;
- installer;
- packaging;
- licensing activation;
- SaaS integration;
- backend changes;
- frontend changes;
- database changes;
- Docker changes;
- Alembic changes;
- Stripe changes;
- AI Jobs changes;
- credits changes;
- ledger changes.

## Required pre-execution gates after this contract

A future controlled real-folder dry-run may not happen until at least these later gates pass:

1. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.EXECUTION.V1`

This contract alone does not authorize item 3.

## Repository safety requirements

Before closing this phase:

- the contract document must exist;
- the contract test must exist;
- the clean prerequisite recovery tag must exist;
- the clean prerequisite recovery tag must point to the expected commit;
- the superseded readiness tag must be documented as not the clean stable anchor;
- protected files must not be staged;
- `.env` must not be staged;
- database files must not be staged;
- backup files must not be staged;
- SaaS, backend, frontend, Docker, Alembic, Stripe, AI Jobs, credits, and ledger files must not be staged;
- WSL/repository guard must pass;
- PostgreSQL-only regression guard must pass.

## Acceptance criteria

This phase is accepted only if:

- this authorization contract document exists;
- this authorization contract test exists;
- this phase is documented as docs/test-only;
- this phase clearly states that it does not execute the CLI against real folders;
- the clean prerequisite recovery tag is documented;
- the superseded readiness tag is documented as not the clean stable anchor;
- all required human authorization fields are documented;
- eligible folder class requirements are documented;
- blocked folder classes are documented;
- real media remains not authorized by this contract;
- output behavior remains sanitized and no-write by default;
- blocked operations remain blocked;
- later required gates are documented;
- previous readiness gate tests still pass;
- previous smoke/demo QA gate tests still pass;
- previous smoke/demo implementation tests still pass;
- previous smoke/demo contract tests still pass;
- previous CLI tests still pass;
- previous runtime tests still pass;
- repository guards still pass.
