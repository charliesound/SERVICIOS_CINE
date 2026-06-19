# CID Local Media Agent — Real Preflight Minimal Runtime CLI Real Folder Authorization QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1`

## Objective

This phase audits the real-folder authorization contract before any future dry-run readiness gate is considered.

This phase is docs/test-only.

It does not execute the CLI against a real folder. It does not authorize a real-folder smoke invocation. It does not authorize real client media. It does not authorize mounted Windows paths. It does not authorize cloud-synced folders. It does not authorize network shares. It does not authorize scanner integration. It does not authorize ffprobe or ffmpeg. It does not authorize media probing, media decoding, report generation, sync analysis, transcription, translation, subtitles, NLE export, upload, packaging, desktop app, installer, licensing, SaaS, backend, frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, or ledger work.

The only purpose is to verify that the authorization contract is complete, conservative, and non-executing.

## Contract under audit

The contract under audit is:

`docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_contract_v1.md`

The contract test under audit is:

`tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_authorization_contract.py`

## Current clean stable prerequisite

The latest clean stable prerequisite is:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-authorization-contract-v1-20260619`

Expected prerequisite commit:

`0f31ac90c86d9daa7ebb066d0a89d51baa6f0e73`

## QA decision states

This QA gate allows only:

- `QA_PASS`
- `QA_FAIL`
- `QA_BLOCKED`

`QA_PASS` means the authorization contract is safe to use as the basis for a later dry-run readiness gate.

`QA_FAIL` means the contract is incomplete, ambiguous, or inconsistent.

`QA_BLOCKED` means the contract appears to authorize a blocked action or cross a privacy, dependency, path, data, or integration boundary.

## Required QA checks

This QA gate must verify that the authorization contract:

- exists;
- has a matching test file;
- is docs/test-only;
- does not execute the CLI against a real folder;
- does not authorize real-folder smoke invocation;
- does not authorize real client media execution;
- documents the clean stable prerequisite tag;
- documents the superseded readiness tag as not the clean anchor;
- documents authorization decision states;
- documents all required human authorization fields;
- documents eligible folder class restrictions;
- documents blocked folder classes;
- documents conservative real media policy;
- documents sanitized output behavior;
- documents default no-write behavior;
- documents blocked operations;
- documents later required gates before execution;
- avoids the bad regression-guard literal previously recovered;
- keeps the PostgreSQL-only wording neutral and guard-safe.

## Required authorization field audit

The contract must contain all required authorization fields:

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

## Required path and folder audit

The contract must keep these blocked:

- entire disk;
- repository root;
- home directory root;
- mounted Windows path;
- `/mnt/` path;
- /mnt/ path;
- Windows drive path;
- cloud-synced directory;
- network share;
- production delivery folder;
- backup folder;
- database folder.

## Required operation boundary audit

The contract must keep these blocked:

- real-folder smoke invocation;
- broad real project scan;
- whole-disk scan;
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

## Required later gate audit

The contract must continue to require these later gates before any execution:

1. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.EXECUTION.V1`

The contract must state that the contract alone does not authorize execution.

## Repository safety requirements

Before closing this QA gate:

- this QA gate document must exist;
- this QA gate test must exist;
- the authorization contract document must exist;
- the authorization contract test must exist;
- the latest authorization contract stable tag must exist;
- the latest authorization contract stable tag must point to the expected commit;
- the latest authorization contract stable tag must be an ancestor of current `HEAD`;
- protected files must not be staged;
- `.env` must not be staged;
- database files must not be staged;
- backup files must not be staged;
- SaaS, backend, frontend, Docker, Alembic, Stripe, AI Jobs, credits, and ledger files must not be staged;
- WSL/repository guard must pass;
- PostgreSQL-only regression guard must pass.

## Acceptance criteria

This phase is accepted only if:

- this QA gate document exists;
- this QA gate test exists;
- this phase is documented as docs/test-only;
- this phase clearly states that it does not execute the CLI against real folders;
- the authorization contract document exists;
- the authorization contract test exists;
- the clean stable authorization contract tag is documented;
- the clean stable authorization contract tag points to the expected commit;
- the authorization contract is verified as non-executing;
- all required authorization fields are verified;
- eligible folder restrictions are verified;
- blocked folder classes are verified;
- real media remains not authorized by the contract;
- output behavior remains sanitized and no-write by default;
- blocked operations remain blocked;
- later required gates are verified;
- previous authorization contract tests still pass;
- previous readiness gate tests still pass;
- previous smoke/demo QA gate tests still pass;
- previous smoke/demo implementation tests still pass;
- previous smoke/demo contract tests still pass;
- previous CLI tests still pass;
- previous runtime tests still pass;
- repository guards still pass.
