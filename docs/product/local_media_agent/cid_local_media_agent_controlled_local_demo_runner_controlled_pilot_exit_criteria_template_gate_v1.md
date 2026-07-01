# CID Local Media Agent — Controlled Pilot Exit Criteria Template Gate V1

Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.EXIT.CRITERIA.TEMPLATE.GATE.V1`

Expected closure result:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_EXIT_CRITERIA_TEMPLATE_GATE_V1_CLOSED`

## Purpose

This document defines a controlled, reusable exit criteria template for a future CID Local Media Agent pilot.

It does not authorize a real pilot.

It does **not** authorize a real pilot. It does not authorize external installation, customer media, real production material, customer processing, support commitments, pricing, legal commitment, or product-final promises.

The purpose is to make sure that, once a pilot is eventually authorized by later gates, the team already knows how the pilot may end and how each outcome must be interpreted.

## Relationship to previous gates

This gate sits after the controlled pilot evidence plan template.

The intended controlled chain is:

1. Controlled local demo runner exists.
2. Operator evidence exists.
3. Demo narrative exists.
4. Operator runbook exists.
5. Failure modes and recovery exist.
6. Demo acceptance checklist exists.
7. Stakeholder demo brief exists.
8. Controlled external demo readiness exists.
9. External demo feedback capture exists.
10. External demo follow-up decision exists.
11. Controlled pilot candidate gate exists.
12. Controlled pilot boundary gate exists.
13. Controlled pilot prerequisites gate exists.
14. Controlled pilot scope template exists.
15. Controlled pilot risk register template exists.
16. Controlled pilot evidence plan template exists.
17. Controlled pilot exit criteria template exists.

This gate must remain documentation and QA only.

## Non-authorization statement

This template does not authorize:

- real customer pilot;
- customer media ingestion;
- real scanner execution;
- real ffprobe or FFmpeg execution;
- external installation;
- customer production workflow dependency;
- legal or commercial commitment;
- support SLA;
- pricing;
- public demo;
- SaaS integration;
- database use;
- backend changes;
- frontend changes;
- installer packaging;
- runtime modification.

## Exit criteria template fields

A future pilot exit record must include the following fields before any decision is accepted.

### 1. Pilot identity

Required fields:

- `pilot_reference_id`;
- `pilot_candidate_reference`;
- `stakeholder_profile`;
- `pilot_owner_internal`;
- `pilot_owner_external`;
- `pilot_start_date`;
- `pilot_end_date`;
- `pilot_scope_reference`;
- `pilot_risk_register_reference`;
- `pilot_evidence_plan_reference`.

No real personal data or confidential project detail belongs in this generic template.

### 2. Pilot scope confirmation

The exit decision must confirm whether the executed pilot stayed inside the authorized scope.

Allowed values:

- `SCOPE_RESPECTED`;
- `SCOPE_RESPECTED_WITH_MINOR_RESERVATIONS`;
- `SCOPE_BREACH_DETECTED`;
- `SCOPE_NOT_EVALUABLE`.

If scope breach is detected, the pilot cannot be classified as clean success.

### 3. Evidence completeness

The exit decision must classify the evidence set.

Allowed values:

- `EVIDENCE_COMPLETE`;
- `EVIDENCE_COMPLETE_WITH_RESERVATIONS`;
- `EVIDENCE_INCOMPLETE`;
- `EVIDENCE_INVALID`;
- `EVIDENCE_NOT_COLLECTED`.

Evidence must be linked to the controlled pilot evidence plan, not improvised after the fact.

### 4. Value signal

The exit decision must classify whether the pilot demonstrated operational value.

Allowed values:

- `VALUE_SIGNAL_STRONG`;
- `VALUE_SIGNAL_MODERATE`;
- `VALUE_SIGNAL_WEAK`;
- `VALUE_SIGNAL_NOT_DEMONSTRATED`;
- `VALUE_SIGNAL_NOT_EVALUABLE`.

Value must be based on evidence, not enthusiasm alone.

### 5. Technical readiness outcome

The exit decision must classify technical readiness.

Allowed values:

- `TECHNICALLY_READY_FOR_NEXT_CONTROLLED_STAGE`;
- `TECHNICALLY_READY_WITH_RESERVATIONS`;
- `TECHNICAL_BLOCKERS_FOUND`;
- `TECHNICALLY_INCONCLUSIVE`;
- `TECHNICAL_SCOPE_NOT_YET_AVAILABLE`.

If a required real feature is still absent, the decision must say so explicitly.

### 6. Operational readiness outcome

The exit decision must classify operational readiness.

Allowed values:

- `OPERATIONALLY_READY_FOR_NEXT_CONTROLLED_STAGE`;
- `OPERATIONALLY_READY_WITH_RESERVATIONS`;
- `OPERATIONAL_BLOCKERS_FOUND`;
- `OPERATIONALLY_INCONCLUSIVE`;
- `OPERATOR_TRAINING_REQUIRED`.

Operational readiness includes operator clarity, support load, repeatability, stop conditions, and stakeholder expectation control.

### 7. Commercial fit outcome

The exit decision must classify commercial fit without making a sales commitment.

Allowed values:

- `COMMERCIAL_FIT_STRONG`;
- `COMMERCIAL_FIT_POSSIBLE`;
- `COMMERCIAL_FIT_WEAK`;
- `COMMERCIAL_FIT_NOT_DEMONSTRATED`;
- `COMMERCIAL_FIT_NOT_EVALUABLE`.

This is not a price proposal, contract offer, subscription commitment, or delivery promise.

### 8. Risk outcome

The exit decision must classify residual risk.

Allowed values:

- `RISK_ACCEPTABLE_FOR_NEXT_CONTROLLED_STAGE`;
- `RISK_ACCEPTABLE_WITH_MITIGATIONS`;
- `RISK_TOO_HIGH`;
- `RISK_INCONCLUSIVE`;
- `RISK_REGISTER_INCOMPLETE`.

A high residual risk blocks escalation even if the stakeholder is interested.

## Final exit classifications

Exactly one final classification must be selected.

### A. `PILOT_SUCCESS`

Use only when:

- scope was respected;
- evidence is complete;
- value signal is strong or moderate;
- no critical risk remains open;
- technical readiness is adequate for the next controlled stage;
- the stakeholder understands the current limits.

This classification still does not authorize production rollout.

### B. `PILOT_SUCCESS_WITH_RESERVATIONS`

Use when:

- value is demonstrated;
- some limitations remain;
- risks are known and mitigable;
- next stage requires explicit corrections or restrictions.

This classification is useful when the product direction is validated but not yet fully ready.

### C. `PILOT_INCONCLUSIVE`

Use when:

- evidence is incomplete or ambiguous;
- test conditions were not representative;
- stakeholder feedback is mixed;
- technical or operational signals are not strong enough.

This classification should lead to either a revised pilot design or a pause.

### D. `PILOT_STOPPED_FOR_RISK`

Use when:

- privacy, data, legal, support, expectation, technical, or operational risk becomes unacceptable;
- scope cannot be protected;
- the customer wants functionality outside the authorized boundary;
- evidence collection would become unsafe.

This classification is a protective stop, not a failure of discipline.

### E. `PILOT_NO_COMMERCIAL_FIT`

Use when:

- the stakeholder has no urgent pain;
- value is not material;
- budget or adoption path is unlikely;
- workflow mismatch is clear;
- the product would require excessive customization.

This avoids forcing a pilot into a weak commercial channel.

### F. `PILOT_PENDING_TECHNICAL_DEVELOPMENT`

Use when:

- interest is real;
- value hypothesis remains credible;
- but a required technical capability is not yet implemented;
- the honest next step is product development, not continued pilot conversation.

This classification is important for avoiding overpromising.

## Exit decision table

| Field | Required | Acceptable examples |
|---|---:|---|
| Scope status | Yes | `SCOPE_RESPECTED`, `SCOPE_RESPECTED_WITH_MINOR_RESERVATIONS` |
| Evidence status | Yes | `EVIDENCE_COMPLETE`, `EVIDENCE_COMPLETE_WITH_RESERVATIONS` |
| Value signal | Yes | `VALUE_SIGNAL_STRONG`, `VALUE_SIGNAL_MODERATE` |
| Technical readiness | Yes | `TECHNICALLY_READY_WITH_RESERVATIONS` |
| Operational readiness | Yes | `OPERATIONALLY_READY_WITH_RESERVATIONS` |
| Commercial fit | Yes | `COMMERCIAL_FIT_POSSIBLE` |
| Risk status | Yes | `RISK_ACCEPTABLE_WITH_MITIGATIONS` |
| Final classification | Yes | one of the six final classifications |

## Hard stop conditions

A future pilot must stop, pause, or be classified as blocked if any of the following occurs:

- material outside the authorized scope is introduced;
- the stakeholder asks to use the tool as production-critical infrastructure;
- confidentiality or consent is unclear;
- evidence cannot be captured safely;
- output quality is being interpreted as a final product claim;
- support burden exceeds the authorized pilot boundary;
- the operator cannot reproduce the procedure;
- a critical risk has no mitigation;
- a product capability is missing but being implied as available.

## Required exit narrative

The exit decision must include a short written narrative with five sections:

1. `What was tested`.
2. `What was demonstrated`.
3. `What was not demonstrated`.
4. `What risk remains`.
5. `Recommended next controlled step`.

The narrative must be plain enough for a producer, production manager, school director, post supervisor, or internal product owner.

## Allowed next steps after exit

Allowed next steps must remain conservative.

Allowed outputs:

- `PROCEED_TO_NEXT_CONTROLLED_STAGE`;
- `REPEAT_WITH_REVISED_SCOPE`;
- `PAUSE_UNTIL_TECHNICAL_CAPABILITY_EXISTS`;
- `REJECT_PILOT_ESCALATION`;
- `REQUIRE_RISK_MITIGATION_FIRST`;
- `REQUIRE_COMMERCIAL_CLARIFICATION_FIRST`.

Not allowed:

- automatic production rollout;
- automatic paid subscription;
- automatic external installation;
- automatic processing of real media;
- automatic SaaS integration;
- automatic support commitment;
- automatic legal or pricing commitment.

## Operator wording

Safe wording:

> The pilot result indicates whether this controlled path deserves a next controlled stage. It does not turn the current demo into a finished product or production deployment.

Unsafe wording:

> The pilot proved the product is ready for production use.

Unsafe wording:

> We can now process all your real material.

Unsafe wording:

> This is ready for a paid rollout.

## Required evidence boundaries

The exit record must distinguish:

- evidence produced by the tool;
- evidence observed by the operator;
- feedback from the stakeholder;
- assumptions made by the internal team;
- items that remain unverified.

Feedback is not evidence unless it is linked to a specific observed event or documented decision.

## Template skeleton

A future filled pilot exit record may use this skeleton:

```text
pilot_reference_id: TBD
stakeholder_profile: TBD
scope_status: TBD
evidence_status: TBD
value_signal: TBD
technical_readiness: TBD
operational_readiness: TBD
commercial_fit: TBD
risk_status: TBD
final_classification: TBD

what_was_tested:
  TBD

what_was_demonstrated:
  TBD

what_was_not_demonstrated:
  TBD

remaining_risks:
  TBD

recommended_next_controlled_step:
  TBD

explicit_non_authorizations:
  - no production rollout authorized
  - no external installation authorized
  - no customer media processing authorized
  - no support commitment authorized
  - no pricing or contract commitment authorized
```

## QA expectations

The companion QA test must verify that this document:

- names the phase;
- names the expected closure result;
- includes all six final exit classifications;
- includes hard stop conditions;
- includes conservative allowed next steps;
- blocks automatic production rollout;
- blocks real customer media processing;
- blocks external installation;
- requires evidence completeness;
- requires residual risk classification;
- requires a written exit narrative;
- remains documentation and QA only.

## Closure statement

This gate is closed only when the document and QA test are added, the scoped tests pass, mandatory guards pass, and the change is committed and tagged without modifying runtime, pyproject, commands, scanner, ffprobe, FFmpeg, SaaS, database, installer, backend, or frontend.
