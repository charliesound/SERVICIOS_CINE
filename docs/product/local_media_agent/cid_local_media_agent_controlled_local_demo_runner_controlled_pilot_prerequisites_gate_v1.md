# CID Local Media Agent — Controlled Pilot Prerequisites Gate V1

## Gate identity

- Gate name: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.PREREQUISITES.GATE.V1`
- Expected close result: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_PREREQUISITES_GATE_V1_CLOSED`
- Scope: documentation and QA test only.
- Product line: CID Local Media Agent.
- Baseline before this gate: the controlled pilot boundary gate is closed.

## Purpose

This gate defines the minimum prerequisites that must exist before CID Local Media Agent may move from a controlled external demo / pilot candidate conversation into any future real pilot planning conversation.

This gate does not authorize a real pilot. It only freezes the conditions that must be satisfied before a later gate can even consider a real pilot.

## Current authorized state

The authorized state remains:

- controlled local technical demo only;
- fixture-owned temporary output only;
- single controlled text artifact only;
- installed command smoke only;
- operator-controlled explanation only;
- external feedback and follow-up decision process only;
- pilot candidate classification only;
- pilot boundary definition only.

## Explicit non-authorizations

This gate does not authorize:

- real client media;
- production media;
- personal data processing;
- confidential project files;
- external installation;
- client workstation installation;
- remote client execution;
- scanner execution;
- FFmpeg execution;
- ffprobe execution;
- transcription;
- synchronization;
- media indexing;
- SaaS connection;
- database access;
- payment, pricing, commercial contract, or subscription;
- support SLA;
- public demo;
- pilot start;
- pilot success claim;
- product readiness claim.

## Prerequisite categories

A future real pilot may only be considered after every category below has an owner, evidence, and an explicit pass/fail decision.

### 1. Human consent and authorization

Required before any future real pilot:

- written authorization from the client-side decision maker;
- named internal CID owner;
- named client owner;
- named technical contact;
- confirmation that the client understands this is not a final product;
- confirmation that the client understands pilot scope can be stopped;
- confirmation that no uncontrolled media is accepted.

Blocked until later gate:

- verbal-only approval;
- informal transfer of media;
- open-ended evaluation;
- uncontrolled folder access;
- access to full project drives.

### 2. Scope definition

A future pilot scope must define:

- exact use case;
- exact allowed inputs;
- exact disallowed inputs;
- exact expected output;
- maximum duration;
- maximum number of files;
- maximum number of operators;
- environment owner;
- demo/pilot distinction;
- stop conditions;
- rollback/cleanup procedure.

The scope must avoid phrases implying unlimited automation, finished product, production reliability, or client-ready deployment.

### 3. Data and media boundaries

Before any future real media pilot, the following must be defined:

- whether media is synthetic, public test media, client-provided non-sensitive media, or production material;
- whether any personal data may appear;
- whether any minors, performers, crew, locations, contracts, unreleased scenes, or sound reports are present;
- whether media contains confidential creative material;
- whether the client has rights to provide the material;
- whether the material can be copied, processed, stored, deleted, or retained;
- whether any output may be shown back to the client;
- whether any output may be used as evidence after the pilot.

Until a later explicit data-handling gate exists, real client material remains blocked.

### 4. Technical readiness prerequisites

A future pilot cannot start unless later gates establish:

- real scanner readiness;
- real media preflight readiness;
- FFmpeg/ffprobe execution policy;
- timeout policy;
- failure-mode policy;
- output boundary policy;
- cleanup policy;
- logging and redaction policy;
- no-overwrite guarantees;
- environment compatibility policy;
- reproducible operator command sequence;
- QA coverage for every enabled path.

The current controlled runner does not satisfy these prerequisites by itself because it is a controlled demo runner, not a real pilot execution system.

### 5. Legal and confidentiality prerequisites

A future pilot requires a later explicit legal/confidentiality gate covering:

- NDA or written confidentiality terms;
- client consent for test processing;
- retention/deletion policy;
- permitted evidence collection;
- limits of liability;
- ownership of outputs;
- use of screenshots or reports;
- handling of unpublished creative material;
- client approval before any external mention.

This gate does not create legal approval. It only requires that such approval exist before a future pilot.

### 6. Success criteria

A future pilot must define success criteria before it starts. Examples:

- operator can run a bounded workflow without intervention;
- output is created inside a controlled output root;
- no overwrite occurs;
- cleanup works;
- report is understandable to the client;
- error states are actionable;
- processing time is within agreed tolerance;
- client confirms the workflow addresses a real operational pain.

Success criteria must be measurable and must not be framed as product-market fit, production readiness, or final delivery readiness.

### 7. Support and rollback prerequisites

A future pilot requires:

- named support owner;
- defined response window;
- pilot stop procedure;
- cleanup procedure;
- artifact removal procedure;
- rollback path;
- incident note template;
- client communication line;
- explicit statement that unsupported issues stop the pilot rather than expanding scope.

No support obligation is created by this gate.

### 8. Commercial boundaries

Before any future pilot, the commercial position must be clear:

- pilot candidate does not equal paid customer;
- pilot discussion does not equal contract;
- pilot feedback does not equal product commitment;
- pricing remains separate;
- subscription remains separate;
- licensing remains separate;
- installation rights remain separate;
- roadmap promises remain blocked.

## Minimum evidence pack for later pilot consideration

A future gate may consider pilot opening only if the following evidence exists:

- candidate classification record;
- stakeholder brief record;
- external demo readiness record;
- feedback capture record;
- follow-up decision record;
- pilot candidate gate pass;
- pilot boundary gate pass;
- this prerequisites gate pass;
- written client-side intent to evaluate a future controlled pilot;
- explicit list of missing technical gates.

## Decision statuses

A contact may be classified as one of the following:

- `PILOT_PREREQUISITES_NOT_READY` — the default state.
- `PILOT_PREREQUISITES_PARTIAL` — some prerequisites are known, but missing items remain.
- `PILOT_PREREQUISITES_READY_FOR_PLANNING_GATE` — prerequisites are sufficiently defined to prepare a later pilot planning gate.
- `PILOT_BLOCKED_BY_DATA_RISK` — media or confidentiality risk is too high.
- `PILOT_BLOCKED_BY_TECHNICAL_READINESS` — required real execution paths do not exist.
- `PILOT_BLOCKED_BY_COMMERCIAL_AMBIGUITY` — expectations are unclear or overextended.

Only `PILOT_PREREQUISITES_READY_FOR_PLANNING_GATE` allows preparation of a later pilot planning gate. It still does not authorize a real pilot.

## Required operator language

Acceptable operator language:

> This is a prerequisite review for a possible future controlled pilot. It does not authorize client media, installation, real processing, pricing, or product commitment.

> Before we discuss a pilot, we need to know exactly what material, environment, owner, scope, success criteria, and stop conditions would apply.

> If the prerequisites are unclear, the correct decision is to pause, not to expand the demo.

Forbidden operator language:

- We can start the pilot now.
- Send me your production media.
- Install it on your machine.
- This is ready for client work.
- This will process your whole project.
- Pricing is already fixed.
- This is the final product.
- We can support whatever happens.

## Stop conditions

The operator must stop pilot discussion when:

- the client wants to send real media immediately;
- the client requests installation;
- confidentiality terms are absent;
- ownership of material is unclear;
- data handling is unclear;
- success criteria are vague;
- expected workflow requires scanner, FFmpeg, ffprobe, transcription, synchronization, or SaaS features that are not authorized in the current line;
- the conversation becomes a price/contract negotiation without a commercial gate;
- the client expects production reliability.

## Relationship to prior gates

This gate depends on:

- operator evidence pack gate;
- demo narrative gate;
- operator runbook gate;
- failure modes recovery gate;
- demo acceptance checklist gate;
- stakeholder demo brief gate;
- controlled external demo readiness gate;
- external demo feedback capture gate;
- external demo follow-up decision gate;
- controlled pilot candidate gate;
- controlled pilot boundary gate.

This gate does not replace any of them.

## QA expectations

The QA test for this gate must verify:

- the phase/result identifiers are present;
- the gate is doc/test-only;
- real pilot remains blocked;
- real media remains blocked;
- external installation remains blocked;
- legal/confidentiality prerequisites are required;
- technical prerequisites are required;
- success criteria are required;
- support and rollback prerequisites are required;
- commercial boundaries are preserved;
- explicit decision statuses exist;
- prior gate dependencies are listed.

## Closure statement

When this gate closes, the only authorized result is:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_PREREQUISITES_GATE_V1_CLOSED`

Closing this gate means that CID Local Media Agent has a controlled checklist of prerequisites for any future pilot planning discussion. It does not authorize a real pilot, real media, installation, support, pricing, contract, or production usage.
