# CID Local Media Agent — Controlled Local Demo Runner — Technical Next Implementation Readiness Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.TECHNICAL.NEXT.IMPLEMENTATION.READINESS.GATE.V1`
- Expected result: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_TECHNICAL_NEXT_IMPLEMENTATION_READINESS_GATE_V1_CLOSED`
- Scope type: documentation and QA test only.
- Product area: CID Local Media Agent.
- Current baseline before this gate: controlled local demo runner plus complete demo, external-demo, pilot-preparation, pilot-pack, and demo-to-pilot roadmap gates.

## Purpose

This gate decides the next safe technical implementation direction after the completed controlled demo and pilot preparation package. It does not implement that next direction. It only records readiness, ordering, constraints, blocked shortcuts, and the next smallest technical step that can move the product toward a real Local Media Agent without using customer material.

The intent is to prevent a jump from a controlled text-artifact demo directly into real customer usage. The product must move through a narrow technical bridge: controlled non-customer fixtures, read-only media inspection, explicit command safety, visible evidence, and privacy boundaries.

## Non-negotiable boundary

This gate does not authorize:

- real customer media;
- real production project folders;
- client installation;
- public demo;
- paid pilot;
- customer-facing promise;
- scanner over arbitrary folders;
- batch processing;
- transcription;
- synchronization;
- DaVinci Resolve, Avid, or NLE integration;
- SaaS or database access;
- backend, frontend, credits, billing, installer, or license activation work;
- modification of runtime code, package entrypoints, or pyproject configuration.

The current gate remains documentation-only. Any future implementation must have its own explicit gate, with its own narrow scope and validation.

## Current technical position

The current Local Media Agent line can already demonstrate:

1. an installed export command;
2. an installed controlled demo runner;
3. `--help` execution;
4. `--result-json` execution;
5. `--result-json --keep-output` execution;
6. deterministic artifact name, byte count, and SHA evidence;
7. automatic cleanup by default;
8. controlled cleanup for preserved temporary output;
9. no real media;
10. no external process execution;
11. no network;
12. no SaaS or database;
13. no write inside the repository;
14. no overwrite.

This is enough for a controlled technical conversation, but not enough for a real product pilot.

## Technical gap summary

The remaining technical gap between the current demo and a future pilot is not mainly commercial. It is implementation safety. The missing technical layers are:

- controlled non-customer media fixtures;
- fixture manifest with expected properties;
- read-only media metadata extraction;
- safe external command wrapper policy for media tooling;
- timeout and error redaction behavior;
- output boundary policy for generated reports;
- deterministic visible report over fixture evidence;
- minimal scanner behavior limited to fixture roots;
- operator-facing failure records;
- packaging and installation readiness after the read-only chain is stable;
- privacy and data-handling checks before any customer material is considered.

## Candidate next implementation blocks considered

### Option 1 — Controlled non-customer fixture pack

Create a small local fixture pack that is explicitly non-customer, non-confidential, deterministic, and safe to inspect. It should include a manifest, expected file names, expected hashes where appropriate, and a no-client-material statement.

Status: suitable as first technical step.

### Option 2 — Read-only single-file metadata extraction over fixture

Use the fixture pack to run a strictly read-only metadata extraction over one controlled fixture file. This must use a safe command policy, timeout, no shell interpolation, redacted errors, and no scanning of arbitrary folders.

Status: suitable after fixture pack readiness is closed.

### Option 3 — Visible report over controlled fixture metadata

Convert read-only fixture metadata into a visible operator report that can be compared with expected evidence. This is suitable only after the read-only extraction layer is stable.

Status: suitable after the read-only extraction layer.

### Option 4 — Minimal fixture-root scanner

Create a minimal scanner limited to a fixture-owned root, with explicit path boundaries and no customer folder traversal. This should not be the first implementation step, because scanner behavior multiplies risk.

Status: defer until fixture and single-file read-only extraction are stable.

### Option 5 — Packaging readiness

Prepare packaging after command behavior, fixture handling, and report evidence are stable. Packaging must not precede safe read-only behavior.

Status: defer.

### Option 6 — Pilot execution preparation

Use pilot templates only after the technical chain has enough safe behavior to justify controlled use. Pilot execution remains blocked.

Status: blocked.

## Decision

The next technical implementation direction should be:

`CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN`

This means the next implementation path should begin with a controlled fixture pack and then move to a read-only single-file metadata extraction chain. It must not jump directly to a scanner, batch processing, customer material, packaging, installer work, or pilot execution.

## Recommended immediate next gate

Recommended next phase:

`CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.READINESS.GATE.V1`

Recommended goal:

Create documentation and QA for a controlled, non-customer fixture pack that can be used later by a read-only metadata extraction implementation. The fixture pack gate should define fixture ownership, file selection rules, allowed formats, forbidden material, manifest schema, expected evidence, and cleanup policy.

The fixture pack gate may remain doc/test-only or may introduce fixture files only if explicitly approved by the phase scope. It must not use customer media.

## Implementation order after this gate

1. Controlled non-customer fixture pack readiness.
2. Controlled fixture manifest contract.
3. Read-only single-file metadata command wrapper readiness.
4. Read-only single-file metadata implementation over fixture.
5. Visible metadata report over fixture.
6. Minimal fixture-root scanner readiness.
7. Minimal fixture-root scanner implementation.
8. Packaging readiness.
9. External pilot readiness review.

This order is intentionally conservative.

## Required constraints for the next technical phase

The next phase must preserve these constraints:

- WSL Ubuntu execution only during development;
- canonical repository only;
- `.venv` activated;
- PostgreSQL-only project policy remains untouched;
- no `.env` changes;
- no database or SaaS access;
- no backend or frontend work;
- no pyproject or runtime command changes unless explicitly authorized;
- no real customer media;
- no broad folder traversal;
- no batch scanner;
- no network;
- no overwrite;
- no writes outside controlled output roots;
- no change to installer or licensing.

## Blocked shortcuts

The following shortcuts remain explicitly blocked:

- using a real shoot folder as the first test;
- demonstrating over customer assets;
- adding scanner traversal before single-file behavior is proven;
- adding transcription before metadata extraction is safe;
- adding synchronization before metadata extraction is safe;
- creating public marketing claims;
- quoting prices or pilot dates based on the current technical state;
- treating the current demo runner as a product release;
- treating a candidate as an approved pilot.

## Readiness checklist

This gate is ready to close only if:

- the next technical target is explicitly named;
- the target is smaller than a scanner;
- customer material remains blocked;
- runtime implementation remains blocked in this gate;
- pilot execution remains blocked;
- packaging remains deferred;
- fixture-first ordering is present;
- read-only single-file extraction is present as a later step;
- output boundaries remain controlled;
- QA confirms that this is documentation/test-only.

## Close result

If validated, this gate closes with:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_TECHNICAL_NEXT_IMPLEMENTATION_READINESS_GATE_V1_CLOSED`

The only authorized result is a technical-readiness decision. No implementation permission is granted by this gate.
