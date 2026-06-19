# CID Local Media Agent — Real Preflight Minimal Runtime CLI Smoke Demo Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.CONTRACT.V1`

## Objective

This phase defines the contract for a future local smoke/demo invocation of the already implemented minimal real preflight CLI.

This phase is documentation/test-only.

It does not create smoke/demo runtime code. It does not modify the CLI runtime. It does not modify the preflight runtime. It does not modify scanner behavior. It does not generate reports. It does not process media content. It does not add packaging, installer, desktop, licensing, SaaS, backend, frontend, database, billing, upload, or cloud behavior.

The only purpose of this phase is to define how a future smoke/demo test may exercise the existing CLI with synthetic local folders and synthetic placeholder files.

## Current stable prerequisite

This contract depends on the already closed phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.QA.GATE.V1`

The CLI under the previous QA gate is:

`scripts/cid_local_media_agent_real_preflight_cli.py`

The runtime called by that CLI is:

`scripts/cid_local_media_agent_real_preflight.py`

## Future smoke/demo test target file

A later implementation phase may create this file:

`tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo.py`

This current phase must not create that file.

## Future smoke/demo phase

A later implementation phase, if opened, should be:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.IMPLEMENTATION.V1`

That later phase must start from a clean repository precheck and must include tests before or with implementation.

## Smoke/demo purpose

The future smoke/demo may do only this:

- create temporary synthetic input and output folders;
- create synthetic placeholder files with safe fake media extensions;
- invoke the existing CLI boundary;
- verify sanitized JSON output;
- verify sanitized text output;
- verify exit code mapping;
- verify no private path leakage;
- verify no raw filename leakage;
- verify no files are created in the selected output folder;
- verify no files are created, modified, or deleted in the selected input folder except synthetic fixture setup performed before CLI invocation.

## Synthetic fixture boundary

The future smoke/demo may create only synthetic placeholder files.

Allowed synthetic placeholder extensions:

- `.mov`;
- `.mp4`;
- `.mxf`;
- `.wav`;
- `.aif`;
- `.aiff`;
- `.txt`;
- `.custom`.

The future smoke/demo must not use real client media.

The future smoke/demo must not use real project folders.

The future smoke/demo must not use private production paths.

The future smoke/demo must not use mounted Windows paths.

The future smoke/demo must not use cloud-synced folders.

The future smoke/demo must not use network shares.

## Required smoke/demo cases

The future smoke/demo must verify at least these cases:

- pass case with one accepted synthetic placeholder file;
- fail case with no accepted extension;
- blocked case with output folder inside input folder;
- JSON output sanitization;
- text output sanitization;
- custom accepted extension forwarding;
- file-count limit forwarding;
- invalid usage sanitized error;
- selected output folder remains empty after CLI invocation;
- selected input folder contains only pre-created synthetic fixtures after CLI invocation.

## Required CLI invocation boundary

The future smoke/demo must invoke only the approved minimal CLI:

`scripts/cid_local_media_agent_real_preflight_cli.py`

The future smoke/demo must not invoke:

- scanner CLIs;
- synthetic visible report CLIs;
- media probing CLIs;
- transcription CLIs;
- translation CLIs;
- subtitle CLIs;
- sync CLIs;
- NLE export CLIs;
- upload CLIs;
- SaaS CLIs;
- billing CLIs;
- database CLIs.

## Required output checks

The future smoke/demo must assert that JSON and text output never include:

- full private paths;
- raw filenames;
- client names;
- project names;
- absolute paths;
- relative source paths;
- environment variables;
- user account names;
- hostnames;
- media hashes;
- media content;
- stream metadata;
- codec metadata;
- timecode metadata;
- embedded metadata;
- transcript text;
- subtitle text;
- waveform data;
- frame data;
- thumbnail data.

## Required exit code mapping

The future smoke/demo must verify this mapping through CLI behavior:

- `PREFLIGHT_PASS` -> exit code `0`;
- `PREFLIGHT_FAIL` -> exit code `2`;
- `PREFLIGHT_BLOCKED` -> exit code `3`;
- invalid CLI usage -> exit code `64`.

The future smoke/demo may verify internal-error mapping only through safe monkeypatching or isolated direct invocation, never by leaking stack traces.

## No-write boundary

The future smoke/demo must prove that the CLI does not write inside the selected output folder.

The future smoke/demo must prove that the CLI does not create, modify, or delete files in the selected input folder after fixture setup.

The future smoke/demo must not authorize creation of:

- reports;
- manifests;
- indexes;
- caches;
- thumbnails;
- waveform data;
- transcripts;
- subtitles;
- sidecars;
- NLE export files;
- temporary files inside selected folders.

## Local-only boundary

The future smoke/demo must remain local-only.

It must not:

- upload files;
- transfer files to cloud services;
- call remote APIs;
- send telemetry;
- connect to SaaS services;
- connect to databases;
- invoke desktop apps;
- invoke NLE apps;
- invoke media tools.

## Operations still blocked

This contract does not authorize:

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

- the smoke/demo contract document exists;
- the phase is documentation/test-only;
- the future smoke/demo test file is named;
- the future smoke/demo implementation phase is named;
- the current CLI file exists;
- the current runtime file exists;
- the current CLI QA gate document exists;
- synthetic fixture boundaries are enumerated;
- required smoke/demo cases are enumerated;
- CLI invocation boundary is enumerated;
- output sanitization requirements are enumerated;
- exit code mapping requirements are enumerated;
- no-write behavior is required;
- local-only behavior is required;
- blocked operations remain blocked;
- this phase does not create the future smoke/demo test implementation file.
