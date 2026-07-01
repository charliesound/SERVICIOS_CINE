# CID Local Media Agent — Controlled Pilot Evidence Plan Template Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.EVIDENCE.PLAN.TEMPLATE.GATE.V1`
- Expected closure result: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_EVIDENCE_PLAN_TEMPLATE_GATE_V1_CLOSED`
- Commit message: `docs: add CID Local Media Agent controlled local demo runner pilot evidence plan template gate`
- Tag: `cid-dev-stable-local-media-agent-controlled-local-demo-runner-pilot-evidence-plan-template-gate-v1-20260630`
- Scope: documentation and QA test only.
- Status: template gate for a possible future controlled pilot.
- Current authorization: planning artifact only.

## Purpose

This gate defines a reusable evidence plan template for a future controlled pilot of CID Local Media Agent.

The template answers one operational question:

> If a future pilot becomes authorized by later gates, what evidence must be collected to decide whether the pilot demonstrated real value without exceeding approved boundaries?

This document does not approve a pilot. It does not approve client material, external installation, production use, support commitments, pricing, contracts, or processing of any real client asset.

## Explicit non-authorizations

This gate does not authorize:

- real client media;
- production media;
- external installation;
- public demo;
- scanner execution;
- ffprobe or FFmpeg execution;
- network access;
- SaaS or database access;
- installer work;
- backend or frontend work;
- contractual commitment;
- pricing commitment;
- operational support commitment;
- material ingestion from a productora, school, post house, distributor, institution, or production office.

The only currently demonstrated technical chain remains the controlled local demo runner and its controlled text artifact evidence.

## Relationship with previous gates

This gate depends conceptually on the already closed gates for:

1. controlled local demo runner execution;
2. operator evidence;
3. demo narrative;
4. operator runbook;
5. failure modes and recovery;
6. demo acceptance checklist;
7. stakeholder brief;
8. controlled external demo readiness;
9. feedback capture;
10. follow-up decision;
11. pilot candidate classification;
12. pilot boundary;
13. pilot prerequisites;
14. pilot scope template;
15. pilot risk register template.

This gate adds the missing evidence dimension: how a future pilot would be measured, captured, reviewed, anonymized, and stopped.

## Evidence plan template status

The evidence plan is a blank reusable template. It must not contain:

- customer name;
- project title;
- real production title;
- real file names;
- private locations;
- private budgets;
- personal data;
- credentials;
- secrets;
- actual media paths;
- actual client feedback;
- real pilot dates.

A filled version would require a later explicit gate.

## Evidence principles

A future controlled pilot evidence plan must follow these principles:

1. Collect only what is necessary to evaluate value.
2. Separate technical evidence from business evidence.
3. Separate operator notes from customer feedback.
4. Avoid retaining material that is not needed.
5. Prefer anonymized summaries over raw sensitive details.
6. Record blocked items as useful evidence, not as failures to hide.
7. Preserve exact runner evidence when using the controlled runner.
8. Stop the pilot when boundaries are exceeded.
9. Make every acceptance decision traceable.
10. Never convert uncertainty into a sales claim.

## Evidence categories

### 1. Technical execution evidence

Required fields:

- command or procedure executed;
- operator identity or internal role placeholder;
- machine profile placeholder;
- operating system placeholder;
- start and end timestamps placeholder;
- runner status;
- artifact name;
- artifact bytes;
- artifact SHA256;
- cleanup status;
- failure mode if any;
- recovery action if any;
- boundary confirmation.

For the current controlled runner chain, the stable artifact reference remains:

- artifact name: `controlled_visible_report.controlled.txt`
- artifact bytes: `167`
- artifact SHA256: `277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f`
- runner status: `CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED`
- boundary token: `DEMO_TECNICA_LOCAL_CONTROLADA_ONLY`

### 2. Workflow value evidence

Required fields:

- stakeholder profile;
- pain point observed;
- current manual workaround;
- expected value hypothesis;
- time-saving hypothesis;
- review burden hypothesis;
- handoff improvement hypothesis;
- production-office usefulness;
- post-production usefulness;
- sound/post usefulness;
- education or training usefulness if applicable;
- confidence level.

The evidence plan must distinguish measured evidence from opinion.

### 3. Feedback evidence

Required fields:

- what the stakeholder understood;
- what they misunderstood;
- strongest positive reaction;
- strongest objection;
- most requested missing capability;
- readiness concern;
- trust concern;
- buying or adoption signal;
- support expectation;
- follow-up decision recommendation.

No real feedback is stored in this template.

### 4. Risk evidence

Required fields:

- risk identifier;
- risk category;
- risk description;
- likelihood;
- impact;
- current mitigation;
- owner;
- stop condition;
- review status.

Risk evidence must reference the pilot risk register template instead of replacing it.

### 5. Privacy and data handling evidence

Required fields:

- data classification placeholder;
- permitted input class;
- excluded input class;
- anonymization rule;
- retention rule;
- deletion rule;
- access rule;
- reviewer rule;
- consent status placeholder;
- evidence redaction status.

A future pilot must prefer redacted summaries and hashes over raw customer material wherever possible.

### 6. Operator evidence

Required fields:

- operator preparation completed;
- runbook followed;
- acceptance checklist checked;
- failure modes known;
- recovery path known;
- no improvisation statement;
- cleanup confirmation;
- issue log created if needed;
- stop decision recorded if needed.

### 7. Commercial evidence

Required fields:

- stakeholder segment;
- urgency level;
- budget owner unknown or known placeholder;
- adoption friction;
- procurement friction;
- integration request;
- pricing sensitivity placeholder;
- next-step appetite;
- no-promise confirmation;
- recommended route.

Commercial evidence must not imply a price or final product readiness.

## Evidence capture matrix

| Evidence ID | Category | Capture method | Required? | Owner placeholder | Retention rule | Stop trigger |
|---|---|---:|---:|---|---|---|
| EVID-TECH-001 | Technical execution | runner JSON or controlled log summary | Yes | internal operator | keep redacted summary | unexpected status |
| EVID-TECH-002 | Artifact integrity | bytes and SHA256 | Yes | internal operator | keep hash and byte count | mismatch |
| EVID-OPS-001 | Operator process | runbook checklist | Yes | internal operator | keep checklist summary | runbook not followed |
| EVID-VALUE-001 | Pain validation | stakeholder interview notes | Yes | product owner | anonymized notes | no clear pain |
| EVID-VALUE-002 | Workflow value | before/after hypothesis | Yes | product owner | summary only | value not explainable |
| EVID-FEED-001 | Objections | feedback form | Yes | product owner | anonymized notes | blocker objection |
| EVID-RISK-001 | Risk delta | risk register update | Yes | product owner | risk summary | high unmitigated risk |
| EVID-PRIV-001 | Data boundary | data handling checklist | Yes | product owner | approval summary | unclear data permission |
| EVID-COMM-001 | Commercial signal | follow-up decision record | Optional | business owner | summary only | premature sales pressure |
| EVID-STOP-001 | Stop decision | stop record | Conditional | accountable owner | keep decision summary | boundary breach |

## Evidence quality levels

### Level 0 — Not evidence

Examples:

- “They liked it.”
- “It looks useful.”
- “They might pay.”
- “It worked on my machine.”
- “It should scale later.”

### Level 1 — Weak evidence

Examples:

- one informal comment;
- one uncontrolled observation;
- unstructured feedback;
- unverified expectation;
- vague request for future features.

### Level 2 — Useful controlled evidence

Examples:

- structured feedback mapped to stakeholder segment;
- controlled runner JSON;
- verified artifact hash and byte count;
- runbook checklist completed;
- specific workflow pain observed;
- clear follow-up decision.

### Level 3 — Pilot-grade evidence

Examples:

- predefined success criteria reviewed;
- permitted input class respected;
- measurable workflow effect;
- recorded risk changes;
- redacted evidence package;
- explicit stop/no-stop decision;
- stakeholder validation from an accountable role.

This template targets Level 2 and prepares for Level 3 in later gates.

## Success evidence placeholders

A future pilot evidence plan may include success criteria such as:

- stakeholder can explain the value in their own words;
- operator can execute without improvising;
- no boundary breach occurs;
- evidence package is complete;
- feedback maps to a real production workflow;
- risks remain acceptable;
- missing capabilities are clearly classified;
- next step is justified by evidence, not enthusiasm.

## Failure evidence placeholders

A future pilot must treat the following as valid evidence:

- stakeholder expected real scanning when only controlled runner exists;
- stakeholder requested processing of real material before authorization;
- operator needed to improvise;
- evidence was incomplete;
- boundaries were unclear;
- cleanup was not confirmed;
- technical output was correct but business value was not understood;
- interest was polite but not operational;
- risks exceeded current readiness.

Failure evidence should drive scope reduction or pilot deferral.

## Stop conditions

A future pilot must stop or not start if:

- client material is proposed without a later explicit authorization gate;
- the stakeholder expects production use;
- a legal or confidentiality boundary is unclear;
- the operator cannot explain current limitations;
- support expectations exceed current capacity;
- data retention cannot be defined;
- success criteria are vague;
- there is pressure to promise scanner, ffprobe, FFmpeg, SaaS, installer, or production workflows before they exist;
- the evidence plan cannot be completed.

## Evidence package outline for a future filled version

A later filled evidence package should include:

1. pilot identity placeholder;
2. stakeholder role and segment;
3. approved scope reference;
4. approved risk register reference;
5. evidence matrix;
6. technical run evidence;
7. operator checklist;
8. stakeholder feedback summary;
9. value assessment;
10. risk delta;
11. stop/no-stop decisions;
12. final recommendation.

This gate creates only the template.

## Review roles

A future filled plan should identify:

- internal operator;
- product owner;
- technical reviewer;
- business reviewer;
- customer representative placeholder;
- final decision owner.

No real names are included in this template.

## Required closure checks for this gate

To close this gate, the repository must confirm:

- only this document and its QA test are staged;
- no runtime files are changed;
- no package entrypoints are changed;
- no scanner code is changed;
- no ffprobe or FFmpeg integration is changed;
- no SaaS, database, backend, frontend, installer, or pyproject file is changed;
- previous demo and pilot-planning gates still pass;
- WSL repository guard passes;
- PostgreSQL-only regression guard passes.

## Final statement

This gate creates a controlled pilot evidence plan template. It improves readiness for a future pilot conversation, but it does not authorize a pilot, customer material, external installation, production processing, pricing, contract, or product-final claim.
