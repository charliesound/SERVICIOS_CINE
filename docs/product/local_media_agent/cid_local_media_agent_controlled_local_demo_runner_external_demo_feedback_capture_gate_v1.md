# CID Local Media Agent — Controlled Local Demo Runner — External Demo Feedback Capture Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.EXTERNAL.DEMO.FEEDBACK.CAPTURE.GATE.V1`
- Expected result token: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_EXTERNAL_DEMO_FEEDBACK_CAPTURE_GATE_V1_CLOSED`
- Product area: `CID Local Media Agent`
- Gate type: documentation and QA only
- Intended use: internal feedback capture after a controlled external demo
- Audience: operator, product owner, and commercial reviewer
- Baseline assumption: the controlled external demo readiness gate has already passed

## Purpose

This gate defines how feedback must be captured immediately after a controlled external demo of the local technical runner.

The goal is not to sell, close, quote, promise delivery, or expand scope. The goal is to turn a controlled demo conversation into structured evidence that can inform the next product decision.

The feedback capture must help answer five practical questions:

1. Did the stakeholder understand the controlled demo boundary?
2. Did the demo address a real workflow pain?
3. Which future capabilities matter most to that stakeholder?
4. What objections or risks were raised?
5. Is the stakeholder suitable for a later pilot conversation, or should the contact remain exploratory?

## Scope

This gate is documentation and QA only.

Allowed:

- Define a post-demo feedback capture structure.
- Define stakeholder classification after the demo.
- Define questions for product, workflow, trust, technical, and commercial feedback.
- Define how to record objections without converting them into commitments.
- Define a conservative next-step decision model.
- Define evidence quality requirements for internal review.

Forbidden:

- No runtime implementation.
- No command implementation.
- No pyproject change.
- No scanner execution.
- No media scanning.
- No real ffprobe execution.
- No real FFmpeg execution.
- No real media processing.
- No real client material.
- No SaaS access.
- No database access.
- No installer work.
- No backend change.
- No frontend change.
- No pricing promise.
- No delivery date promise.
- No pilot commitment.
- No public demo claim.
- No production-readiness claim.

## Operating boundary to repeat before feedback

Before asking for feedback, the operator must restate the demo boundary:

> What you have seen is a controlled local technical demo. It proves a narrow local execution chain with deterministic output and safety boundaries. It is not yet the full product, not a public demo, not a real scanner, not real media analysis, and not a final client workflow.

The feedback must be requested in that context.

## Feedback capture timing

Feedback should be captured in three moments:

1. **Immediate verbal feedback** during the call or meeting.
2. **Operator notes** within 30 minutes of the meeting.
3. **Internal classification** after reviewing the notes calmly.

The operator must not rely only on memory several days later.

## Stakeholder profile fields

Every feedback record must capture:

- Stakeholder type: productora, productor ejecutivo, jefe/a de producción, escuela, postproductora, sonido/post, distribuidora, institución, other.
- Role in buying decision: decision maker, influencer, evaluator, user, teacher, technical advisor, unknown.
- Production context: one project, multiple productions, school workflow, post pipeline, archive/library, institutional workflow, unknown.
- Urgency level: high, medium, low, unknown.
- Data sensitivity level: high, medium, low, unknown.
- Demo context: remote call, in-person meeting, internal referral, school meeting, producer meeting, technical review, unknown.

## Core feedback questions

The operator should ask concise questions. The goal is not to interrogate the stakeholder; the goal is to identify whether the pain is real.

### Understanding

- What did you understand this demo is proving today?
- Was the controlled nature of the demo clear?
- Which part felt useful, and which part felt too technical?

### Workflow pain

- Where do you currently lose time with local media folders?
- Who suffers that problem: production, post, sound, direction, school staff, students, or another team?
- How often does the problem happen?
- What happens today when the folder is messy, incomplete, or undocumented?

### Value perception

- What would make this useful in a real working day?
- Which output would be most valuable first: report, verification, metadata overview, transcription, subtitles, sync support, media organization, or another result?
- Would a local-only approach increase trust for your team?

### Trust and boundary

- Does the fact that files do not leave the local environment matter to you?
- What would you need to trust this with real material later?
- What would make you reject it immediately?

### Buying and adoption

- Who would need to approve a test later?
- Who would actually use it day to day?
- What would block adoption even if the tool works technically?
- Would this be evaluated per project, per company, per seat, or as a school/lab tool?

### Objections

- What sounds unclear or risky?
- What feels missing for your use case?
- What would you not want this product to do?
- What must be proven before a real pilot conversation?

## Feedback classification

After the demo, classify the contact using exactly one primary state:

- `EXPLORATORY_ONLY`: stakeholder was curious but no clear pain emerged.
- `PAIN_CONFIRMED`: a real workflow pain was described.
- `TECHNICAL_INTEREST_CONFIRMED`: the stakeholder cares about the technical boundary or local execution chain.
- `COMMERCIAL_INTEREST_CONFIRMED`: the stakeholder asked about pilot, pricing, deployment, seats, or timing.
- `NOT_A_FIT`: the stakeholder needs something outside the current product direction.
- `WAITLIST_CANDIDATE`: interest exists but timing or readiness is not appropriate yet.
- `PILOT_DISCOVERY_CANDIDATE`: stakeholder may be suitable for a later discovery call, not an immediate pilot promise.

## Evidence quality levels

Feedback must be graded by evidence quality:

- `LOW_EVIDENCE`: vague praise, politeness, or general curiosity.
- `MEDIUM_EVIDENCE`: stakeholder named a workflow problem but gave limited detail.
- `HIGH_EVIDENCE`: stakeholder described a concrete recurring workflow, current workaround, owner, cost, risk, or decision path.

Only `HIGH_EVIDENCE` should influence roadmap priority strongly.

## Red flags

The operator must flag the feedback record if any of these appear:

- Stakeholder believes the demo is already the full product.
- Stakeholder assumes real media scanning is already available.
- Stakeholder asks to process confidential material immediately.
- Stakeholder asks for a public promise, date, price, or contractual commitment.
- Stakeholder wants a feature outside the local media agent direction.
- Stakeholder expects cloud upload as the default path.
- Stakeholder requests unsupported production usage.
- Stakeholder asks for a live installation on an uncontrolled machine.

Any red flag requires internal review before a next step.

## Notes structure

A feedback note must follow this structure:

```text
Feedback record ID:
Demo date:
Operator:
Stakeholder type:
Stakeholder role:
Context:
Controlled boundary restated: yes/no
Main pain described:
Current workaround:
Most valuable future output:
Trust/privacy comments:
Adoption path:
Objections:
Red flags:
Evidence quality: LOW_EVIDENCE / MEDIUM_EVIDENCE / HIGH_EVIDENCE
Primary classification:
Recommended next step:
Commitments made: none / list exact wording
Follow-up required: yes/no
Internal reviewer:
```

## Commitments policy

The operator must record any wording that could be interpreted as a commitment.

Allowed wording:

- We are collecting feedback.
- This is not yet the final product.
- This is a controlled local technical demo.
- We are validating whether the workflow pain is real.
- A future pilot would require a separate decision.

Forbidden wording:

- This will be ready for your next production.
- This already works with your real media.
- We can deploy this in your company now.
- Pricing will be this amount.
- The scanner is already finished.
- The product is production-ready.
- We can process confidential material today.

## Recommended next-step model

The feedback record must end with one of these recommendations:

- `NO_FOLLOW_UP`: no clear fit or no useful feedback.
- `SEND_SUMMARY_ONLY`: send a short thank-you and summary, without commercial push.
- `ASK_ONE_FOLLOW_UP_QUESTION`: clarify a missing workflow point.
- `SCHEDULE_PRODUCT_DISCOVERY`: deeper conversation about workflow, not a sales close.
- `HOLD_FOR_LATER`: stakeholder is useful but timing is premature.
- `INTERNAL_REVIEW_REQUIRED`: red flag, expectation risk, or sensitive material issue.

## Internal review criteria

Before acting on the feedback, the reviewer must verify:

- The demo boundary was restated.
- No unsupported product promise was made.
- The main pain is described in operational terms.
- The stakeholder role is clear enough.
- The evidence quality is not inflated.
- Red flags are captured.
- The recommended next step matches the evidence.
- The record does not contain confidential media details.

## What this gate does not authorize

This gate does not authorize:

- A real client pilot.
- A paid pilot.
- A public demo.
- Processing client media.
- Installing on an uncontrolled client machine.
- Product launch claims.
- Pricing offers.
- SaaS integration claims.
- Scanner availability claims.
- Real ffprobe or FFmpeg execution claims.

## Acceptance criteria

This gate is accepted only if the documentation and QA prove that:

- The feedback capture template exists.
- Stakeholder profile fields are defined.
- Core feedback questions are defined.
- Evidence quality levels are defined.
- Feedback classification states are defined.
- Red flags are defined.
- Commitments policy is defined.
- Next-step recommendations are conservative.
- No production, public demo, client media, SaaS, database, installer, scanner, real ffprobe, or real FFmpeg authorization is introduced.

## Closure token

When closed, this gate must emit:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_EXTERNAL_DEMO_FEEDBACK_CAPTURE_GATE_V1_CLOSED`
