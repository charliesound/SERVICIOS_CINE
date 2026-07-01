# CID Local Media Agent — Controlled Non-Customer Fixture Pack Creation Readiness Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.READINESS.GATE.V1`
- Expected result token: `LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_CREATION_READINESS_GATE_V1_CLOSED`
- Previous dependency: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.PLAN.GATE.V1`
- Required earlier contract: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CONTRACT.GATE.V1`
- Technical decision carried forward: `CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN`
- Gate type: documentation and QA only.

## Purpose

This gate reviews whether the controlled non-customer fixture pack contract and plan are ready for a later explicit creation gate. It does not create fixture files, media files, binary files, generated artifacts, runtime modules, scanner behavior, metadata extraction behavior, or package entrypoints.

The purpose is to prevent an uncontrolled jump from fixture planning to fixture bytes. The readiness review checks whether the planned fixture root, manifest policy, file list, integrity policy, allowed use, forbidden use, and creation boundaries are sufficiently explicit to support a later fixture creation gate.

## Closed decision

The readiness decision is:

`READY_FOR_SEPARATE_CONTROLLED_FIXTURE_PACK_CREATION_GATE_WITH_BOUNDARIES`

This means the next gate may propose creating the planned fixture pack, but this gate itself does not authorize or perform fixture creation.

## Scope allowed in this gate

This gate may add only:

1. This readiness review document.
2. A QA test that validates the readiness review document.

No implementation is allowed in this gate.

## Scope explicitly forbidden in this gate

This gate must not:

- create fixture binaries;
- create media files;
- create audio, video, image, subtitle, archive, or sidecar payload files;
- create `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack/v1/`;
- create `manifest.controlled.json`;
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

## Readiness inputs reviewed

This readiness review depends on the earlier contract and plan.

### Contract input

The contract gate established that a controlled non-customer fixture pack must be small, deterministic, local, reviewable, and separated from customer material. It also established that future fixture use must remain bounded before any read-only single-file metadata chain.

### Plan input

The plan gate established the planned fixture root:

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack/v1/`

The plan gate also established the planned manifest:

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack/v1/manifest.controlled.json`

The planned fixture entries remain:

- `CONTROLLED_NON_CUSTOMER_FIXTURE_VIDEO_MINIMAL_V1`
- `CONTROLLED_NON_CUSTOMER_FIXTURE_AUDIO_MINIMAL_V1`
- `CONTROLLED_NON_CUSTOMER_FIXTURE_NON_MEDIA_REJECT_V1`
- `CONTROLLED_NON_CUSTOMER_FIXTURE_MANIFEST_ONLY_METADATA_V1`

## Readiness checks

The later creation gate may be prepared only if all readiness checks below remain true.

### Root readiness

The future fixture root is explicit, narrow, and repo-local. No broad folder root is permitted.

Required future root:

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack/v1/`

The later creation gate must fail closed if it attempts to create fixtures outside this root.

### Manifest readiness

The planned manifest is explicit and mandatory.

Required future manifest:

`manifest.controlled.json`

The later creation gate must include manifest fields for fixture pack version, fixture IDs, relative paths, byte sizes, SHA256 hashes, generation method, non-customer provenance statement, allowed uses, forbidden uses, validation status, creation gate identity, and reviewer notes.

### Fixture list readiness

The planned fixture list is intentionally small and enough for the first safe metadata path. The later creation gate may create the planned files or a justified reduced subset, but it must not expand the pack without a new planning gate.

The later creation gate must preserve these planned roles:

1. minimal video metadata target;
2. minimal audio metadata target;
3. non-media reject target;
4. manifest-only metadata notes target.

### Integrity readiness

The later creation gate must record exact byte size and SHA256 for every created file. Every file must have stable relative path, stable filename, declared role, allowed uses, forbidden uses, generation or origin note, and review status.

Any mismatch between manifest and bytes must fail closed.

### Provenance readiness

The later creation gate must prove that every fixture is non-customer, non-production, non-personal, and safe for internal QA. It must not include rushes, camera originals, production audio, client material, copyrighted source content, voices, faces, private locations, or identifying metadata.

### Tooling readiness

The later creation gate should prefer deterministic generated tiny fixtures or text fixtures. It must not execute ffprobe, FFmpeg, scanner logic, runtime metadata extraction, or broad media processing unless a separate gate explicitly authorizes that mechanism.

### Use readiness

After later creation, fixture use is limited to local QA, read-only single-file metadata chain development, visible report development over controlled fixture files, future scanner boundary tests limited to the fixture root, and safety/privacy validation.

### Non-use readiness

After later creation, the fixture pack still must not authorize customer material, production rushes, external client delivery, broad folder scanning, installation outside the controlled environment, SaaS upload, database ingestion, commercial claim of product readiness, pilot execution, or external support commitment.

## Creation gate requirements

The next creation gate must be separate and must include:

- exact file list;
- exact fixture root;
- exact manifest path;
- generation method;
- integrity calculation method;
- byte-size expectations;
- SHA256 expectations;
- cleanup and rollback rules;
- staged scope check;
- QA integrity tests;
- guard execution;
- non-authorization statement.

The next creation gate must not touch runtime, pyproject, SaaS, database, backend, frontend, installer, scanner, or metadata extraction implementation unless a future explicit phase changes that scope.

## Readiness outcome

The creation readiness outcome is:

`READY_FOR_SEPARATE_CONTROLLED_FIXTURE_PACK_CREATION_GATE_WITH_BOUNDARIES`

The next gate may prepare fixture creation, but it must remain narrow and controlled.

## Acceptance criteria for this readiness gate

This gate can close only if:

- the document identifies the phase and expected result token;
- the document references the contract gate and the plan gate;
- the document states that no fixtures are created;
- the document keeps the future fixture root explicit;
- the document keeps the future manifest explicit;
- the document names the planned fixture IDs;
- the document requires byte-size and SHA256 integrity;
- the document keeps customer and production material blocked;
- the document keeps ffprobe, FFmpeg, and scanner execution blocked;
- the document keeps runtime, pyproject, SaaS, database, backend, frontend, and installer changes blocked;
- the document declares the readiness outcome;
- the QA test passes;
- WSL/repo/secrets guard passes;
- PostgreSQL-only regression guard passes.

## Non-authorization statement

Closing this gate does not create fixtures. Closing this gate does not authorize read-only metadata extraction, ffprobe execution, FFmpeg execution, scanner execution, visible report generation over fixture files, external demo expansion, pilot execution, installation, SaaS integration, or customer material processing.

Closing this gate only authorizes preparing a later, separate, controlled fixture creation gate.

## Next expected gate

Recommended next phase:

`CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1`

Purpose of the next gate: create only the approved controlled non-customer fixture pack files and manifest, with integrity QA and no runtime expansion.
