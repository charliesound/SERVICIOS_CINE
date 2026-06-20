# CID Local Media Agent - Controlled Visible Report Internal Demo Readiness v1

## Phase

CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.INTERNAL.DEMO.READINESS.V1

## Objective

Prepare controlled internal demo readiness for the current visible report workflow.

This phase defines what can be shown internally, how it must be shown, and which limits must remain visible.

This phase does not add runtime capabilities.

This phase does not authorize client-facing demo, public demo, sales use, production use, external presentation, installer distribution, or second-machine installation.

## Source Stable State

Source stable HEAD:

7cc4e6b67774291d233b6afe6f17ac20aa80196b

Source commit:

test: add CID Local Media Agent internal demo script QA gate

Source tag:

cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-internal-demo-script-preparation-qa-gate-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_SCRIPT_PREPARATION_QA_GATE_PASS_READY_FOR_INTERNAL_DEMO_READINESS

## Current Decision

The visible report remains:

APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY

## Internal Demo Readiness Decision

The internal demo is:

READY_FOR_CONTROLLED_INTERNAL_DEMO_PLANNING_ONLY

This means the demo may be prepared only for controlled internal review and product planning.

## Allowed Internal Demo Audience

Allowed audience:

- internal product owner
- internal producer reviewer
- internal development reviewer
- internal planning reviewer
- trusted internal technical reviewer

## Blocked Audience

Blocked audience:

- client
- productora
- school
- external producer
- investor
- sales lead
- public audience
- paid pilot user
- production user
- support user

## Allowed Demo Environment

Allowed environment:

- same controlled development machine
- controlled internal workstation
- local-only repository checkout
- controlled fixture input
- controlled output folder
- no real client material
- no production media
- no network upload
- no external service dependency
- no database write requirement

## Blocked Demo Environment

Blocked environment:

- client computer
- public event computer
- sales laptop shown to client
- production workstation with real media
- shared machine with uncontrolled files
- cloud runner
- SaaS environment
- external demo booth
- school classroom machine
- productora machine

## What Can Be Demonstrated

The internal demo may show:

- controlled JSON input
- direct CLI command
- generated visible report path
- producer-readable report structure
- accepted media list from controlled facts
- rejected non-media list from controlled facts
- human-review-required items from controlled facts
- warnings from controlled facts
- local-only privacy boundaries represented in the report
- roadmap modules marked as not generated
- internal demo script boundaries

## What Must Be Said During The Demo

The presenter must say:

This is a controlled internal demo.

This is not a client demo.

This is not product delivery.

This is not an installer.

This is not a second-machine installation test.

This does not scan real media.

This does not run media probing tools.

This does not execute ffprobe.

This does not execute ffmpeg.

This does not sync audio.

This does not transcribe.

This does not generate subtitles.

This does not translate subtitles.

This does not export timelines.

This does not integrate with DaVinci Resolve.

This does not integrate with Avid.

This does not upload to SaaS.

This does not write to a database.

This does not prove commercial readiness.

## Required Demo Steps

The internal demo may follow this controlled sequence:

1. Show the phase and current status.
2. Explain that the input is controlled fixture data.
3. Run or describe the direct CLI command.
4. Open the generated visible report.
5. Walk through the executive summary.
6. Show local-only privacy statements.
7. Show accepted media, rejected non-media, warnings, and human-review items.
8. Show roadmap modules marked as not generated.
9. Close with the internal-only readiness decision.
10. State the next safe technical step.

## Demo Stop Conditions

The internal demo must stop if:

- real client files are requested
- real media folder execution is requested
- scanner execution is requested
- media probing execution is requested
- ffprobe or ffmpeg execution is requested
- sync output is requested
- transcription output is requested
- subtitle output is requested
- timeline export is requested
- SaaS upload is requested
- database write is requested
- client-facing packaging is requested
- installation on external machine is requested

## Required Screen Disclaimer

The demo must keep the following disclaimer visible or stated:

Internal controlled demo only. This is not client-facing, not production-ready, and not a finished Local Media Agent product. It renders controlled scanner-result data into a visible report and does not process real media.

## Producer Readiness Interpretation

The internal demo is useful because it demonstrates the communication layer of CID Local Media Agent:

- how the system can explain folder status to a producer
- how local-only privacy boundaries can be made visible
- how warnings and human-review items can be surfaced
- how unavailable roadmap capabilities can be explicitly marked as not generated

The internal demo is not sufficient for customer validation because it does not yet include real scanning, real media probing, real synchronization, real transcription, real subtitle creation, real timeline export, installer packaging, license management, or external deployment controls.

## Next Safe Phase

The next safe phase may be:

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.READINESS.V1

That next phase may only prepare a second-machine internal setup plan.

It must not create a commercial installer.

It must not authorize client installation.

It must not authorize public demo use.

It must not authorize paid pilot use.

## Validation Evidence Required

This readiness phase is accepted only with:

- internal demo readiness test passing
- internal demo script preparation QA gate test passing
- internal demo script preparation test passing
- controlled visible report review execution QA gate test passing
- controlled visible report review execution test passing
- controlled visible report review readiness test passing
- controlled CLI execution QA gate test passing
- controlled CLI execution record test passing
- CLI test passing
- CLI implementation QA gate passing
- runtime generator test passing
- controlled runtime implementation QA gate passing
- supporting implemented runtime chain tests passing
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing

## Acceptance Result

LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_READINESS_PASS_READY_FOR_SECOND_MACHINE_SETUP_READINESS
