# CID Local Media Agent — Controlled Local Demo Runner Stakeholder Demo Brief Gate V1

## Gate identity

- Gate name: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.STAKEHOLDER.DEMO.BRIEF.GATE.V1`
- Expected closure result: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_STAKEHOLDER_DEMO_BRIEF_GATE_V1_CLOSED`
- Product line: `CID Local Media Agent`
- Demo status: controlled technical demo only
- Audience status: internal preparation for controlled external conversations
- Implementation status: documentation and QA only
- Baseline expectation: the previous controlled local demo runner acceptance checklist gate is already closed

## Purpose

This gate converts the controlled local demo runner from a technical proof into a stakeholder-specific conversation brief. The goal is not to expand functionality. The goal is to help an operator explain the same controlled demo differently depending on who is in the room, while keeping the same truthful boundaries.

The brief exists to answer five questions before any controlled stakeholder conversation:

1. Who is the stakeholder?
2. Which pain point can they understand quickly?
3. Which part of the controlled demo should be shown first?
4. Which claims must be avoided?
5. Which feedback should be captured after the conversation?

## Non-goals

This gate does not create, modify, or approve:

- runtime code;
- package entrypoints;
- project configuration;
- scanner behavior;
- media analysis behavior;
- real media processing;
- production demo assets;
- installer behavior;
- backend services;
- frontend screens;
- SaaS integration;
- payment, credit, ledger, or AI job behavior;
- deployment configuration;
- public marketing copy.

This gate also does not authorize real client material, public claims, performance claims, release claims, roadmap guarantees, or production-readiness claims.

## Universal demo framing

Every stakeholder conversation must start from the same controlled framing:

> This is a controlled local technical demo of one narrow slice of the future CID Local Media Agent workflow. It demonstrates an installed command, a controlled runner, deterministic report artifact evidence, cleanup behavior, and operator discipline. It is not yet the full product, it is not a scanner, and it is not processing real client footage.

The operator may say:

- the current demo proves that the controlled local runner can be executed reproducibly;
- the demo produces a deterministic controlled artifact;
- the artifact has stable bytes and digest evidence;
- the default behavior cleans the temporary output;
- the preserved-output path can be inspected and manually cleaned;
- the demo has a runbook, acceptance checklist, and failure recovery rules;
- the next feedback target is business usefulness and workflow fit, not production deployment.

The operator must not say:

- that the full product is finished;
- that real camera files are being scanned;
- that real metadata extraction is active in this demo;
- that real video or audio analysis is happening in this demo;
- that syncing, transcription, subtitling, translation, editing, delivery, or media indexing are already available in this demo;
- that the demo is ready for unattended client use;
- that a date, price, installation model, or feature scope is final;
- that CID SaaS is required for this local controlled demo;
- that the demo is a public launch.

## Stakeholder profiles

### 1. Producer

Primary concern:

- reducing chaos across projects;
- knowing what material exists;
- avoiding hidden postproduction surprises;
- gaining operational control without forcing the team to upload sensitive assets.

Recommended opening:

> I want to show a controlled local demo of how CID Local Media Agent is being built around traceable, local-first handling of media evidence. This is not the final media scanner yet; it is the controlled execution and reporting spine that will support later product modules.

Show first:

1. Explain the local-only premise.
2. Show `--help` to prove the command is installed and inspectable.
3. Run `--result-json` to show structured deterministic evidence.
4. Explain the stable artifact, bytes, and digest.
5. Explain that cleanup is automatic by default.

Useful question to ask:

> In your current productions, where does media visibility break first: set, DIT, post, production office, or delivery?

Likely objection:

> This is still very technical.

Answer:

> Correct. Today I am not selling a finished product. I am validating whether the operational spine solves a real production control problem before expanding the media functions.

Do not emphasize:

- command-line detail;
- internal test names;
- engineering phase vocabulary;
- low-level artifact mechanics beyond proof of traceability.

### 2. Executive producer managing multiple productions

Primary concern:

- portfolio visibility;
- comparing productions without micromanaging each crew;
- risk, delays, missing media, and reporting discipline;
- whether a tool can scale across several simultaneous projects.

Recommended opening:

> The long-term value is not one folder report. It is a local-first control layer that can eventually give each production a consistent evidence trail without centralizing the media itself.

Show first:

1. Explain why the demo is intentionally narrow.
2. Show the structured JSON as future evidence format.
3. Explain the acceptance checklist as governance discipline.
4. Explain failure recovery as risk control.
5. Explain that each production can be evaluated with the same operational language later.

Useful question to ask:

> If you had three productions running at once, what would you want to know every Friday without asking each jefe de producción manually?

Likely objection:

> How would this work across several productions?

Answer:

> This demo does not implement multi-production control yet. It validates the local evidence and operator discipline that would be required before scaling to several productions.

Do not promise:

- centralized dashboard;
- multi-tenant production control;
- automatic cross-project comparison;
- SaaS synchronization;
- final reporting formats.

### 3. Jefe/a de producción

Primary concern:

- fewer surprises;
- clear handoff between departments;
- less manual checking;
- fewer phone calls about missing files or unclear media state;
- practical workflow, not abstract technology.

Recommended opening:

> This demo is about discipline: can a local tool generate controlled evidence, clean up after itself, and give a predictable result before we add heavier media functions?

Show first:

1. Show the runbook logic.
2. Run the demo using `--result-json`.
3. Explain the artifact name and digest only as audit evidence.
4. Show the default cleanup behavior.
5. Mention the failure recovery gate.

Useful question to ask:

> What is the most annoying media handoff problem you see between rodaje, producción, DIT, montaje, and post?

Likely objection:

> I need this with real folders and real files.

Answer:

> That is exactly the direction, but this gate is deliberately before real material. The current step proves controlled execution; the next product steps must earn real-folder capability safely.

Do not emphasize:

- product vision too early;
- advanced AI features;
- promotional language;
- investor-style claims.

### 4. Film school or training center

Primary concern:

- teaching professional discipline;
- showing students how evidence, traceability, and workflow control matter;
- demonstrating local-first AI/tooling without exposing student material;
- avoiding hype.

Recommended opening:

> This is a useful teaching demo because it separates product truth from product ambition. Students can see what a controlled technical demo proves and what it does not prove yet.

Show first:

1. Show `--help` as inspectability.
2. Show `--result-json` as structured evidence.
3. Explain stable bytes and digest as reproducibility.
4. Show cleanup behavior as operator responsibility.
5. Explain the list of non-promises.

Useful question to ask:

> Would it be valuable for students to learn how production tools should prove behavior before being trusted on real media?

Likely objection:

> Students will want something visual.

Answer:

> Yes. This controlled demo is not the visual product layer. It is the engineering and production-discipline layer that should exist before the visual layer.

Do not promise:

- classroom-ready installer;
- finished UI;
- student accounts;
- curriculum package;
- real footage exercises.

### 5. Postproduction company

Primary concern:

- ingest discipline;
- metadata reliability;
- reducing messy deliveries;
- avoiding manual triage;
- trustable evidence before media enters post.

Recommended opening:

> This is not the ingest scanner yet. It is the local controlled report and evidence discipline that a future ingest-facing agent would need before touching real client files.

Show first:

1. Explain artifact determinism.
2. Show `--result-json`.
3. Explain digest and byte count.
4. Explain no overwrite and cleanup boundaries.
5. Ask where incoming media breaks their process.

Useful question to ask:

> When a production sends you material, what is the first missing or unreliable piece of information?

Likely objection:

> We need support for real codecs, folder structures, audio, and camera metadata.

Answer:

> Agreed. This demo does not claim that yet. It establishes the controlled execution and evidence contract before real media analysis is introduced.

Do not promise:

- codec coverage;
- audio sync;
- NLE integration;
- automated conform;
- final ingest report formats.

### 6. Sound department or post sound team

Primary concern:

- audio file organization;
- sync problems;
- wild tracks;
- slate, take, channel, and scene confusion;
- communication with editorial and production.

Recommended opening:

> For sound, the long-term interest is clear: local evidence around what files exist and how they may relate. But this demo is earlier than that; it proves the controlled local reporting path first.

Show first:

1. Explain local-first privacy.
2. Show the deterministic artifact.
3. Explain why the demo is not yet analyzing audio files.
4. Ask where sound handoff becomes painful.
5. Frame future validation around real workflow cases, not feature promises.

Useful question to ask:

> In your experience, what causes the worst audio handoff problems: naming, metadata, timecode, slate notes, missing files, or unclear editorial communication?

Likely objection:

> Can it sync audio and picture?

Answer:

> Not in this controlled demo. Sync is a future product area. Today the demo only proves controlled local execution and evidence generation.

Do not promise:

- waveform sync;
- timecode sync;
- clap detection;
- transcription;
- speaker detection;
- subtitle generation.

### 7. Distributor, exhibitor, or institutional stakeholder

Primary concern:

- delivery reliability;
- traceability;
- compliance discipline;
- reducing last-minute delivery uncertainty;
- understanding whether the project can become a professional tool.

Recommended opening:

> This is an early controlled technical layer, not a delivery product. Its relevance is that professional delivery depends on traceable evidence, repeatable operations, and clear boundaries.

Show first:

1. Explain the acceptance checklist.
2. Explain failure modes and stop conditions.
3. Show JSON output as controlled evidence.
4. Explain no real media and no delivery claims.
5. Ask what evidence they typically need before trusting a delivery process.

Useful question to ask:

> What recurring delivery uncertainty would you want a production tool to detect earlier?

Likely objection:

> This is not yet useful for delivery.

Answer:

> Correct. It is not a delivery module. It is the controlled evidence approach that future delivery-facing modules would need.

Do not promise:

- DCP checks;
- platform delivery validation;
- broadcaster compliance;
- automated QC;
- legal delivery readiness.

## Demo order by stakeholder type

| Stakeholder | Start with | Show second | Avoid leading with |
|---|---|---|---|
| Producer | local-first control | JSON evidence | command internals |
| Executive producer | portfolio risk language | acceptance checklist | single-file mechanics |
| Jefe/a de producción | practical handoff pain | cleanup and failure recovery | AI feature vision |
| Film school | teaching discipline | digest and reproducibility | commercial pitch |
| Postproduction | ingest discipline | artifact determinism | unfinished codec claims |
| Sound team | handoff pain | controlled evidence | sync promises |
| Distributor/institution | traceability | stop conditions | delivery product claims |

## Universal feedback capture

After any controlled conversation, capture answers to these questions:

1. Stakeholder type.
2. Their strongest pain point.
3. Which part of the demo they understood fastest.
4. Which part created confusion.
5. Which missing feature they asked for first.
6. Whether they accepted the controlled-demo boundary.
7. Whether they saw value despite the current narrow scope.
8. What proof they would need before a second meeting.
9. Whether they are willing to provide non-sensitive workflow examples.
10. Whether they are a future buyer, tester, advisor, or only a general observer.

## Stop conditions during stakeholder conversations

The operator must stop or reframe the demo if:

- the stakeholder assumes the tool is already a finished product;
- the stakeholder asks to test real client material during the conversation;
- the stakeholder asks for production installation;
- the stakeholder asks for pricing or delivery commitments as if fixed;
- the stakeholder asks for features outside the controlled demo;
- the operator cannot explain a failure without speculation;
- the demo output does not match expected controlled evidence;
- the stakeholder conversation starts shifting into public marketing claims.

Recommended stop phrase:

> I want to keep this precise. This demo is only validating the controlled local execution and evidence layer. The real product modules must be validated in later gates before I can claim them.

## Approved next-step asks

The operator may ask for:

- feedback on workflow pain;
- examples of non-sensitive folder chaos;
- priority ranking of future media functions;
- willingness to see a later controlled real-folder demo;
- willingness to review a product brief;
- willingness to join a private validation conversation;
- permission to follow up with a narrowed use case.

The operator must not ask for:

- real client files;
- confidential scripts;
- protected production documents;
- deployment access;
- payment commitment;
- production usage approval;
- public endorsement;
- public announcement.

## Acceptance checklist for this brief

This brief is accepted only if it:

- defines stakeholder-specific framing;
- includes producer, executive producer, jefe/a de producción, film school, postproduction, sound, and institutional/distribution profiles;
- states what to show first for each profile;
- defines one useful question per profile;
- defines one likely objection and answer per profile;
- lists non-promises clearly;
- keeps the controlled local demo boundary intact;
- includes universal feedback capture;
- includes stop conditions;
- includes approved next-step asks;
- remains documentation-only;
- does not authorize real material;
- does not authorize public demo status;
- does not authorize production readiness claims.

## Closure statement

If this gate closes, CID Local Media Agent gains a stakeholder-specific demo brief for controlled conversations. It improves commercial and production communication discipline without expanding implementation scope.

Expected result token:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_STAKEHOLDER_DEMO_BRIEF_GATE_V1_CLOSED`
