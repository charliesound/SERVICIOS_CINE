# CID Local Media Agent — Controlled Pilot Scope Template Gate V1

## Gate identity

- Gate name: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.SCOPE.TEMPLATE.GATE.V1`
- Expected close result: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_SCOPE_TEMPLATE_GATE_V1_CLOSED`
- Scope: documentation and QA test only.
- Product line: CID Local Media Agent.
- Baseline before this gate: the controlled pilot prerequisites gate is closed.

## Purpose

This gate creates a reusable scope template for a possible future controlled pilot of CID Local Media Agent.

The template is intentionally blank. It must not contain real client names, production titles, locations, personal data, confidential media references, pricing, contract terms, installation approval, or real pilot authorization.

The objective is to prepare a consistent structure for future pilot planning without allowing the project to jump from prerequisite review into real execution.

## Current authorized state

The authorized state remains:

- controlled local technical demo only;
- fixture-owned temporary output only;
- single controlled text artifact only;
- installed command smoke only;
- operator-controlled explanation only;
- external feedback capture only;
- follow-up decision only;
- pilot candidate classification only;
- pilot boundary definition only;
- pilot prerequisites definition only.

## Explicit non-authorizations

This gate does not authorize:

- real client media;
- production media;
- client project drives;
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
- real pilot start;
- pilot success claim;
- product readiness claim.

## Template status labels

The future filled scope may only use one of these status labels:

- `PILOT_SCOPE_TEMPLATE_BLANK`
- `PILOT_SCOPE_DRAFT_INCOMPLETE`
- `PILOT_SCOPE_DRAFT_REVIEW_REQUIRED`
- `PILOT_SCOPE_READY_FOR_APPROVAL_GATE`
- `PILOT_SCOPE_BLOCKED_BY_UNCLEAR_DATA`
- `PILOT_SCOPE_BLOCKED_BY_TECHNICAL_GAP`
- `PILOT_SCOPE_BLOCKED_BY_COMMERCIAL_AMBIGUITY`
- `PILOT_SCOPE_BLOCKED_BY_LEGAL_OR_CONFIDENTIALITY_GAP`

No status in this gate may authorize real execution.

## Controlled pilot scope template

The following template is the only approved structure for a future controlled pilot scope draft.

### 1. Pilot identity

Fields to fill in a later controlled gate:

- candidate organization placeholder;
- stakeholder role placeholder;
- internal CID owner placeholder;
- client-side owner placeholder;
- technical contact placeholder;
- decision-maker placeholder;
- date placeholder;
- scope version placeholder;
- status label placeholder.

Forbidden at this stage:

- real organization name;
- real personal name;
- real email address;
- real project title;
- confidential production code name.

### 2. Business problem hypothesis

Fields to fill in a later controlled gate:

- operational pain statement;
- current workflow description;
- frequency of the problem;
- cost of the problem;
- stakeholder affected;
- expected learning from the pilot;
- reason the controlled demo was insufficient;
- reason a future pilot may be justified.

The hypothesis must be about workflow validation, not about guaranteed product value.

### 3. Proposed pilot objective

Fields to fill in a later controlled gate:

- primary pilot objective;
- secondary pilot objective;
- explicit non-objectives;
- what the pilot must prove;
- what the pilot must not claim;
- minimum observable evidence;
- maximum scope boundary;
- stop condition.

Required operator framing:

> This scope template prepares a possible future controlled pilot. It does not authorize real media, installation, or production use.

Forbidden phrasing:

- We can start the pilot now.
- Send the production drive.
- This is ready for client deployment.
- This confirms product-market fit.
- This is a paid subscription scope.

### 4. Allowed input category placeholder

A later filled template must define whether inputs are:

- synthetic fixture only;
- sanitized sample only;
- client-approved non-production sample;
- generated proxy material;
- metadata-only sample.

This gate keeps real client material blocked until a later explicit authorization gate.

The filled template must document:

- allowed input type;
- maximum file count;
- maximum size;
- accepted formats;
- forbidden formats;
- whether audio is included;
- whether video is included;
- whether metadata is included;
- whether any personal data could appear;
- whether any copyrighted third-party material could appear.

### 5. Disallowed input category placeholder

A later filled template must explicitly reject:

- full production folders;
- camera cards;
- sound rolls;
- rushes from active productions;
- private cast or crew data;
- contracts;
- call sheets;
- location permits;
- legal documents;
- payroll documents;
- distribution materials;
- client database exports;
- unreleased confidential creative material.

### 6. Technical capability boundary

The filled scope must separate:

- current controlled demo capability;
- future capability under evaluation;
- unavailable capability;
- blocked capability;
- out-of-scope capability.

The template must preserve these current limits:

- no real scanner execution;
- no real FFmpeg execution;
- no real ffprobe execution;
- no real transcription;
- no real synchronization;
- no real indexing;
- no SaaS connection;
- no database access;
- no installer;
- no automated client workflow.

### 7. Environment placeholder

Fields to fill in a later controlled gate:

- execution machine placeholder;
- operating system placeholder;
- local path placeholder;
- isolation requirement;
- network requirement;
- storage requirement;
- cleanup requirement;
- rollback requirement;
- log retention requirement;
- evidence capture requirement.

Default boundary:

- local controlled environment only;
- no client workstation approval;
- no remote access approval;
- no persistent client installation approval.

### 8. Duration and cadence placeholder

Fields to fill in a later controlled gate:

- pilot duration placeholder;
- number of sessions placeholder;
- maximum operator hours placeholder;
- maximum client time required placeholder;
- review cadence placeholder;
- feedback deadline placeholder;
- closure meeting placeholder;
- no-open-ended-pilot rule.

A future pilot must have a start, stop, and review decision.

### 9. Success criteria placeholder

The filled scope must define measurable criteria such as:

- time saved hypothesis;
- error reduction hypothesis;
- clarity of report output;
- operator usability;
- stakeholder comprehension;
- value signal strength;
- technical confidence;
- support load;
- risk level;
- decision usefulness.

The template must not define success as:

- client likes it;
- demo looked impressive;
- pilot felt promising;
- product is ready;
- revenue is guaranteed.

### 10. Evidence capture placeholder

A future filled scope must define allowed evidence:

- operator notes;
- anonymized issue list;
- timestamped decision log;
- non-sensitive screenshots if approved;
- command output summary;
- pass/fail checklist;
- stakeholder feedback summary;
- follow-up decision record.

Blocked evidence:

- raw client media;
- confidential project files;
- personal documents;
- hidden metadata dumps;
- uncontrolled logs;
- private communications;
- screenshots containing protected information.

### 11. Support and incident boundary

A future filled scope must define:

- support contact;
- support hours;
- incident stop condition;
- escalation path;
- rollback owner;
- cleanup owner;
- what happens if output is wrong;
- what happens if the operator is unavailable;
- what happens if client expectations expand.

Default boundary:

- no support SLA;
- no production reliability promise;
- no unattended execution;
- no emergency support;
- no obligation to process additional material.

### 12. Legal, confidentiality, and approval placeholder

A later gate must confirm:

- written approval exists;
- confidentiality terms exist;
- retention/deletion terms exist;
- permitted evidence collection is defined;
- pilot owner is identified;
- stop/withdrawal process is defined;
- no sensitive data is accepted without explicit later authorization.

This template does not create legal approval.

### 13. Commercial boundary placeholder

A future filled scope may record commercial learning, but must not define:

- price;
- paid subscription;
- binding contract;
- delivery date;
- roadmap commitment;
- service obligation;
- guarantee of future availability.

Allowed commercial notes:

- perceived value;
- urgency;
- budget owner hypothesis;
- decision process hypothesis;
- buying committee hypothesis;
- willingness to continue conversation;
- blockers to adoption.

### 14. Exit decision placeholder

A future filled scope must end with one of these decisions:

- `PILOT_SCOPE_NOT_READY`
- `PILOT_SCOPE_NEEDS_REVISION`
- `PILOT_SCOPE_READY_FOR_APPROVAL_GATE`
- `PILOT_SCOPE_REJECTED`
- `PILOT_SCOPE_DEFERRED_UNTIL_REAL_SCANNER`
- `PILOT_SCOPE_DEFERRED_UNTIL_INSTALLER`
- `PILOT_SCOPE_DEFERRED_UNTIL_LEGAL_TERMS`

No exit decision in this template starts a real pilot.

## Stop conditions

The operator must stop scope preparation if:

- the client wants to send real media immediately;
- the client asks for installation before approval;
- the client expects production reliability;
- success criteria are vague;
- confidentiality terms are absent;
- material boundaries are unclear;
- the client asks for price before scope is understood;
- internal technical readiness is not aligned;
- the requested workflow requires real scanner execution;
- the requested workflow requires real FFmpeg or ffprobe execution;
- the requested workflow requires SaaS or database integration.

## Required prior gate dependencies

This template depends on the closure of:

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
- controlled pilot boundary gate;
- controlled pilot prerequisites gate.

## QA expectations

The QA test for this gate must verify that:

- the phase and result token are declared;
- the scope remains documentation and QA only;
- the template is blank and reusable;
- real client media remains blocked;
- pilot execution remains blocked;
- allowed and disallowed input placeholders exist;
- success criteria, evidence, support, legal, and commercial placeholders exist;
- stop conditions are explicit;
- prior gate dependencies are listed;
- no product readiness claim is made.

## Close result

If this gate is accepted, the only valid close result is:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_SCOPE_TEMPLATE_GATE_V1_CLOSED`
