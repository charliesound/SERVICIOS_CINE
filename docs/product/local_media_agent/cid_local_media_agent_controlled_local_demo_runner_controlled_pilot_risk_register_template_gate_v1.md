# CID Local Media Agent — Controlled Pilot Risk Register Template Gate V1

## Gate identity

- Gate name: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.RISK.REGISTER.TEMPLATE.GATE.V1`
- Expected closure result: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_RISK_REGISTER_TEMPLATE_GATE_V1_CLOSED`
- Product area: `CID Local Media Agent`
- Current artifact type: documentation and QA only
- Operational maturity: controlled planning artifact for a future pilot, not a pilot authorization
- Baseline dependency: the controlled pilot scope template gate must already be closed

## Purpose

This gate creates a reusable internal risk register template for a future controlled pilot of CID Local Media Agent.

The template is intentionally conservative. It helps evaluate pilot risk before any real customer material, external installation, operational support commitment, pricing promise, or production-like execution is accepted.

The risk register is meant to be filled only after a contact has passed the controlled demo flow and has been classified as a candidate for a future pilot. It does not convert a candidate into an authorized pilot.

## Non-authorization statement

This gate does not authorize:

- real customer media;
- real production material;
- external installation;
- processing client files;
- scanner execution;
- ffprobe execution;
- FFmpeg execution;
- SaaS/database access;
- remote support commitment;
- pricing commitment;
- contract execution;
- public demo;
- production use;
- product-final claims.

Any future pilot must still pass dedicated authorization gates for legal, data, technical, support, security, operational, and commercial readiness.

## Required upstream gates

Before this template can be used with a real opportunity, the following gates must exist as closed or be explicitly superseded by a stricter later gate:

1. Controlled local demo runner operator evidence pack gate.
2. Demo narrative gate.
3. Operator runbook gate.
4. Failure modes and recovery gate.
5. Demo acceptance checklist gate.
6. Stakeholder demo brief gate.
7. Controlled external demo readiness gate.
8. External demo feedback capture gate.
9. External demo follow-up decision gate.
10. Controlled pilot candidate gate.
11. Controlled pilot boundary gate.
12. Controlled pilot prerequisites gate.
13. Controlled pilot scope template gate.

## Risk register status values

Use only these statuses:

- `OPEN`
- `MITIGATED`
- `ACCEPTED_WITH_RESERVATION`
- `BLOCKING`
- `REJECTED`
- `NOT_APPLICABLE`

No risk can be silently ignored. A risk that is unknown must remain `OPEN` or `BLOCKING`.

## Risk severity values

Use only these severity values:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

`HIGH` and `CRITICAL` risks require a named mitigation and an owner before any pilot proposal can advance.

## Risk probability values

Use only these probability values:

- `LOW`
- `MEDIUM`
- `HIGH`
- `UNKNOWN`

`UNKNOWN` probability must not be treated as safe. It must be reviewed before pilot authorization.

## Risk ownership fields

Every risk entry must include:

- risk id;
- risk title;
- category;
- description;
- trigger condition;
- severity;
- probability;
- owner;
- mitigation;
- stop condition;
- evidence required;
- current status;
- decision date;
- follow-up action.

## Required risk categories

The future pilot risk register must include, at minimum, the following categories:

### 1. Customer data and material risk

Covers risks related to real media, personal data, copyrighted material, unreleased production content, confidential folders, incomplete consent, unclear ownership, sensitive metadata, or accidental access to material outside the agreed scope.

Minimum required risks:

- material ownership unclear;
- consent incomplete;
- customer provides more material than allowed;
- confidential filenames or paths become visible;
- operator accidentally opens material outside the pilot folder;
- customer expects production-grade data handling before authorization.

### 2. Technical readiness risk

Covers risks related to immature functionality, missing scanner behavior, missing real ffprobe/FFmpeg integration, unsupported formats, performance uncertainty, output variability, environment mismatch, and lack of installer readiness.

Minimum required risks:

- scanner real execution not yet authorized;
- media probing not yet authorized for client material;
- unsupported codec/container expectations;
- hardware mismatch between internal demo and customer environment;
- output format expectations exceed current controlled artifact;
- no signed installer available yet.

### 3. Operator and workflow risk

Covers risks related to human execution, inconsistent demo framing, failure to follow the runbook, mishandling of preserved output roots, incomplete cleanup, poor note-taking, or unclear escalation.

Minimum required risks:

- operator skips preflight;
- operator uses the wrong command;
- operator fails to clean temporary output;
- operator over-explains technical evidence and loses stakeholder context;
- feedback is captured without decision criteria;
- failure is improvised instead of stopped.

### 4. Expectation and commercial risk

Covers risks related to overpromising, premature pricing, perceived product-final status, public-demo confusion, roadmap pressure, and unclear pilot success criteria.

Minimum required risks:

- stakeholder interprets controlled demo as finished product;
- pilot candidate expects immediate production use;
- price is discussed before scope and risk acceptance;
- pilot success criteria are vague;
- product roadmap is inferred from technical demo;
- external stakeholder expects support level not approved.

### 5. Legal, confidentiality, and permission risk

Covers risks related to NDA status, permission to use material, production confidentiality, credits, distribution restrictions, data-processing terms, and storage boundaries.

Minimum required risks:

- confidentiality terms not approved;
- data-processing responsibility unclear;
- pilot material includes third-party restrictions;
- stakeholder lacks authority to approve pilot;
- deletion and retention expectations are undefined;
- screenshots or recordings are not allowed.

### 6. Support and operational risk

Covers risks related to support availability, response time expectations, rollback, issue triage, incident communication, and pilot interruption.

Minimum required risks:

- no support window approved;
- operator availability does not match pilot expectation;
- rollback process undefined;
- incident severity levels undefined;
- customer expects live troubleshooting beyond agreed scope;
- pilot interruption criteria not documented.

### 7. Security and local boundary risk

Covers risks related to local-only boundaries, network assumptions, repository safety, temporary folders, command boundaries, write locations, and unintended persistence.

Minimum required risks:

- local-only guarantee misunderstood;
- network access expectation unclear;
- temporary output not deleted;
- files are written outside controlled output root;
- customer asks for cloud upload before authorization;
- repository or development environment is exposed during demo.

### 8. Success criteria and evidence risk

Covers risks related to unclear pass/fail criteria, weak evidence, anecdotal feedback, missing baseline, and lack of objective decision records.

Minimum required risks:

- success criteria are not measurable;
- evidence pack is not captured;
- stakeholder feedback is vague;
- no decision record is written;
- pilot output cannot be compared against baseline;
- blocker risks remain open.

## Template table

Use the following structure for each pilot risk entry:

| Field | Required value |
| --- | --- |
| Risk ID | `RISK-XXX` |
| Risk title | Short operational title |
| Category | One of the required categories |
| Description | What can go wrong |
| Trigger condition | What event makes the risk active |
| Severity | `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` |
| Probability | `LOW`, `MEDIUM`, `HIGH`, or `UNKNOWN` |
| Owner | Named responsible role, not a vague group |
| Mitigation | Specific preventive or corrective action |
| Stop condition | What must stop the pilot path |
| Evidence required | What proof is needed |
| Current status | `OPEN`, `MITIGATED`, `ACCEPTED_WITH_RESERVATION`, `BLOCKING`, `REJECTED`, or `NOT_APPLICABLE` |
| Decision date | Date of the last decision |
| Follow-up action | Next controlled action |

## Example placeholder entries

The following examples are placeholders. They must not be treated as filled customer risk records.

### Example RISK-001 — Material ownership unclear

- Risk ID: `RISK-001`
- Category: customer data and material risk
- Description: the stakeholder may provide material without clear ownership or permission.
- Trigger condition: customer proposes using real project media without written scope approval.
- Severity: `HIGH`
- Probability: `UNKNOWN`
- Owner: pilot owner
- Mitigation: require written scope, permitted material list, and responsible approver.
- Stop condition: ownership or permission remains unclear.
- Evidence required: approved pilot scope and permitted material description.
- Current status: `BLOCKING`
- Follow-up action: do not accept files until legal/data prerequisites are closed.

### Example RISK-002 — Product-final expectation

- Risk ID: `RISK-002`
- Category: expectation and commercial risk
- Description: the stakeholder may interpret the controlled demo as a finished product.
- Trigger condition: stakeholder asks whether it can be deployed immediately in production.
- Severity: `HIGH`
- Probability: `MEDIUM`
- Owner: demo operator
- Mitigation: restate that the current chain is a controlled technical demo and planning framework.
- Stop condition: stakeholder insists on production use before authorization.
- Evidence required: meeting note confirming the limitation was explained.
- Current status: `OPEN`
- Follow-up action: classify as wait-until-runtime-ready or reject as premature.

### Example RISK-003 — Support scope unclear

- Risk ID: `RISK-003`
- Category: support and operational risk
- Description: the customer may expect immediate support outside an agreed window.
- Trigger condition: stakeholder requests live troubleshooting or rapid turnaround during pilot.
- Severity: `MEDIUM`
- Probability: `UNKNOWN`
- Owner: pilot owner
- Mitigation: define support window, escalation route, and interruption criteria before pilot authorization.
- Stop condition: support expectations exceed approved capacity.
- Evidence required: written support boundary in the pilot scope.
- Current status: `OPEN`
- Follow-up action: include support boundary in pilot scope template before approval.

## Blocking criteria

A future pilot must not proceed if any of the following conditions exists:

- any `CRITICAL` risk remains `OPEN`;
- any data/material risk is `BLOCKING`;
- permission to use material is incomplete;
- stakeholder authority is unclear;
- pilot scope is not approved;
- support boundary is not approved;
- local-only boundary cannot be preserved;
- output, retention, or deletion expectations are undefined;
- commercial expectations exceed current technical maturity;
- product-final claims are required by the stakeholder.

## Acceptance criteria for this gate

This documentation gate is accepted only if:

- it remains documentation and QA only;
- it creates no runtime code;
- it creates no scanner behavior;
- it performs no media probing;
- it performs no FFmpeg work;
- it accepts no customer material;
- it defines risk categories, status values, severity values, probability values, ownership fields, required evidence, blocking criteria, and non-authorization boundaries;
- it links risk handling to prior demo, feedback, pilot candidate, pilot boundary, pilot prerequisites, and pilot scope template gates;
- it keeps all future pilot authorization explicitly blocked.

## Closure statement

If the QA test for this document passes and the repository guards pass, this phase may close with:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_RISK_REGISTER_TEMPLATE_GATE_V1_CLOSED`
