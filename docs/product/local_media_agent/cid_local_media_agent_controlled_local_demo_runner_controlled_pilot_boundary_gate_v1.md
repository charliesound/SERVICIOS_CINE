# CID Local Media Agent — Controlled Pilot Boundary Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.BOUNDARY.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_BOUNDARY_GATE_V1_CLOSED`

## Purpose

This gate defines the controlled boundary between a contact being a **pilot candidate** and a real pilot being authorized.

The previous gate can classify a stakeholder as a future pilot candidate. This gate prevents that classification from being interpreted as approval to process real material, install on an external machine, promise production use, offer support, quote final pricing, or start a client-facing pilot.

The boundary is intentionally conservative. A real pilot requires additional explicit gates for legal, data, technical, support, success criteria, operator readiness, installation, and rollback decisions.

## Current authorized state

The current authorized state remains a controlled technical demo only.

Allowed at this stage:

- use the installed controlled local demo runner;
- show the controlled demo narrative;
- use the operator runbook;
- use failure and recovery guidance;
- use the demo acceptance checklist;
- use stakeholder brief guidance;
- show a controlled external demo only when the readiness gate passes;
- capture external demo feedback;
- make a follow-up decision;
- classify a contact as a future pilot candidate.

Not authorized at this stage:

- real pilot execution;
- client material intake;
- processing of real media;
- external installation;
- client workstation setup;
- scanner execution;
- media folder scanning;
- ffprobe execution over real media;
- FFmpeg execution over real media;
- SaaS integration;
- database usage;
- installer distribution;
- production support;
- client SLA;
- commercial pricing commitment;
- binding delivery date;
- promise of final product behavior.

## Boundary principle

A candidate can be interesting without being ready for a pilot.

The transition from candidate to pilot must require explicit approval across four dimensions:

1. **Business fit** — the contact has a real operational problem and a credible reason to test.
2. **Technical fit** — the future pilot scope can be implemented without unsafe shortcuts.
3. **Data and legal fit** — real material, privacy, confidentiality, ownership, and handling rules are defined.
4. **Operational fit** — support, rollback, demo expectations, and success criteria are realistic.

If any dimension is unresolved, the contact remains a candidate, not a pilot.

## Pilot boundary states

### State A — Demo-only contact

The person has seen or can see the controlled demo.

Allowed next steps:

- show controlled demo;
- capture feedback;
- classify interest;
- schedule another conversation;
- explain future roadmap boundaries.

Blocked:

- pilot planning;
- material collection;
- installation;
- operational commitment.

### State B — Candidate contact

The person has a plausible use case and meaningful interest.

Allowed next steps:

- document the pain point;
- identify potential pilot scenario;
- ask about workflow constraints;
- ask what success would look like;
- ask what kind of material could be used later;
- ask who must approve a future pilot.

Blocked:

- accepting material;
- processing files;
- promising a date;
- quoting final price;
- starting client setup;
- giving production instructions.

### State C — Candidate with unresolved blockers

The contact has interest, but one or more blocking areas remain open.

Typical blockers:

- unclear decision maker;
- no defined workflow pain;
- no safe material policy;
- unrealistic expectation of finished product;
- need for real scanner before any value can be validated;
- need for cross-platform installer before testing;
- expectation of immediate production use;
- legal or confidentiality requirements not defined;
- support expectations too high for current stage.

Allowed next steps:

- keep the contact warm;
- send a conservative summary;
- list unresolved blockers;
- defer pilot conversation;
- request clarification later.

Blocked:

- scheduling pilot execution;
- collecting files;
- changing product scope to satisfy one prospect without gate approval.

### State D — Pilot-ready candidate pending future authorization

The contact may become pilot-ready, but only after additional gates are closed.

Minimum future gates required before real pilot authorization:

- pilot scope gate;
- real material intake policy gate;
- privacy and confidentiality gate;
- technical execution readiness gate;
- support and rollback gate;
- success criteria gate;
- pilot approval record gate.

Until those gates exist and pass, this state is still not a pilot.

### State E — Real pilot authorized

This state is explicitly out of scope for the current phase.

A real pilot may only be authorized by a later phase that states exactly what is allowed, what material may be used, where it may run, what evidence is collected, how the output is cleaned up, and who approved it.

## Required evidence before moving beyond candidate

A contact cannot move toward pilot readiness unless the following evidence exists:

- named organization or stakeholder type;
- role of the person in the production/post/delivery chain;
- operational pain point in their own words;
- why the current controlled demo is relevant to that pain;
- what part of the future product they want to validate;
- who owns approval for a pilot;
- whether real material would be allowed later;
- whether confidentiality constraints exist;
- what environment would be used later;
- what success would mean;
- what failure would mean;
- whether expectations are aligned with current limitations.

## Minimum hard blockers

The following conditions block pilot authorization:

- the contact expects a final product;
- the contact expects production reliability now;
- the contact wants immediate processing of real media;
- the contact wants installation on their machine now;
- the contact requires cloud or SaaS integration now;
- the contact requires real scanner behavior now;
- the contact requires automatic sync/transcription/subtitle features now;
- no one can define success criteria;
- no one can define who approves material use;
- no one accepts that the current demo is controlled and limited;
- the requested scope requires touching forbidden areas.

## Commercial boundary

The operator may say:

> This contact is a possible candidate for a future controlled pilot, but we are not authorizing a pilot yet.

The operator must not say:

> We can start a real pilot now.

The operator may say:

> Before a pilot, we need to define scope, data handling, success criteria, support expectations, and technical readiness.

The operator must not say:

> Send me your material and I will test it.

The operator may say:

> The current demo proves a controlled internal chain, not final product behavior.

The operator must not say:

> This is ready for production use.

## Technical boundary

The current controlled demo chain proves:

- installed command availability;
- controlled runner invocation;
- deterministic controlled artifact;
- stable artifact name;
- stable artifact byte count;
- stable artifact digest;
- default cleanup;
- preserve-and-clean workflow;
- negative path fail-closed behavior;
- controlled JSON evidence;
- no real media access;
- no scanner execution;
- no external media processing.

The current chain does not prove:

- real folder scanning;
- real metadata extraction;
- real ffprobe integration over client media;
- FFmpeg processing;
- waveform sync;
- timecode sync;
- transcription;
- translation;
- subtitle generation;
- DaVinci integration;
- Avid integration;
- installer readiness;
- external machine compatibility;
- licensing readiness;
- support readiness;
- legal readiness.

## Data boundary

No real client file should be accepted at this stage.

If a prospect offers real material, the operator response is:

> Not yet. We first need a separate controlled pilot intake policy that defines what material can be used, where it can live, who approves it, how it is cleaned up, and what evidence is retained.

Allowed discussion topics:

- types of media they usually have;
- approximate workflow pain;
- typical folder complexity;
- metadata problems;
- production/post handoff issues;
- confidentiality concerns;
- what they would want to validate later.

Blocked actions:

- copying material;
- downloading material;
- opening client files;
- running commands over client files;
- generating client output;
- storing client names, titles, or sensitive details in repository files.

## Legal and confidentiality boundary

A future pilot may require:

- written authorization;
- confidentiality terms;
- scope definition;
- material handling rules;
- retention/deletion policy;
- limitation of liability;
- non-production disclaimer;
- evidence handling policy;
- named contact responsible for approval.

This gate does not create any legal template. It only states that legal and confidentiality readiness must be resolved before pilot authorization.

## Support boundary

A future pilot must define:

- who operates the tool;
- who observes the test;
- who receives outputs;
- what happens if the tool fails;
- whether the test may be repeated;
- what support channel exists;
- how long support lasts;
- what is explicitly not supported.

Until this exists, there is no pilot support commitment.

## Success criteria boundary

A future pilot must define measurable criteria before execution.

Possible future criteria:

- a controlled folder can be scanned;
- expected metadata can be surfaced;
- a useful report can be generated;
- the operator can explain the output;
- the prospect can judge value;
- no material leaves the allowed environment;
- cleanup is verified;
- failure paths are understood.

This gate does not approve those criteria. It only states that they must exist before pilot authorization.

## Candidate decision record

For each candidate, capture:

- contact category;
- role;
- stated pain;
- proposed future pilot value;
- blockers;
- required future gates;
- decision owner;
- next safe action;
- no-go reason if rejected;
- date of classification;
- operator who classified it.

Allowed classifications:

- `DEMO_ONLY_CONTACT`
- `PILOT_CANDIDATE_EARLY`
- `PILOT_CANDIDATE_BLOCKED`
- `PILOT_CANDIDATE_READY_FOR_SCOPE_DISCUSSION`
- `NOT_A_PILOT_CANDIDATE`

Blocked classifications:

- `PILOT_APPROVED`
- `REAL_MEDIA_APPROVED`
- `INSTALLATION_APPROVED`
- `PRODUCTION_USE_APPROVED`
- `CLIENT_PROCESSING_APPROVED`

## Stop conditions

Stop the pilot conversation immediately if:

- the prospect asks to send material now;
- the prospect asks for production use;
- the prospect asks for final pricing based on the demo;
- the prospect expects automatic scanner/transcription/sync/subtitle behavior now;
- the prospect cannot accept the controlled limitation;
- the prospect wants installation before readiness gates;
- the operator is tempted to promise future capability as already working.

Recommended stop wording:

> I want to keep this accurate. The current chain is a controlled technical demo. I can record your pilot interest, but I cannot accept material or start a real pilot until the pilot boundary, intake, support, and approval gates are explicitly closed.

## Required assertions for QA

The QA for this gate must verify that:

- the phase identifier exists;
- the closure result exists;
- candidate and pilot are clearly separated;
- real pilot is not authorized;
- real material intake is blocked;
- external installation is blocked;
- production use is blocked;
- final pricing commitment is blocked;
- required future gates are named;
- allowed and blocked classifications are defined;
- stop conditions are present;
- no implementation, runtime, scanner, media processing, SaaS, database, installer, backend, or frontend scope is introduced.

## Scope lock

This phase is documentation and QA only.

It must not modify:

- runtime code;
- package entrypoints;
- command behavior;
- scanner behavior;
- media processing;
- ffprobe behavior;
- FFmpeg behavior;
- SaaS code;
- database code;
- installer code;
- backend code;
- frontend code;
- pyproject configuration.

## Closure statement

If the documentation and QA pass, this phase may close with:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_BOUNDARY_GATE_V1_CLOSED`
