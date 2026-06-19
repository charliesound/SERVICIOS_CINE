# CID Local Media Agent — Real Preflight Minimal Runtime CLI Smoke Demo Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.READINESS.GATE.V1`

## Objective

This phase is a conservative readiness gate before any step that could be confused with a real-folder smoke invocation.

This phase is docs/test-only.

It does not execute the CLI against real folders. It does not authorize real client media. It does not authorize mounted Windows paths. It does not authorize cloud-synced folders. It does not authorize network shares. It does not authorize scanner integration. It does not authorize ffprobe or ffmpeg. It does not authorize report generation. It does not authorize media decoding, transcription, translation, subtitles, sync analysis, NLE export, upload, packaging, installer, desktop app, licensing, SaaS, backend, frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, or ledger work.

The only purpose is to confirm that the current repository state is ready for a future separately authorized gate, while preserving the current synthetic-only privacy boundary.

## Current stable prerequisite

The latest stable prerequisite is:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-smoke-demo-qa-gate-v1-20260619`

Expected stable commit:

`edb1600c87e34e0cff8ed830118f3214a48161c4`

## Prerequisite phase chain

The readiness gate requires the following phase chain to exist:

1. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CONTRACT.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.IMPLEMENTATION.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.QA.GATE.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.CONTRACT.V1`
5. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.IMPLEMENTATION.V1`
6. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.QA.GATE.V1`
7. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.CONTRACT.V1`
8. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.IMPLEMENTATION.V1`
9. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.QA.GATE.V1`

## Required local files

The readiness gate requires these files to exist:

- `scripts/cid_local_media_agent_real_preflight.py`
- `scripts/cid_local_media_agent_real_preflight_cli.py`
- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract.py`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo.py`
- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_qa_gate.py`

## Required repository prechecks before any later real-folder-related discussion

Before any later phase that moves beyond synthetic temporary folders, the operator must confirm:

- `git status --short --untracked-files=all` is reviewed;
- current `HEAD` is known;
- `origin/main` is not behind the expected local branch state;
- the latest stable smoke/demo QA gate tag exists;
- the latest stable smoke/demo QA gate tag is an ancestor of the current `HEAD`;
- protected files are not staged;
- `.env` is not staged;
- .env is not staged;
- database files are not staged;
- backups are not staged;
- frontend/backend/SaaS/Docker/Alembic/Stripe/AI Jobs/credits/ledger files are not staged unless a separate explicit phase authorizes them;
- `guard_wsl_repo.sh` passes;
- `guard_no_sqlite_regressions.sh` passes.

## Required test matrix

This readiness gate requires the following matrix to remain green:

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

## Privacy boundary

The current approved privacy boundary remains:

- synthetic temporary folders only;
- synthetic placeholder files only;
- no real client media;
- no real project folders;
- no raw private paths in CLI output;
- no raw filenames in CLI output;
- no client names in CLI output;
- no project names in CLI output;
- sanitized JSON output only;
- sanitized text output only;
- no selected output folder writes;
- no selected input folder changes after fixture setup.

## Explicit non-authorization

This readiness gate explicitly does not authorize:

- real-folder smoke invocation;
- real client media;
- mounted Windows paths;
- `/mnt/` paths;
- /mnt/ paths;
- `C:\` paths;
- c:\ paths;
- cloud-synced folders;
- network shares;
- scanner integration;
- ffprobe;
- ffmpeg;
- media probing;
- media decoding;
- report generation;
- synthetic visible report integration;
- waveform analysis;
- audio sync;
- clap detection;
- timecode extraction;
- transcription;
- translation;
- subtitle generation;
- DaVinci Resolve integration;
- Avid integration;
- EDL/XML/AAF/OTIO/timeline generation;
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

## Allowed decision states

The readiness gate may produce only:

- `READINESS_PASS`
- `READINESS_FAIL`
- `READINESS_BLOCKED`

`READINESS_PASS` means the repo is ready to discuss the next conservative gate.

`READINESS_FAIL` means tests or prerequisites are missing and must be corrected.

`READINESS_BLOCKED` means the proposed next action would cross the real-media, privacy, integration, dependency, or protected-file boundary.

## Acceptance criteria

This phase is accepted only if:

- this readiness gate document exists;
- this readiness gate test exists;
- all prerequisite smoke/demo files exist;
- the latest smoke/demo QA gate stable tag exists;
- the latest smoke/demo QA gate stable tag is an ancestor of current `HEAD`;
- the prerequisite phase chain is documented;
- the repository prechecks are documented;
- the required test matrix is documented;
- the privacy boundary is documented;
- explicit non-authorization is documented;
- blocked operations remain blocked;
- previous smoke/demo QA gate tests still pass;
- previous smoke/demo implementation tests still pass;
- previous smoke/demo contract tests still pass;
- previous CLI tests still pass;
- previous runtime tests still pass;
- repository guards still pass.
