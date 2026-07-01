# CID Local Media Agent — Controlled Local Demo Runner — Controlled Pilot Candidate Gate V1

## Gate identity

- Gate name: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.CANDIDATE.GATE.V1`
- Expected result token: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_CANDIDATE_GATE_V1_CLOSED`
- Scope class: documentation and QA only.
- Product line: CID Local Media Agent.
- Baseline dependency: the controlled external demo follow-up decision gate must already be closed.

## Purpose

This gate defines how to classify an external contact as a **controlled pilot candidate** after a controlled technical demo, feedback capture, and follow-up decision.

The gate does **not** authorize a real pilot. It only establishes the internal criteria for saying: this contact may be considered for a future controlled pilot when the missing product, legal, operational, and technical conditions are ready.

## Non-authorization boundary

Closing this gate does not authorize a real pilot. Closing this gate also does not authorize any of the following:

- real client material processing;
- customer-side installation;
- public demo usage;
- production usage;
- scanner execution;
- media decoding execution;
- external process execution;
- network transfer;
- SaaS integration;
- persistence backend work;
- licensing activation;
- pricing commitment;
- service-level commitment;
- contractual promise;
- pilot start date;
- product-final claim.

The only permitted action is internal classification of a contact as one of the controlled pilot candidate categories defined below.

## Inputs required before classification

A contact can only be evaluated by this gate after the following evidence exists:

1. A controlled external demo was shown or explicitly declined with reason.
2. Feedback was captured using the feedback capture gate structure.
3. A follow-up decision was recorded using the follow-up decision gate structure.
4. The stakeholder profile is known.
5. The contact's actual operational pain is stated in their own words.
6. The expected value is tied to a concrete workflow, not generic interest in AI.
7. Any requested functionality that is not currently implemented is marked as future, unpromised, and blocked.
8. The contact understands that the current chain is a controlled technical demo, not a finished product.

## Candidate categories

### Category A — Strong future pilot candidate

A contact may be classified as `STRONG_FUTURE_PILOT_CANDIDATE` only when all of the following are true:

- They have a concrete workflow problem related to media review, metadata visibility, folder control, ingest preparation, or production/post coordination.
- They can name who would use the future tool and why.
- They understand the local-only positioning and the controlled demo boundary.
- They can provide structured feedback without demanding immediate production use.
- They have authority or access to the person who can approve a future pilot.
- They accept that real media processing is not authorized yet.
- They can participate in a future pilot with safe, pre-approved, non-sensitive test material when that phase is opened.
- They do not require unsupported platform, installer, SaaS, licensing, scanner, or media-analysis capabilities as a precondition for basic interest.

### Category B — Possible future pilot candidate

A contact may be classified as `POSSIBLE_FUTURE_PILOT_CANDIDATE` when there is real interest, but at least one major condition is still unclear:

- decision-maker access is unclear;
- operational pain is plausible but not quantified;
- the use case is valid but not urgent;
- the stakeholder needs a second demo with a colleague;
- the workflow is adjacent to the current Local Media Agent direction;
- the contact needs a clearer product roadmap before committing attention.

### Category C — Wait until real scanner capability

A contact should be classified as `WAIT_UNTIL_REAL_SCANNER_CAPABILITY` when their interest depends primarily on functionality that is not currently authorized or implemented, such as:

- scanning real folders with customer media;
- extracting real metadata through actual media tooling;
- parsing real shooting material;
- transcribing, syncing, generating subtitles, or preparing editorial outputs;
- customer-side batch processing;
- installer-based usage.

This is not a rejection. It means the contact may be valuable later, but showing more controlled runner evidence will not answer their core need.

### Category D — Commercial conversation only

A contact may be classified as `COMMERCIAL_CONVERSATION_ONLY` when they are interested in business model, pricing, procurement, deployment, or organizational fit, but not ready to evaluate a technical pilot.

Allowed next step: non-binding commercial discovery.

Forbidden next step: offer price, contract terms, delivery timeline, or pilot start without a separate commercial authorization gate.

### Category E — Not a fit now

A contact should be classified as `NOT_A_FIT_NOW` when one or more of the following apply:

- They want a finished production product immediately.
- They need capabilities outside the CID Local Media Agent direction.
- They require handling sensitive real material before the project has approved safeguards.
- They cannot identify an operational workflow where the product would help.
- They evaluate only generic AI novelty, not production value.
- They request claims, timelines, or guarantees that should not be made.

## Mandatory classification fields

Each internal pilot candidate record must include:

- contact role category;
- organization type;
- demo date or feedback reference;
- stated operational pain;
- requested workflow;
- current demo element that resonated;
- missing capability that blocks pilot readiness;
- candidate category;
- confidence level: low, medium, or high;
- next safe action;
- forbidden action;
- expectation risk level;
- decision owner;
- review date.

## Candidate scoring rubric

Use this scoring model only as internal guidance. It is not a sales qualification score.

| Dimension | 0 | 1 | 2 |
|---|---:|---:|---:|
| Operational pain clarity | vague | plausible | concrete |
| Workflow fit | unclear | adjacent | direct |
| Decision access | none | indirect | direct |
| Boundary acceptance | weak | partial | clear |
| Feedback quality | generic | useful | actionable |
| Pilot safety | risky | manageable | safe later |
| Urgency | none | moderate | strong |

Interpretation:

- `0-5`: not a fit now or wait.
- `6-9`: possible future pilot candidate.
- `10-14`: strong future pilot candidate, pending separate pilot authorization.

## Safe next actions by category

| Category | Safe next action | Forbidden action |
|---|---|---|
| Strong future pilot candidate | add to controlled pilot candidate backlog | start pilot |
| Possible future pilot candidate | schedule second discovery or second controlled demo | promise roadmap item |
| Wait until real scanner capability | record blocker and revisit after scanner readiness | process real folders |
| Commercial conversation only | hold non-binding commercial discovery | offer price or contract |
| Not a fit now | close with polite explanation | keep pushing demo |

## Red flags

A contact must not be advanced toward pilot candidacy when any of these red flags are present:

- They insist on using confidential client material immediately.
- They ask for a public reference before a product exists.
- They want the demo positioned as production-ready.
- They want unsupported media processing claims.
- They require immediate integration with external systems.
- They want the tool installed on uncontrolled devices.
- They focus on speculative AI features unrelated to the current product line.
- They do not accept the controlled demo boundary.

## Positive signals

A contact may be promising when they say things like:

- “This would help us understand what is inside chaotic folders before post starts.”
- “Our production teams lose time asking what material exists and whether it is usable.”
- “I would want my post supervisor or production coordinator to see this.”
- “I understand this is not processing our real material yet, but the direction is useful.”
- “Can we define what a safe pilot would look like later?”

These are signals, not commitments.

## Minimum pilot-candidate note template

```text
CONTACT_ROLE_CATEGORY:
ORGANIZATION_TYPE:
DEMO_OR_FEEDBACK_REFERENCE:
STATED_OPERATIONAL_PAIN:
REQUESTED_WORKFLOW:
DEMO_ELEMENT_THAT_RESONATED:
MISSING_CAPABILITY_BLOCKING_REAL_PILOT:
CANDIDATE_CATEGORY:
CONFIDENCE_LEVEL:
EXPECTATION_RISK_LEVEL:
NEXT_SAFE_ACTION:
FORBIDDEN_ACTION:
DECISION_OWNER:
REVIEW_DATE:
```

## Operator language

Recommended wording:

> “I am not marking this as a pilot yet. I am marking it as a possible pilot candidate for a later controlled phase, provided the missing safeguards and product capabilities are approved.”

Avoid:

> “We can start a pilot with your material.”

Avoid:

> “This is ready for your production.”

Avoid:

> “We can install this for your team now.”

## Decision examples

### Example 1 — Productora with multiple active productions

- Pain: fragmented folder review and lack of early visibility.
- Interest: executive overview before post handoff.
- Category: `STRONG_FUTURE_PILOT_CANDIDATE` if they accept controlled boundaries.
- Safe next action: record candidate and prepare future pilot scope once real scanner readiness is authorized.
- Forbidden action: promise multi-production dashboard or customer material processing.

### Example 2 — Escuela de cine

- Pain: students deliver disorganized media and need discipline around folder evidence.
- Interest: teaching controlled workflow habits.
- Category: `POSSIBLE_FUTURE_PILOT_CANDIDATE` or `COMMERCIAL_CONVERSATION_ONLY` depending on decision access.
- Safe next action: second demo for coordinator or program director.
- Forbidden action: claim classroom deployment readiness.

### Example 3 — Postproduction supervisor

- Pain: wants actual media metadata and batch scanning.
- Interest: high, but blocked by missing real scanner capability.
- Category: `WAIT_UNTIL_REAL_SCANNER_CAPABILITY`.
- Safe next action: revisit when scanner readiness gate exists.
- Forbidden action: process real folder sample now.

### Example 4 — Generic AI-curious contact

- Pain: not concrete.
- Interest: novelty.
- Category: `NOT_A_FIT_NOW`.
- Safe next action: close politely or keep in low-priority updates.
- Forbidden action: spend technical discovery time without workflow evidence.

## Closure criteria

This gate may be closed only if the documentation and QA test verify that:

- pilot candidacy is classification only;
- real pilot start remains blocked;
- real customer material remains blocked;
- installation remains blocked;
- unsupported media processing remains blocked;
- candidate categories are explicit;
- scoring is internal and non-binding;
- safe next actions and forbidden actions are paired;
- red flags and positive signals are documented;
- a minimum candidate note template exists;
- the expected closure result token is present.

## Final closure token

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_CANDIDATE_GATE_V1_CLOSED`
