# CID Local Media Agent — Controlled Non-Customer Fixture Pack Plan Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.PLAN.GATE.V1`
- Expected result token: `LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_PLAN_GATE_V1_CLOSED`
- Previous dependency: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CONTRACT.GATE.V1`
- Technical decision carried forward: `CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN`
- Gate type: documentation and QA only.

## Purpose

This gate defines the planned controlled non-customer fixture pack that will be created in a later explicit gate. It does not create fixture files, media files, binary files, generated artifacts, runtime modules, scanner behavior, metadata extraction behavior, or package entrypoints.

The purpose is to turn the previous fixture pack contract into an actionable plan before any fixture bytes exist. The plan establishes allowed names, allowed directory boundaries, intended fixture roles, expected integrity metadata policy, prohibited material, review requirements, and the later gate that may create the fixtures.

## Closed decision

The planned next implementation path remains:

`CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN`

The immediate next technical step after this gate is not ffprobe execution, not scanner execution, and not real media processing. The next step is a separate fixture pack creation gate that may create only explicitly planned non-customer controlled fixtures.

## Scope allowed in this gate

This gate may add only:

1. This planning document.
2. A QA test that validates the planning document.

No implementation is allowed in this gate.

## Scope explicitly forbidden in this gate

This gate must not:

- create fixture binaries;
- create audio, video, image, subtitle, archive, or sidecar payload files;
- execute ffprobe;
- execute FFmpeg;
- add subprocess wrappers;
- run scanner logic;
- add scanner runtime;
- modify CLI entrypoints;
- modify `pyproject.toml`;
- modify package metadata;
- touch SaaS code;
- touch database code;
- touch backend code;
- touch frontend code;
- touch installer code;
- touch `.env`;
- use customer material;
- use real production material;
- write outside the repository through this gate;
- authorize pilot execution;
- authorize external installation.

## Planned fixture root

The future fixture pack root is planned as:

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack/v1/`

This path is reserved by this plan, but this gate does not create it.

A later fixture creation gate must create the root only if it also creates a manifest and integrity metadata in the same controlled change.

## Planned manifest file

A later creation gate is expected to create:

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack/v1/manifest.controlled.json`

The manifest is planned to contain:

- fixture pack version;
- fixture IDs;
- relative paths;
- media type declarations;
- byte sizes;
- SHA256 hashes;
- generation method;
- non-customer provenance statement;
- allowed use cases;
- forbidden use cases;
- validation status;
- creation gate identity;
- reviewer notes.

This gate does not create the manifest.

## Planned fixture entries

The future fixture pack should be intentionally small. It should support the first read-only single-file metadata chain without inviting scanner scope creep.

### Planned fixture 001 — minimal video container

- Fixture ID: `CONTROLLED_NON_CUSTOMER_FIXTURE_VIDEO_MINIMAL_V1`
- Planned relative path: `media/video/controlled_non_customer_minimal_video_v1.mp4`
- Planned role: safe single-file metadata target for future read-only metadata extraction.
- Expected characteristics: short duration, no customer material, no identifiable person, no copyrighted source content, deterministic generation notes.
- Planned integrity fields: byte size and SHA256.
- Status in this gate: planned only, not created.

### Planned fixture 002 — minimal audio container

- Fixture ID: `CONTROLLED_NON_CUSTOMER_FIXTURE_AUDIO_MINIMAL_V1`
- Planned relative path: `media/audio/controlled_non_customer_minimal_audio_v1.wav`
- Planned role: future audio metadata target after the video fixture path has passed.
- Expected characteristics: generated tone or silent controlled audio, no voices, no copyrighted source content, deterministic generation notes.
- Planned integrity fields: byte size and SHA256.
- Status in this gate: planned only, not created.

### Planned fixture 003 — non-media reject file

- Fixture ID: `CONTROLLED_NON_CUSTOMER_FIXTURE_NON_MEDIA_REJECT_V1`
- Planned relative path: `non_media/controlled_non_customer_non_media_reject_v1.txt`
- Planned role: future negative-path validation for scanner boundary and media detection policy.
- Expected characteristics: small UTF-8 text, no sensitive content.
- Planned integrity fields: byte size and SHA256.
- Status in this gate: planned only, not created.

### Planned fixture 004 — manifest-only metadata target

- Fixture ID: `CONTROLLED_NON_CUSTOMER_FIXTURE_MANIFEST_ONLY_METADATA_V1`
- Planned relative path: `metadata/controlled_non_customer_manifest_notes_v1.json`
- Planned role: future validation that metadata sidecars are not treated as media payloads unless explicitly allowed.
- Expected characteristics: JSON notes only, no embedded media, no secrets.
- Planned integrity fields: byte size and SHA256.
- Status in this gate: planned only, not created.

## Creation policy for later gate

The later fixture creation gate must:

1. create only the planned fixture root;
2. create only the planned fixture files or a justified reduced subset;
3. generate or store exact byte sizes;
4. generate or store SHA256 hashes;
5. prove that files are non-customer and non-production;
6. keep fixtures small;
7. include a manifest;
8. include QA tests for integrity;
9. avoid invoking scanner runtime;
10. avoid invoking ffprobe or FFmpeg unless a later explicit creation mechanism requires it and is authorized by its own gate.

## Integrity policy

Every future fixture file must have:

- stable relative path;
- stable filename;
- byte size recorded in manifest;
- SHA256 recorded in manifest;
- declared fixture role;
- declared allowed uses;
- declared forbidden uses;
- non-customer provenance statement;
- generation or origin note;
- review status.

Any fixture whose size or SHA does not match the manifest must fail closed.

## Allowed use after future creation

After a later creation gate, fixtures may be used only for:

- local QA;
- read-only single-file metadata chain development;
- visible report development over controlled fixture files;
- future scanner boundary tests limited to the fixture root;
- safety and privacy validation.

## Forbidden use after future creation

Even after fixture creation, the fixture pack must not authorize:

- customer material;
- production rushes;
- external client delivery;
- broad folder scanning;
- installation outside the controlled environment;
- SaaS upload;
- database ingestion;
- commercial claim of product readiness;
- pilot execution.

## Acceptance criteria for this plan gate

This gate can close only if:

- the document identifies the phase and expected result token;
- the document states that no fixtures are created;
- the document defines the future fixture root;
- the document defines a future manifest;
- the document names at least four planned fixture entries;
- the document defines byte-size and SHA256 policy;
- the document keeps ffprobe and FFmpeg execution blocked;
- the document keeps scanner execution blocked;
- the document keeps customer and production material blocked;
- the document keeps runtime, pyproject, SaaS, database, backend, frontend, and installer changes blocked;
- the QA test passes;
- WSL/repo/secrets guard passes;
- PostgreSQL-only regression guard passes.

## Non-authorization statement

Closing this gate does not authorize fixture creation. It only authorizes the plan for a later fixture creation gate.

Closing this gate does not authorize read-only metadata extraction, ffprobe execution, FFmpeg execution, scanner execution, visible report generation over fixture files, external demo expansion, pilot execution, installation, SaaS integration, or customer material processing.

## Next expected gate

Recommended next phase:

`CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.READINESS.GATE.V1`

Purpose of the next gate: decide whether the planned fixture pack can be created, with exact file list, integrity expectations, generation method, and final safety boundaries.
