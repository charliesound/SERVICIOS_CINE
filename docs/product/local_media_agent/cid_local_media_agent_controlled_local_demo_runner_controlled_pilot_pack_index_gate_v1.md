# CID Local Media Agent — Controlled Local Demo Runner — Controlled Pilot Pack Index Gate V1

## Gate identity

- Gate name: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.PACK.INDEX.GATE.V1`
- Result token: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_PACK_INDEX_GATE_V1_CLOSED`
- Product area: CID Local Media Agent
- Gate type: documentation and QA only
- Intended use: internal pilot preparation index
- External status: not public, not client-facing, not a real pilot authorization

## Purpose

This gate creates the internal index for the controlled pilot preparation pack. It connects the pilot scope template, risk register template, evidence plan template, and exit criteria template into a single operational sequence.

The purpose is to prevent the team from treating individual templates as standalone authorization. The templates are preparation assets only. They do not authorize a real pilot, client material, external installation, client processing, product pricing, or commercial commitment.

## Current baseline expected before this gate

The pilot preparation chain must already include:

1. Controlled pilot candidate gate.
2. Controlled pilot boundary gate.
3. Controlled pilot prerequisites gate.
4. Controlled pilot scope template gate.
5. Controlled pilot risk register template gate.
6. Controlled pilot evidence plan template gate.
7. Controlled pilot exit criteria template gate.

This gate does not replace those documents. It indexes them and defines their usage order.

## Strict scope

This gate is documentation and QA only.

Allowed:

- Add this index document.
- Add its QA test.
- Reference previously closed controlled pilot preparation templates.
- Define an operator-facing sequence.
- Define blocked transitions.
- Define minimum evidence required before any future pilot authorization gate.

Forbidden:

- No runtime implementation.
- No command implementation.
- No packaging implementation.
- No pyproject change.
- No scanner execution.
- No ffprobe execution.
- No FFmpeg execution.
- No real media access.
- No client material.
- No external installation.
- No SaaS access.
- No database access.
- No backend change.
- No frontend change.
- No pricing commitment.
- No contract commitment.
- No support commitment.
- No real pilot authorization.

## Pack contents indexed by this gate

### 1. Pilot prerequisites template

Purpose: determine whether a future pilot can even be considered.

It should answer:

- Is there an identified responsible person on the client side?
- Is there explicit internal permission to discuss a pilot?
- Are allowed and forbidden data categories clear?
- Are operating limits understood?
- Are support limits understood?
- Are confidentiality and rollback expectations defined?

Output status:

- `READY_FOR_SCOPE_DRAFT`
- `BLOCKED_PENDING_PREREQUISITES`
- `NOT_A_PILOT_CANDIDATE`

### 2. Pilot scope template

Purpose: define the controlled shape of a future pilot without using client material yet.

It should answer:

- What operational problem is being tested?
- What workflow is in scope?
- What workflow is out of scope?
- What input types would be allowed later?
- What input types remain forbidden?
- What duration is proposed?
- What would count as operational value?

Output status:

- `SCOPE_DRAFT_READY_FOR_RISK_REVIEW`
- `SCOPE_TOO_BROAD`
- `SCOPE_NOT_VALIDATED`

### 3. Pilot risk register template

Purpose: identify and classify pilot risks before any future authorization.

It should answer:

- What could expose client material improperly?
- What could create false expectations?
- What could require support beyond current capacity?
- What could create legal or confidentiality issues?
- What technical readiness gaps still exist?
- What operator errors could invalidate evidence?
- What should stop the pilot before it starts?

Output status:

- `RISK_REGISTER_READY_FOR_EVIDENCE_PLAN`
- `BLOCKED_BY_HIGH_RISK`
- `REQUIRES_SCOPE_REDUCTION`

### 4. Pilot evidence plan template

Purpose: define what evidence a future pilot would collect and how it would be validated.

It should answer:

- What evidence demonstrates value?
- What evidence demonstrates safety?
- What evidence demonstrates operator repeatability?
- What is deliberately not captured?
- What must be anonymized or redacted?
- Who validates evidence?
- What evidence is insufficient?

Output status:

- `EVIDENCE_PLAN_READY_FOR_EXIT_CRITERIA`
- `EVIDENCE_PLAN_INCOMPLETE`
- `EVIDENCE_PLAN_NOT_SAFE`

### 5. Pilot exit criteria template

Purpose: define how a future pilot would end and what decision follows.

It should answer:

- What counts as success?
- What counts as success with reservations?
- What counts as inconclusive?
- What triggers stop by risk?
- What indicates no commercial fit?
- What indicates pending technical development?
- What decision is allowed after the pilot?

Output status:

- `EXIT_CRITERIA_READY_FOR_PILOT_AUTHORIZATION_REVIEW`
- `EXIT_CRITERIA_INCOMPLETE`
- `EXIT_CRITERIA_TOO_VAGUE`

## Required usage order

The pilot preparation pack must be used in this order:

1. Prerequisites.
2. Scope.
3. Risk register.
4. Evidence plan.
5. Exit criteria.
6. Pilot authorization review gate, not included in this gate.

The order must not be reversed. Exit criteria cannot be written before evidence is defined. Evidence cannot be defined before risks are understood. Risks cannot be assessed before scope exists. Scope cannot be drafted until prerequisites are checked.

## Dependency map

```text
Prerequisites
  -> Scope
      -> Risk Register
          -> Evidence Plan
              -> Exit Criteria
                  -> Future Pilot Authorization Review Gate
```

The final node is intentionally not authorized by this gate.

## Decision states for the pack

The whole pilot preparation pack may only have one of these states:

- `PACK_NOT_STARTED`
- `PACK_INCOMPLETE`
- `PACK_BLOCKED_BY_PREREQUISITES`
- `PACK_BLOCKED_BY_SCOPE`
- `PACK_BLOCKED_BY_RISK`
- `PACK_BLOCKED_BY_EVIDENCE_PLAN`
- `PACK_BLOCKED_BY_EXIT_CRITERIA`
- `PACK_READY_FOR_FUTURE_AUTHORIZATION_REVIEW`

The pack must never produce:

- `PILOT_AUTHORIZED`
- `CLIENT_MATERIAL_ALLOWED`
- `EXTERNAL_INSTALLATION_ALLOWED`
- `REAL_PROCESSING_ALLOWED`
- `COMMERCIAL_OFFER_APPROVED`

## Minimum completeness checklist

Before the pack can be marked `PACK_READY_FOR_FUTURE_AUTHORIZATION_REVIEW`, all of the following must be true:

- Prerequisites are completed.
- Scope is narrow and explicit.
- Forbidden material is listed.
- Risk register has no unresolved high-risk blocker.
- Evidence plan defines what will and will not be captured.
- Exit criteria define success, reservation, inconclusive, stop, no-fit, and pending-technical outcomes.
- Client-facing language remains conservative.
- No real media is accepted.
- No external installation is authorized.
- No production workflow is promised.
- No price is committed.
- No legal agreement is implied.
- No support obligation is created.

## Required operator language

When using this pack internally, the operator must say:

> This is a preparation index for a possible future controlled pilot. It does not authorize a real pilot, client material, installation, processing, price, support, or product commitment.

The operator must not say:

- The pilot is approved.
- We can start with your media.
- We can install it at your site.
- We can process your production material.
- This is ready for paid deployment.
- Support is included.
- The current technical demo already covers real scanner behavior.

## Blocked transitions

The following transitions are blocked by this gate:

- Demo feedback directly to real pilot.
- Pilot candidate directly to client material.
- Scope template directly to installation.
- Risk register directly to client processing.
- Evidence plan directly to commercial claim.
- Exit criteria directly to sales commitment.
- Pack index directly to real pilot authorization.

## Future gate required before real pilot

A future pilot authorization review gate is required before any of the following:

- Accepting real client material.
- Running against real media.
- Installing on an external client machine.
- Providing client support.
- Defining pilot dates.
- Defining pricing.
- Signing any commitment.
- Treating outputs as production evidence.

That future gate is outside this phase.

## QA expectations

The QA test for this gate must confirm:

- The gate identity is present.
- The result token is present.
- The document is documentation and QA only.
- The five pilot pack templates are indexed.
- The required usage order is present.
- The dependency map is present.
- The decision states are present.
- Blocked transitions are explicit.
- Future pilot authorization remains required.
- Real pilot, client material, external installation, processing, pricing, support, runtime, scanner, ffprobe, FFmpeg, SaaS, database, backend, and frontend remain blocked.
- The document does not authorize a real pilot.

## Closure statement

If this gate is closed, the controlled pilot preparation pack has an internal index and usage order. The project gains a safer way to move from commercial interest to structured pilot preparation without authorizing a real pilot.

Closure does not authorize real client work.

Expected closure result:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_PACK_INDEX_GATE_V1_CLOSED`
