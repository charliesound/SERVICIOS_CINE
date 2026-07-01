# CID Local Media Agent — Controlled External Demo Readiness Gate V1

## 1. Purpose

This gate defines the minimum internal readiness required before the controlled local demo runner is shown to one external stakeholder.

It does not authorize a public demo, a production launch, a client deployment, a scanner claim, a media-processing claim, a SaaS claim, or a product-final claim.

The gate exists to prevent improvisation, expectation drift, and accidental overpromising when the current demo is shown outside the internal team.

The approved readiness result is:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_EXTERNAL_DEMO_READINESS_GATE_V1_CLOSED`

## 2. Phase identifier

`CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.EXTERNAL.DEMO.READINESS.GATE.V1`

## 3. Baseline dependency

This gate assumes the previous stable baseline is already closed:

- `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_STAKEHOLDER_DEMO_BRIEF_GATE_V1_CLOSED`
- Expected HEAD before applying this phase: `c92457018da79085127031e3a4720c9e1c6feaa2`
- Expected origin/main before applying this phase: `c92457018da79085127031e3a4720c9e1c6feaa2`

## 4. Scope classification

This phase is documentation and QA only.

Allowed scope:

- controlled external demo readiness criteria;
- external stakeholder suitability checklist;
- safe opening statement;
- safe closing statement;
- non-negotiable limits;
- feedback capture protocol;
- stop/no-show conditions;
- QA test asserting the contract of this document.

Forbidden scope:

- runtime changes;
- pyproject changes;
- command changes;
- scanner changes;
- ffprobe or FFmpeg invocation changes;
- real media material;
- real client material;
- SaaS changes;
- database changes;
- installer changes;
- backend changes;
- frontend changes;
- network behavior changes;
- license or payment behavior;
- product-launch authorization.

## 5. Demo status authorized by this gate

The demo may be described only as:

> A controlled technical local demo that proves the installed runner can execute a deterministic internal fixture, return verifiable JSON evidence, preserve or clean its temporary output according to the selected mode, and produce a stable controlled artifact.

The demo must not be described as:

- a finished product;
- a public demo;
- a production workflow;
- a client-ready ingest system;
- a real scanner;
- a real ffprobe or FFmpeg analysis workflow;
- a real transcription workflow;
- a media sync engine;
- a subtitle pipeline;
- a DaVinci Resolve workflow;
- a cloud system;
- a SaaS module;
- a paid release;
- an installer-ready application.

## 6. External stakeholder eligibility

The demo may be shown only to a selected external person or small external group when all of these conditions are true:

1. The person understands they are seeing a controlled technical demo, not a final product.
2. The meeting has a defined commercial or product-learning purpose.
3. The operator can explain the boundaries without weakening them.
4. The operator can stop the demo if the preflight or evidence check fails.
5. The recipient is not expecting to process real material during this meeting.
6. The recipient is not being asked to pay based on this demo alone.
7. The recipient is not being promised delivery dates, pricing, installer availability, or real-media features.
8. The operator has the runbook, failure recovery guide, acceptance checklist, and stakeholder brief available.
9. The operator has verified the current baseline before the meeting.
10. The operator has a structured feedback form or notes template ready.

## 7. External stakeholder profiles allowed for controlled showing

The following profiles are eligible for a controlled showing if the acceptance checklist passes:

- producer;
- executive producer managing several productions;
- head of production;
- production manager;
- film school decision-maker;
- postproduction supervisor;
- sound/post professional;
- institutional audiovisual contact;
- distribution or exhibition stakeholder evaluating operational value.

The following contexts are not authorized by this gate:

- public event;
- sales webinar;
- paid client onboarding;
- product announcement;
- press demonstration;
- investor demo using inflated claims;
- live processing of stakeholder files;
- demo with confidential client material;
- demo requiring network access;
- demo requiring installation on the stakeholder machine.

## 8. Mandatory pre-demo checklist

Before showing the demo externally, the operator must confirm:

- repo is on the expected stable commit or a later approved stable commit;
- worktree is clean;
- target tag for the current gate is absent before closure;
- `.venv` is activated;
- `cid-local-media-agent-controlled-local-demo-runner --help` works;
- `cid-local-media-agent-controlled-local-demo-runner --result-json` works;
- `cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output` works;
- JSON evidence contains the expected controlled result;
- controlled artifact name is `controlled_visible_report.controlled.txt`;
- controlled artifact SHA256 is `277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f`;
- controlled artifact byte size is `167`;
- default cleanup removes temporary output;
- preserved output can be manually cleaned;
- no repo write occurs during the runner smoke;
- no real media material is introduced;
- no external client path is introduced;
- no network dependency is introduced;
- no database or SaaS dependency is introduced;
- the operator has the failure modes recovery document open;
- the operator has the stakeholder demo brief open.

## 9. Safe opening statement

The operator should open the external demo with a statement equivalent to:

> What I am going to show is a controlled technical demo of the Local Media Agent command chain. It does not process real client material yet. It does not run the final scanner yet. It does not prove the final product. The purpose is to show the direction, the evidence discipline, and how we are building the tool safely before introducing real workflows.

This statement must be made before any command is shown.

## 10. Safe sequence for the external demo

Recommended order:

1. State the controlled nature of the demo.
2. State what is not included yet.
3. Show the command help.
4. Explain that the help proves the installed operator surface exists.
5. Run the JSON evidence mode.
6. Explain the evidence fields.
7. Point to the artifact name.
8. Point to the stable SHA and byte count.
9. Explain deterministic evidence in plain production language: "same controlled input, same controlled output".
10. Run the keep-output mode only if useful.
11. Explain temporary output preservation.
12. Explain cleanup and why it matters.
13. Connect the demo to the stakeholder's workflow pain point.
14. Repeat the limits.
15. Ask for feedback on usefulness, language, risk, and priority.
16. Close without asking for commitment beyond feedback or a future controlled follow-up.

## 11. Safe closing statement

The operator should close with:

> The useful part today is not that this is already the finished product. The useful part is that the local command chain, evidence discipline, and demo boundaries are already controlled. The next product value depends on which real workflow should be prioritized first and which risks must be solved before real material is introduced.

## 12. What the operator may say

The operator may say:

- "This is a controlled technical demo.";
- "The output is deterministic and evidence-checked.";
- "The current chain is intentionally limited.";
- "This is not processing your files yet.";
- "We are validating the operator workflow before moving into real media workflows.";
- "The next step is to learn which use case is most valuable for your team.";
- "The current demo helps us discuss the product without risking client material.";
- "The final roadmap depends on validation, not assumptions.".

## 13. What the operator must not say

The operator must not say:

- "This is ready for your production.";
- "You can use it next week on a real shoot.";
- "It already scans your media folders.";
- "It already runs full ffprobe or FFmpeg workflows on client material.";
- "It already syncs picture and sound.";
- "It already transcribes your rushes.";
- "It already builds subtitles.";
- "It already integrates with DaVinci Resolve.";
- "It already has installer/licensing ready.";
- "It is already the SaaS product.";
- "Pricing is final.";
- "Delivery date is guaranteed.";
- "We can process your real material now.".

## 14. Stakeholder-specific framing

### 14.1 Producer

Use language around control, risk reduction, repeatability, and avoiding chaos in media intake.

Ask:

- Which part of local media intake creates the most production friction?
- Who currently checks whether files are usable?
- What evidence would make you trust a technical assistant?

Do not lead with command-line details unless the producer asks.

### 14.2 Executive producer with several productions

Use language around multi-project visibility, delegation, and standardized technical evidence.

Ask:

- Across three to five productions, where do you lose control first?
- Would standardized local evidence reports help compare projects?
- Who should receive the report: production, post, sound, DIT, or executive team?

Do not promise multi-project SaaS control from this local demo.

### 14.3 Head of production

Use language around practical coordination, handoff, and preflight discipline.

Ask:

- What would need to be checked before postproduction receives material?
- What report format would actually be read?
- Which warnings should require human approval?

Do not imply automated production decisions.

### 14.4 Film school

Use language around teaching safe workflows, evidence, and local-first discipline.

Ask:

- Would students benefit from seeing what a controlled media preflight means?
- Could this become an educational workflow before becoming a professional workflow?
- Which mistakes do students make most often with camera and sound files?

Do not present it as a complete course product.

### 14.5 Postproduction supervisor

Use language around ingest quality, early detection, and report handoff.

Ask:

- What metadata or file evidence matters before editorial starts?
- What should be flagged before material reaches post?
- What would make this credible rather than noisy?

Do not claim full post pipeline integration.

### 14.6 Sound/post professional

Use language around sync risk, clip evidence, and avoiding ambiguous handoffs.

Ask:

- Which file-level evidence would help sound editorial?
- Which production sound problems should be detected first?
- What would you distrust in an automated assistant?

Do not claim sync, transcription, or subtitle output from this current demo.

### 14.7 Institutional or distribution contact

Use language around controlled process, auditability, and safe adoption.

Ask:

- Would a local-first media evidence workflow reduce operational risk?
- What proof would be needed before institutional use?
- Which legal or privacy boundaries are most important?

Do not imply compliance certification.

## 15. Feedback capture protocol

The operator must capture feedback in five categories:

1. Pain point: what real problem the stakeholder recognized.
2. Value signal: what part of the demo felt useful.
3. Trust signal: what evidence made the demo credible or not credible.
4. Objection: what prevented the stakeholder from seeing immediate value.
5. Priority: which future feature should be validated first.

The operator should avoid asking only: "Did you like it?"

Better questions:

- What part of this would save someone time?
- What part still feels too abstract?
- Which file workflow should be attacked first?
- Who in your team would care about this report?
- What would make this unacceptable in a real production context?
- What should not be automated?
- Which evidence would you need before trusting it?

## 16. No-show conditions

The operator must not show the demo externally if any of these conditions are true:

- worktree is dirty before the demo;
- installed runner command is missing;
- `--help` fails;
- `--result-json` fails;
- `--result-json --keep-output` fails;
- SHA does not match the approved controlled value;
- byte count does not match the approved controlled value;
- cleanup is not understood;
- the operator cannot explain the limits clearly;
- the recipient expects real material processing;
- the meeting is framed as a product launch;
- the meeting requires a public claim;
- the operator is under pressure to promise delivery dates;
- the operator is asked to process external files live;
- the operator cannot capture feedback in a structured way.

## 17. Stop conditions during the meeting

If a failure happens during the meeting:

1. Stop the command sequence.
2. Do not improvise a workaround.
3. State that the demo is intentionally gated.
4. Explain that a failed evidence check is a valid reason to stop.
5. Capture what happened.
6. Continue the conversation conceptually only if useful.
7. Do not claim the demo passed.

Recommended wording:

> I am going to stop here because this demo is designed to fail closed. That is intentional. I would rather stop the demonstration than hide an evidence mismatch or create a false impression.

## 18. External follow-up boundary

After a controlled external demo, the operator may propose only one of these next steps:

- a feedback review call;
- a product-discovery conversation;
- a controlled internal next-demo milestone;
- a list of prioritized use cases;
- a non-binding pilot exploration;
- a request for anonymized workflow examples without ingesting real files.

The operator must not propose:

- paid deployment;
- live client processing;
- installer delivery;
- production use;
- guaranteed dates;
- full SaaS onboarding;
- real-media ingestion without a future approved phase.

## 19. Acceptance criteria

This gate passes only if the document and QA assert all of the following:

- phase identifier is present;
- result token is present;
- baseline commit is present;
- documentation/test-only scope is explicit;
- external showing is limited to controlled one-to-one or small-group contexts;
- public demo is forbidden;
- product-final claims are forbidden;
- real material processing is forbidden;
- command sequence remains limited to help, JSON evidence, and keep-output evidence;
- SHA and byte values are present;
- cleanup is covered;
- no-show conditions are present;
- stop conditions are present;
- stakeholder-specific framing is present;
- feedback capture is structured;
- next steps are limited and non-binding.

## 20. Closure statement

When this gate is closed, the current demo chain is ready for a controlled external conversation with a selected stakeholder only if the operator follows the runbook, acceptance checklist, stakeholder brief, and failure recovery rules.

Closure does not authorize public release, product launch, real media processing, SaaS claims, or production deployment.

