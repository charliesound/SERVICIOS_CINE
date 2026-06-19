# CID Local Media Agent — Real Preflight Minimal Runtime CLI Smoke Demo QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.QA.GATE.V1`

## Objective

This phase audits the synthetic local CLI smoke/demo implementation.

This phase is a QA gate.

It does not add smoke/demo features. It does not widen CLI scope. It does not modify the CLI runtime. It does not modify the preflight runtime. It does not modify scanner behavior. It does not generate reports. It does not process media content. It does not use real client media. It does not use real project folders. It does not add packaging, installer, desktop, licensing, SaaS, backend, frontend, database, billing, upload, or cloud behavior.

The only purpose of this phase is to verify that the current smoke/demo remains synthetic, local-only, sanitized, and inside the approved minimal CLI smoke/demo contract.

## Smoke/demo under audit

The smoke/demo implementation file under audit is:

`tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo.py`

## Governing contract

The governing smoke/demo contract is:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.CONTRACT.V1`

The implementation phase under audit is:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.IMPLEMENTATION.V1`

## Required QA decision states

This QA gate may produce only these conceptual decisions:

- `QA_PASS`
- `QA_FAIL`
- `QA_BLOCKED`

`QA_PASS` means the smoke/demo remains inside the approved synthetic local boundary.

`QA_FAIL` means one or more expected checks failed and must be corrected before continuing.

`QA_BLOCKED` means the smoke/demo appears to cross a real-media, privacy, integration, repository, dependency, or scope boundary.

## Required smoke/demo boundary

The smoke/demo must remain:

- test-only;
- synthetic-only;
- local-only;
- deterministic;
- temporary-folder-only;
- placeholder-file-only;
- free of real client media;
- free of real project folders;
- free of mounted Windows paths;
- free of cloud-synced folders;
- free of network shares;
- free of scanner integration;
- free of media probing;
- free of media decoding;
- free of report generation.

## Required smoke/demo behavior

The smoke/demo must prove:

- sanitized JSON output;
- sanitized text output;
- exit code `0` for `PREFLIGHT_PASS`;
- exit code `2` for `PREFLIGHT_FAIL`;
- exit code `3` for `PREFLIGHT_BLOCKED`;
- exit code `64` for invalid CLI usage;
- no private path leakage;
- no raw filename leakage;
- no selected output folder writes;
- no selected input folder changes after fixture setup;
- custom accepted extension forwarding;
- file-count limit forwarding.

## Required source boundary

The smoke/demo source must not import or invoke:

- scanner modules;
- synthetic visible report modules;
- media probing wrappers;
- transcription modules;
- translation modules;
- sync modules;
- subtitle modules;
- NLE export modules;
- SaaS modules;
- database modules;
- billing modules;
- licensing modules;
- upload modules;
- network clients;
- subprocess execution.

## Required fixture boundary

The smoke/demo may create only synthetic placeholder files inside `tmp_path`.

Allowed synthetic placeholder extensions:

- `.mov`;
- `.wav`;
- `.txt`;
- `.custom`.

The smoke/demo must not use:

- real client media;
- mounted Windows paths;
- `/mnt/` paths;
- `C:\` paths;
- cloud-synced folders;
- network shares;
- production project names;
- production client names;
- real source media folders.

## Operations still blocked

This QA gate does not authorize:

- real-folder smoke invocation;
- real client media;
- mounted Windows paths;
- cloud-synced folders;
- network shares;
- media decoding;
- stream probing;
- codec probing;
- container probing;
- real file probing tools;
- media conversion tools;
- frame extraction;
- thumbnail generation;
- waveform generation;
- audio analysis;
- speech recognition;
- transcription;
- translation;
- subtitle generation;
- sync analysis;
- clap detection;
- timecode extraction;
- scanner integration;
- report generation;
- synthetic visible report integration;
- DaVinci Resolve integration;
- Avid integration;
- NLE export;
- EDL generation;
- XML generation;
- AAF generation;
- OTIO generation;
- timeline generation;
- upload;
- cloud transfer;
- desktop packaging;
- installer creation;
- licensing activation;
- SaaS integration;
- backend changes;
- frontend changes;
- database changes;
- billing changes.

## Acceptance criteria

This phase is accepted only if:

- the smoke/demo QA gate document exists;
- the smoke/demo implementation test exists;
- the smoke/demo contract document exists;
- the CLI file exists;
- the runtime file exists;
- the smoke/demo remains synthetic-only;
- the smoke/demo uses temporary folders;
- the smoke/demo uses placeholder files only;
- JSON output sanitization is verified;
- text output sanitization is verified;
- exit code mapping is verified;
- no private path leakage is verified;
- no raw filename leakage is verified;
- selected output folder no-write behavior is verified;
- selected input folder no-change-after-fixture-setup behavior is verified;
- smoke/demo source import boundaries are verified;
- blocked operation terms are absent from smoke/demo source;
- previous smoke/demo implementation tests still pass;
- previous smoke/demo contract tests still pass;
- previous CLI QA tests still pass;
- previous CLI implementation tests still pass;
- previous runtime tests still pass;
- repository guards still pass.
