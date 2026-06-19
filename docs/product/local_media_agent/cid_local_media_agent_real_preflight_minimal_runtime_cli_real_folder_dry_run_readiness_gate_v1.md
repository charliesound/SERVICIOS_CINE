# CID Local Media Agent — Real Preflight Minimal Runtime CLI Real Folder Dry Run Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1`

## Objective

This phase defines the final conservative readiness gate before any future controlled real-folder dry-run execution may be considered.

This phase is docs/test-only.

It does not execute the CLI against a real folder. It does not authorize a real-folder dry-run execution. It does not authorize real client media. It does not authorize mounted Windows paths. It does not authorize cloud-synced folders. It does not authorize network shares. It does not authorize scanner integration. It does not authorize ffprobe or ffmpeg. It does not authorize media probing, media decoding, report generation, sync analysis, transcription, translation, subtitles, NLE export, upload, packaging, desktop app, installer, licensing, SaaS, backend, frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, or ledger work.

The only purpose is to prove that the repository and authorization chain are ready to discuss a later separately authorized execution phase.

## Current clean stable prerequisite

The latest clean stable prerequisite is:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-authorization-qa-gate-v1-20260619`

Expected prerequisite commit:

`9cbcc9d8f05f79b27311518457dea23a1201fcb6`

## Required prerequisite chain

This readiness gate requires the following chain:

1. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.READINESS.GATE.V1` recovered by PostgreSQL-only wording recovery.
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.CONTRACT.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1`

The future execution phase is not part of this phase.

## Readiness decision states

This readiness gate allows only:

- `READINESS_PASS`
- `READINESS_FAIL`
- `READINESS_BLOCKED`

`READINESS_PASS` means all non-executing prerequisites are ready to prepare a later execution gate.

`READINESS_FAIL` means prerequisite files, tags, fields, or tests are missing or inconsistent.

`READINESS_BLOCKED` means the proposed next step would cross a real-media, path, privacy, dependency, integration, or protected-file boundary.

## Required dry-run candidate record

Before any later execution phase, a human-readable dry-run candidate record must exist outside this contract and must contain:

- `authorized_by_human`;
- `authorization_timestamp`;
- `authorized_phase`;
- `dry_run_candidate_folder_class`;
- `dry_run_candidate_folder_is_local_linux_only`;
- `dry_run_candidate_folder_is_not_repo_root`;
- `dry_run_candidate_folder_is_not_home_root`;
- `dry_run_candidate_folder_is_not_mounted_windows_path`;
- `dry_run_candidate_folder_is_not_under_mnt`;
- `dry_run_candidate_folder_is_not_cloud_synced`;
- `dry_run_candidate_folder_is_not_network_share`;
- `dry_run_candidate_expected_file_count_range`;
- `dry_run_candidate_expected_total_size_range`;
- `dry_run_candidate_allowed_extensions`;
- `dry_run_candidate_contains_real_client_media`;
- `dry_run_candidate_contains_sensitive_media`;
- `dry_run_candidate_contains_personal_data`;
- `dry_run_candidate_input_snapshot_plan`;
- `dry_run_candidate_output_behavior`;
- `dry_run_candidate_no_media_decoding`;
- `dry_run_candidate_no_report_generation`;
- `dry_run_candidate_no_scanner_integration`;
- `dry_run_candidate_no_ffprobe_or_ffmpeg`;
- `dry_run_candidate_no_network_access`;
- `dry_run_candidate_stop_conditions`;
- `dry_run_candidate_rollback_plan`.

This readiness gate does not store a raw folder path in Git.

## Eligible candidate class

A future candidate may be considered only if all of the following are true:

- it is a local Linux folder visible inside WSL;
- it is intentionally selected by the human operator;
- it is not the repository root;
- it is not a home directory root;
- it is not the entire disk;
- it is not a mounted Windows path;
- it is not under `/mnt/`;
- it is not a /mnt/ path;
- it is not a Windows drive path such as `C:\`;
- it is not a cloud-synced directory;
- it is not a network share;
- it is not a production delivery folder;
- it is not a backup folder;
- it is not a database folder;
- it contains a small, bounded number of files;
- it can be snapshotted before execution;
- it can be abandoned without business impact.

## Dry-run behavior allowed for later execution phase only

A later execution phase may propose only:

- minimal CLI preflight invocation;
- local filesystem metadata checks only;
- sanitized stdout;
- sanitized stderr;
- deterministic exit code mapping;
- no selected output folder writes unless separately authorized;
- no selected input folder changes;
- no raw private path leakage;
- no raw filename leakage;
- no client name leakage;
- no project name leakage;
- no stack trace leakage.

This readiness gate itself does not run that invocation.

## Explicit non-authorization

This readiness gate explicitly does not authorize:

- real-folder dry-run execution;
- real-folder smoke invocation;
- broad real project scan;
- whole-disk scan;
- real client media execution;
- sensitive media execution;
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

## Required test matrix before closing this phase

The following matrix must remain green:

- real folder dry-run readiness gate;
- real folder authorization QA gate;
- real folder authorization contract;
- smoke/demo readiness gate;
- smoke/demo QA gate;
- smoke/demo implementation;
- smoke/demo contract;
- CLI QA gate;
- CLI implementation;
- CLI contract;
- minimal runtime QA gate;
- minimal runtime implementation;
- minimal runtime contract;
- WSL/repository guard;
- PostgreSQL-only regression guard.

## Repository safety requirements

Before closing this phase:

- this readiness gate document must exist;
- this readiness gate test must exist;
- the real folder authorization QA gate document must exist;
- the real folder authorization QA gate test must exist;
- the real folder authorization contract document must exist;
- the real folder authorization contract test must exist;
- the latest real folder authorization QA gate stable tag must exist;
- the latest real folder authorization QA gate stable tag must point to the expected commit;
- the latest real folder authorization QA gate stable tag must be an ancestor of current `HEAD`;
- protected files must not be staged;
- `.env` must not be staged;
- database files must not be staged;
- backup files must not be staged;
- SaaS, backend, frontend, Docker, Alembic, Stripe, AI Jobs, credits, and ledger files must not be staged;
- WSL/repository guard must pass;
- PostgreSQL-only regression guard must pass.

## Acceptance criteria

This phase is accepted only if:

- this dry-run readiness gate document exists;
- this dry-run readiness gate test exists;
- this phase is documented as docs/test-only;
- this phase clearly states that it does not execute the CLI against real folders;
- this phase clearly states that it does not authorize dry-run execution;
- the latest real folder authorization QA gate stable tag is documented;
- the latest real folder authorization QA gate stable tag points to the expected commit;
- the prerequisite chain is documented;
- the required dry-run candidate record fields are documented;
- eligible candidate class restrictions are documented;
- dry-run behavior remains minimal and sanitized;
- explicit non-authorization is documented;
- blocked operations remain blocked;
- the required test matrix is documented;
- previous real folder authorization QA gate tests still pass;
- previous real folder authorization contract tests still pass;
- previous smoke/demo readiness tests still pass;
- previous smoke/demo QA gate tests still pass;
- previous smoke/demo implementation tests still pass;
- previous smoke/demo contract tests still pass;
- previous CLI tests still pass;
- previous runtime tests still pass;
- repository guards still pass.
