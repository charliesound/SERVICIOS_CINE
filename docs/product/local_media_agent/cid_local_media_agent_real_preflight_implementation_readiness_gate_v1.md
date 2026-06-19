# CID Local Media Agent — Real Preflight Implementation Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.READINESS.GATE.V1`

## Objective

This phase defines a readiness gate before opening any future real preflight implementation phase.

This phase is documentation/test-only.

It does not implement runtime behavior. It does not create a real preflight function, CLI entry point, scanner integration, report generator, desktop flow, packaging flow, installer, licensing flow, SaaS flow, database flow, billing flow, or media-processing flow.

The only purpose of this phase is to decide whether a later implementation phase may be opened under the previously approved boundary.

## Current stable prerequisite

This readiness gate depends on the already closed phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.BOUNDARY.CONTRACT.V1`

The boundary contract remains authoritative.

## Gate decision states

The readiness gate may produce only one of these decision states:

- `IMPLEMENTATION_READY`
- `IMPLEMENTATION_NOT_READY`
- `IMPLEMENTATION_BLOCKED`

## Decision state meaning

`IMPLEMENTATION_READY` means a later phase may open a minimal real preflight implementation strictly limited to the approved filesystem-metadata boundary.

`IMPLEMENTATION_NOT_READY` means one or more prerequisite contracts, tests, guardrails, or review conditions are missing or incomplete.

`IMPLEMENTATION_BLOCKED` means implementation must not be opened because a privacy, safety, runtime, scope, SaaS, billing, media-processing, or repository boundary is unclear or violated.

## Required prerequisite chain

The readiness gate requires the following closed phases to remain present and valid:

- `CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.V1`
- `CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.QA.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.REAL.MEDIA.PRIVACY.SAFETY.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1`
- `CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.QA.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1`
- `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.QA.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.BOUNDARY.CONTRACT.V1`

## Required repository condition

The future implementation phase must not be opened unless:

- the repository is clean before implementation work starts;
- the current branch is `main`;
- the working directory is `/opt/SERVICIOS_CINE`;
- the work is performed inside WSL Ubuntu;
- .venv is active;
- no Windows path is used;
- no protected file is modified;
- no `.env` file is staged;
- no real database file is staged;
- no backup file is staged;
- PostgreSQL-only guardrails remain intact;
- the WSL repo guard passes;
- the PostgreSQL-only regression guard passes.

## Protected areas that remain closed

The readiness gate does not authorize changes to:

- `.env`;
- real databases;
- backups;
- Docker;
- Alembic;
- frontend;
- backend;
- SaaS runtime;
- Stripe;
- AI Jobs;
- credits;
- ledger;
- billing;
- licensing;
- installer;
- desktop app;
- shell launcher;
- packaging;
- upload flows;
- cloud transfer flows.

## Future implementation scope if ready

If this gate is passed, a later implementation phase may open only a minimal real preflight implementation.

That future implementation must remain limited to local filesystem metadata.

Allowed future implementation scope:

- check whether selected input folder exists;
- check whether selected input folder is a directory;
- check whether selected input folder is locally accessible;
- check whether selected output folder exists or can be safely prepared;
- check input and output separation;
- count selected media files;
- count accepted extensions;
- count ignored extensions;
- count rejected extensions;
- calculate coarse total size bucket;
- calculate maximum detected scan depth;
- detect symlink presence without following symlinks;
- return sanitized failed check identifiers;
- return sanitized remediation guidance.

## Future implementation hard limits

The future implementation must preserve these conservative limits unless a later contract explicitly changes them:

- maximum selected media files: 25;
- maximum total selected media size: 10 GB;
- maximum scan depth: 3;
- accepted extensions: `.mov`, `.mp4`, `.mxf`, `.wav`, `.aif`, `.aiff`;
- symlink following: disabled;
- traversal outside selected folder: blocked;
- output inside input folder: blocked.

## Required future result states

Any future real preflight implementation must return exactly one of:

- `PREFLIGHT_PASS`
- `PREFLIGHT_FAIL`
- `PREFLIGHT_BLOCKED`

## Required future payload boundary

The future real preflight payload may include only:

- sanitized input folder label;
- sanitized output folder label;
- media file count;
- total selected media size bucket;
- maximum detected scan depth;
- accepted extension counts;
- ignored extension counts;
- rejected extension counts;
- failed check identifiers;
- remediation guidance without private full paths.

The future real preflight payload must not include:

- full private paths;
- raw filenames;
- client names;
- project names;
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

## Operations still blocked after this gate

Passing this readiness gate must not authorize:

- media decoding;
- stream probing;
- codec probing;
- container probing;
- ffprobe on real files;
- ffmpeg on real files;
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
- real report generation;
- synthetic visible report integration;
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

## Implementation opening criteria

A later implementation phase may be opened only if all of these are true:

- prerequisite contracts are present;
- prerequisite QA gates are present;
- implementation boundary contract is present;
- this readiness gate is present;
- this readiness gate test passes;
- previous real preflight contract tests pass;
- boundary contract tests pass;
- WSL repo guard passes;
- PostgreSQL-only guard passes;
- staged diff contains only files authorized by the current phase;
- human operator intentionally opens the next implementation phase.

## Required next implementation phase constraints

The next implementation phase, if opened, must:

- be named explicitly;
- identify exact target runtime file or files before editing;
- start with a clean repo precheck;
- include tests before or with implementation;
- remain fail-closed;
- avoid importing scanner code unless a later scanner-integration phase is explicitly opened;
- avoid invoking ffprobe or ffmpeg;
- avoid reading media bytes;
- avoid exposing raw filenames or full paths;
- avoid writing output inside selected input media folders;
- avoid SaaS/backend/frontend/database/billing changes.

## Blocker conditions

Implementation must remain blocked if:

- any prerequisite contract is missing;
- any prerequisite test is failing;
- the boundary contract is not present;
- privacy-safe reporting cannot be guaranteed;
- output separation is unclear;
- symlink behavior is unclear;
- traversal blocking is unclear;
- size and count limits are unclear;
- sanitized payload fields are unclear;
- prohibited payload fields are unclear;
- blocked media operations are unclear;
- protected repo areas would be touched;
- runtime scope would expand beyond filesystem metadata.

## Non-goals

This phase does not:

- implement real preflight;
- modify CLI behavior;
- modify scanner behavior;
- generate real reports;
- process real media;
- invoke media tools;
- connect to DaVinci Resolve;
- create NLE exports;
- create subtitles;
- create transcripts;
- translate media;
- sync audio and video;
- package an app;
- create a desktop app;
- create an installer;
- add licensing;
- connect to SaaS;
- change backend;
- change frontend;
- change databases;
- change billing.

## Acceptance criteria

This phase is accepted only if:

- the readiness gate document exists;
- the readiness gate states that it is documentation/test-only;
- the readiness gate depends on the implementation boundary contract;
- the readiness gate defines exactly three decision states;
- the prerequisite chain is enumerated;
- repository conditions are enumerated;
- future implementation scope is limited to filesystem metadata;
- future hard limits are preserved;
- future payload boundaries are enumerated;
- blocked operations remain blocked;
- next implementation constraints are enumerated;
- no runtime source file is changed by this phase.

## Recommended next phase

If this readiness gate is accepted, the next possible microphase is:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CONTRACT.V1`

That next phase should still be conservative. It should define the exact target file, function name, data shape, test fixtures, and fail-closed expectations before any broad runtime implementation is allowed.
