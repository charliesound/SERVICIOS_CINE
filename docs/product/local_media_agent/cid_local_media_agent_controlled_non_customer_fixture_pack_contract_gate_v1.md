# CID Local Media Agent — Controlled Non-Customer Fixture Pack Contract Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CONTRACT.GATE.V1`
- Expected result: `LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_CONTRACT_GATE_V1_CLOSED`
- Scope class: documentation and QA test only.
- Product line: CID Local Media Agent.
- Current technical baseline: controlled local demo runner is already installed, smokeable, narratable, externally framed, pilot-pack indexed, and roadmap-aligned.
- This gate opens the next technical preparation track, but does **not** implement it.

## Purpose

This gate defines the contract for a future controlled fixture pack that contains only non-customer, non-production, rights-safe media-like test assets.

The fixture pack will be used later to support a controlled metadata path, but this gate only defines the boundaries, naming, metadata obligations, safety rules, and future authorization sequence.

This gate exists so the next technical work cannot accidentally jump from the current controlled text-artifact demo to real customer files, uncontrolled folders, broad scanner execution, or external-media processing.

## Decision

The approved next technical direction is:

`CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN`

The order is mandatory:

1. Define fixture pack contract.
2. Create fixture pack in a later explicit gate.
3. Validate fixture pack integrity in a later explicit gate.
4. Authorize read-only single-file metadata over one controlled fixture in a later explicit gate.
5. Render visible report from controlled fixture metadata in a later explicit gate.
6. Only after that, consider a scanner limited to the fixture root.

## What this gate permits

This gate permits only:

- A written fixture pack contract.
- A QA test that verifies the contract text.
- Discussion of fixture rules, allowed asset categories, naming policy, expected checksums, size policy, provenance, rights status, storage location, and validation sequence.
- Future-gate placeholders for later implementation.

## What this gate does not permit

This gate does not permit:

- Creating media fixtures.
- Adding binary assets.
- Downloading sample media.
- Using customer footage.
- Using production footage.
- Using real rushes.
- Using copyrighted third-party test media.
- Executing media tooling.
- Executing a scanner.
- Reading real folders.
- Adding runtime code.
- Changing package entrypoints.
- Editing project configuration.
- Touching backend, frontend, SaaS, database, installer, billing, AI jobs, credits, ledger, Docker, migrations, or deployment files.
- Writing outside a future controlled fixture root.
- Treating this contract as pilot authorization.

## Fixture pack definition

A controlled non-customer fixture pack is a small set of deliberately created, rights-safe, non-production local assets designed only for repeatable technical validation.

The fixture pack must be:

- owned by the project;
- reproducible;
- small;
- deterministic where possible;
- documented;
- checksum-validated;
- isolated from customer material;
- isolated from production material;
- stored only under an explicitly approved future fixture path;
- never confused with a client delivery folder;
- never used as evidence of customer readiness.

## Allowed future fixture categories

A later gate may authorize one or more of these controlled fixture categories:

1. Tiny silent video fixture generated specifically for the project.
2. Tiny audio fixture generated specifically for the project.
3. Tiny sidecar text fixture containing synthetic metadata-like content.
4. Tiny folder structure fixture with neutral names.
5. Tiny malformed or edge-case fixture only if separately declared safe.

All future fixture content must be synthetic, project-owned, or explicitly generated under a controlled process.

## Forbidden future fixture categories

The future fixture pack must never include:

- footage from a client;
- material from a real production;
- rushes from a set;
- festival screeners;
- social media downloads;
- copyrighted clips;
- stock footage without explicit fixture rights review;
- private documents;
- personal data;
- sensitive audio recordings;
- cast, crew, location, or call-sheet data;
- real project names;
- credentials;
- database files;
- installer output;
- generated deliverables intended for distribution.

## Future fixture location policy

This gate does not create the path, but a later implementation gate must choose one approved path family.

The future path must be clearly marked as controlled and non-customer. It must not be inside a user download folder, desktop folder, client folder, production drive, mounted Windows media folder, or uncontrolled temporary folder.

The future fixture root must be treated as read-only by metadata stages unless a later fixture-creation gate explicitly writes it.

## Required future manifest

A later fixture creation gate must include a manifest with at least:

- fixture id;
- filename;
- relative path;
- media-like type;
- byte size;
- checksum;
- generation method;
- rights status;
- allowed use;
- forbidden use;
- expected metadata fields for later read-only tests;
- validation command or validation procedure;
- cleanup policy;
- owner;
- version.

## Required future checksum policy

Every future fixture must have a stable checksum recorded in the manifest.

Any later metadata gate must fail closed if:

- a fixture is missing;
- byte size changes unexpectedly;
- checksum changes unexpectedly;
- fixture path escapes the approved fixture root;
- a fixture resembles customer or production material;
- the manifest is missing;
- the fixture source is not documented.

## Required future metadata boundary

The first metadata gate after the fixture pack must be limited to one controlled fixture and must be read-only.

The metadata chain must not scan a full folder until a separate scanner gate exists.

The first read-only metadata gate must prove:

- single file only;
- controlled fixture only;
- no customer material;
- no production material;
- no network;
- no database;
- no SaaS;
- no overwrite;
- no writes outside approved output root;
- no broad directory traversal;
- no operator-selected arbitrary folder.

## Required future visible report boundary

A later visible report gate may consume controlled fixture metadata only after the fixture pack and single-file metadata gate are closed.

The report must disclose:

- fixture-only status;
- non-customer status;
- read-only metadata status;
- limitations;
- not product final;
- not pilot authorization;
- not customer evidence.

## Future scanner boundary

A scanner must remain blocked until all previous controlled fixture gates are closed.

The first scanner, if later authorized, must be limited to the approved fixture root and must not recurse outside the approved root.

No broad scan of user folders, production folders, mounted drives, desktop, downloads, or client storage is authorized by this gate.

## Commercial boundary

This fixture contract must not be used to tell a producer, school, post house, distributor, or client that the Local Media Agent can already process their material.

The correct language is:

> We have a controlled demo and a roadmap toward a safe pilot. The next technical step is a controlled non-customer fixture pack before any real material is considered.

## Operator boundary

An operator must not substitute personal footage, old rushes, sample clips from the internet, client files, or production material for the future fixture pack.

If the controlled fixture pack is missing, the operator must stop.

If the controlled fixture manifest is missing, the operator must stop.

If the checksum does not match, the operator must stop.

## Readiness checklist

This gate is ready to close only if:

- the contract names the phase and expected result;
- the contract chooses the controlled fixture-first technical path;
- the contract forbids customer and production material;
- the contract forbids fixture creation in this phase;
- the contract forbids media tooling execution in this phase;
- the contract forbids scanner execution in this phase;
- the contract defines allowed fixture categories;
- the contract defines forbidden fixture categories;
- the contract requires a future manifest;
- the contract requires future checksums;
- the contract preserves read-only single-file sequencing;
- the contract preserves fixture-root scanner sequencing;
- the contract blocks pilot authorization;
- the QA test verifies all of the above.

## Approved next gate after closure

If this gate closes successfully, the next recommended phase is:

`CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.PLAN.GATE.V1`

That next gate should still be documentation/test-only and should define the exact fixture names, planned sizes, planned checksums or checksum-generation approach, directory layout, and creation procedure.

It should still not create binary fixtures.

## Closure statement

This gate closes only as a contract and readiness gate.

Closure means the project has defined how a future controlled non-customer fixture pack must behave.

Closure does not mean fixtures exist.

Closure does not mean metadata extraction is authorized.

Closure does not mean media tooling is authorized.

Closure does not mean scanner execution is authorized.

Closure does not mean customer material is authorized.

Closure does not mean pilot execution is authorized.
