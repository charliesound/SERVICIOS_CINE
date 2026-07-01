# CID Local Media Agent — Controlled Local Demo Runner External Demo Follow-up Decision Gate V1

## Gate identity

- Gate: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.EXTERNAL.DEMO.FOLLOWUP.DECISION.GATE.V1`
- Expected result token: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_EXTERNAL_DEMO_FOLLOWUP_DECISION_GATE_V1_CLOSED`
- Product area: CID Local Media Agent
- Scope class: documentation and QA only
- Intended use: internal controlled decision framework after a controlled external demo
- Status target: controlled follow-up decision readiness, not product launch readiness

## Purpose

This gate defines how to decide the next step after a controlled external demo of the local demo runner has been shown and feedback has been captured.

The goal is to avoid emotional or opportunistic follow-up decisions. The operator must not jump from a positive reaction to a pilot, commercial promise, implementation change, or product commitment without evidence.

The decision must classify the contact into one of five conservative outcomes:

1. Future controlled pilot candidate.
2. Second controlled demo candidate.
3. Hold until real scanner capability exists.
4. Commercial conversation candidate.
5. Low-fit or no-follow-up candidate.

This gate does not authorize a pilot, customer installation, real media processing, external deployment, pricing commitment, contract, SaaS activation, or production use.

## Mandatory baseline before applying this gate

The following internal chain must already be closed:

1. Installed export command.
2. Installed controlled local demo runner.
3. Operator evidence pack.
4. Demo narrative gate.
5. Operator runbook gate.
6. Failure modes and recovery gate.
7. Demo acceptance checklist gate.
8. Stakeholder demo brief gate.
9. Controlled external demo readiness gate.
10. External demo feedback capture gate.

This gate only starts after a controlled external demo has been run under the accepted boundaries and the feedback capture has been completed.

## Non-negotiable boundaries

The follow-up decision must preserve the current controlled-demo boundary:

- No production claim.
- No public demo claim.
- No final product claim.
- No real client media processing.
- No scanner execution claim.
- No ffprobe or FFmpeg execution claim.
- No SaaS integration claim.
- No database access claim.
- No installer claim.
- No automatic workflow claim.
- No external deployment commitment.
- No pricing commitment.
- No delivery date commitment.
- No pilot commitment without a separate future gate.

The correct phrase is:

> This was a controlled technical demonstration. The next step must be selected based on evidence, risk, and fit, not on enthusiasm alone.

## Required feedback inputs

The decision must be based on captured feedback, not memory alone. At minimum, the operator must have notes for:

1. Stakeholder profile.
2. Production context.
3. Operational pain expressed by the stakeholder.
4. What part of the demo they understood quickly.
5. What part caused confusion.
6. Objections raised.
7. Questions asked.
8. Strength of interest.
9. Urgency.
10. Budget or buying-process signal, if voluntarily disclosed.
11. Technical-risk concern.
12. Privacy or local-only concern.
13. Expected next step proposed by the stakeholder.
14. Operator judgement after reflection.

If these inputs are missing, the only allowed decision is `INSUFFICIENT_FEEDBACK_REQUIRES_INTERNAL_REVIEW`.

## Decision outcome 1 — Future controlled pilot candidate

Use this outcome only when the stakeholder shows strong fit, understands the controlled nature of the demo, and has a concrete use case that can later be evaluated safely.

Required evidence:

- The stakeholder describes a real workflow pain without being prompted too heavily.
- The workflow is relevant to media ingest, local organisation, technical reporting, post-production preparation, or production oversight.
- The stakeholder accepts that the current demo is not processing real media.
- The stakeholder is willing to define controlled sample material later under a separate future agreement.
- The stakeholder does not require immediate production use.
- The stakeholder accepts a staged path: internal demo now, controlled pilot later, product decision later.

Allowed next action:

- Prepare a future pilot scoping discussion.
- Capture pilot risks.
- Define what evidence would be needed before touching any real media.

Forbidden next action:

- Accept real files immediately.
- Promise a delivery date.
- Promise automatic sync, transcription, ingest, or scanner behavior.
- Commit to production rollout.

Recommended wording:

> There seems to be a good fit, but the next step is not a production pilot yet. The next step would be a separate controlled pilot-scope discussion where we define boundaries, material policy, evidence, and what must be true before any real content is touched.

## Decision outcome 2 — Second controlled demo candidate

Use this outcome when the stakeholder is interested but did not fully understand the technical boundary, the product direction, or the operational value.

Required evidence:

- Interest is present but unfocused.
- The stakeholder asks for clarifications that should be resolved before any deeper commitment.
- The stakeholder needs another person present, such as a producer, head of production, post supervisor, DIT, sound post lead, or school coordinator.
- The operator detects confusion between demo runner, final product, scanner, SaaS, and future roadmap.

Allowed next action:

- Schedule a second controlled explanation.
- Adapt the stakeholder brief.
- Bring the right decision maker or technical user.
- Use the same controlled demo boundaries.

Forbidden next action:

- Treat interest as validation.
- Move to pricing or pilot design.
- Expand scope to impress the stakeholder.

Recommended wording:

> Before discussing a pilot or commercial step, it would be better to do a second controlled walkthrough with the right people in the room, so expectations stay aligned.

## Decision outcome 3 — Hold until real scanner capability exists

Use this outcome when the stakeholder is only interested in capabilities that are explicitly not present in the controlled demo.

Typical signals:

- They mainly ask for real folder scanning.
- They mainly ask for real media metadata extraction.
- They mainly ask for ffprobe or FFmpeg execution.
- They mainly ask for waveform sync, transcription, subtitles, or DaVinci/Avid workflow.
- They require real material processing before they can evaluate value.

Allowed next action:

- Mark the contact as relevant for future scanner-readiness follow-up.
- Record which real capability matters most.
- Do not schedule a pilot yet.

Forbidden next action:

- Pretend the controlled runner proves scanner readiness.
- Let them provide files now.
- Promise that the next build will include their requested capability.

Recommended wording:

> Your main interest is in functionality that is intentionally outside this controlled demo. I will keep this feedback for the real scanner roadmap, but I should not present the current demo as proof of that capability.

## Decision outcome 4 — Commercial conversation candidate

Use this outcome only when there is buying-context evidence, not just enthusiasm.

Required evidence:

- The stakeholder has a plausible buying role or direct access to one.
- The problem maps to a budgeted operational pain.
- They ask about adoption, team workflow, deployment, licensing, risk, privacy, or procurement.
- They understand that price, packaging, and pilot conditions are not being committed in the demo.
- They accept a staged commercial conversation separate from product execution.

Allowed next action:

- Prepare a commercial-discovery conversation.
- Ask about decision process.
- Ask about current cost of the pain.
- Ask what must be proven before a paid pilot or subscription can be discussed.

Forbidden next action:

- Quote pricing.
- Offer discounts.
- Promise exclusive access.
- Create artificial urgency.
- Call the controlled demo a finished product.

Recommended wording:

> It sounds like there may be a real operational and commercial question here. I would separate that from the technical demo and schedule a discovery conversation about workflow, risk, buying process, and what evidence would be needed before discussing commercial terms.

## Decision outcome 5 — Low-fit or no-follow-up candidate

Use this outcome when the stakeholder does not have a relevant pain, does not understand the boundary, asks for unavailable functionality only, or creates risk of expectation mismatch.

Typical signals:

- They want a finished tool immediately.
- They want public demo access.
- They want to upload or hand over real files now.
- They insist on capabilities that are not present.
- They dismiss local-only safety or controlled gates as unnecessary.
- They cannot identify a concrete workflow pain.
- They are curious but not operationally relevant.

Allowed next action:

- Thank them.
- Record the reason for low fit.
- Do not schedule next steps unless a new use case emerges.

Forbidden next action:

- Continue pursuing the contact due to politeness.
- Offer development promises to keep interest alive.
- Blur controlled-demo boundaries.

Recommended wording:

> At this stage I do not think this controlled demo maps strongly enough to your current workflow. I will keep the feedback, but I do not want to overstate what this version does.

## Decision matrix

| Signal | Future pilot | Second demo | Hold for scanner | Commercial discovery | Low fit |
|---|---:|---:|---:|---:|---:|
| Clear operational pain | Strong | Medium | Medium | Strong | Weak |
| Understands controlled boundary | Required | Weak or partial | Required | Required | Often weak |
| Wants unavailable real capability | Weak | Medium | Strong | Medium | Medium |
| Has buying context | Medium | Weak | Medium | Strong | Weak |
| Needs more people present | Medium | Strong | Medium | Medium | Weak |
| Pushes for files now | Stop | Stop | Stop | Stop | Strong risk |
| Wants final product now | Stop | Stop | Stop | Stop | Strong risk |
| Feedback is vague | Weak | Medium | Weak | Weak | Medium |

`Stop` means the operator must not advance without internal review.

## Required follow-up record

After each controlled external demo, the operator must create an internal follow-up record with:

- Demo date.
- Stakeholder category.
- Stakeholder role, if safe to record.
- Context of the conversation.
- Pain statement.
- Most relevant demo moment.
- Main objection.
- Main confusion.
- Buying-context signal.
- Technical-readiness signal.
- Privacy/local-only signal.
- Decision outcome.
- Reason for outcome.
- Forbidden actions explicitly avoided.
- Proposed next step.
- Owner.
- Review date.

The record must not include confidential client material, real media paths, private script content, production secrets, credentials, or files.

## Decision tokens

The follow-up record must use one of these tokens:

- `FOLLOWUP_DECISION_FUTURE_CONTROLLED_PILOT_CANDIDATE`
- `FOLLOWUP_DECISION_SECOND_CONTROLLED_DEMO_CANDIDATE`
- `FOLLOWUP_DECISION_HOLD_UNTIL_REAL_SCANNER_CAPABILITY`
- `FOLLOWUP_DECISION_COMMERCIAL_DISCOVERY_CANDIDATE`
- `FOLLOWUP_DECISION_LOW_FIT_NO_FOLLOWUP`
- `FOLLOWUP_DECISION_INSUFFICIENT_FEEDBACK_REQUIRES_INTERNAL_REVIEW`

No other decision token is allowed for this gate.

## Red flags requiring stop

The operator must stop and escalate internally if any of the following occur:

- The stakeholder asks to process real material immediately.
- The stakeholder believes this is production-ready.
- The stakeholder asks for a public download.
- The stakeholder asks for installer access.
- The stakeholder asks for a firm delivery date.
- The stakeholder asks for a price before value and scope are understood.
- The stakeholder wants the tool integrated into an active production now.
- The operator feels pressure to overstate the current capability.
- The feedback record is incomplete.

## Allowed output of this gate

This gate may produce only:

- A decision classification.
- A conservative next-step recommendation.
- A list of risks.
- A list of missing evidence.
- A future-gate recommendation.

This gate must not produce:

- Product roadmap commitment.
- Pilot agreement.
- Installation instruction for external users.
- Real media intake instruction.
- Commercial pricing.
- Legal terms.
- Public launch statement.

## Acceptance criteria

This gate is accepted when the documentation and QA prove that:

1. The five main follow-up outcomes are present.
2. The insufficient-feedback outcome is present.
3. Each outcome has allowed and forbidden next actions.
4. Stop conditions are explicit.
5. Decision tokens are fixed.
6. Real media, public demo, installer, scanner, ffprobe, FFmpeg, SaaS, and database commitments remain forbidden.
7. The follow-up record avoids confidential or production-sensitive material.
8. The result token is present.
9. Scope remains documentation and QA only.
10. Existing controlled demo gates remain compatible.

## Closure statement

If this gate closes, the correct closure statement is:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_EXTERNAL_DEMO_FOLLOWUP_DECISION_GATE_V1_CLOSED`

This means the project has a conservative decision framework for what to do after a controlled external demo and captured feedback.

It does not mean that a pilot is authorized, that a commercial offer is ready, or that the Local Media Agent is production-ready.
