# CID Local Media Agent - Internal Demo Second Machine Setup Readiness v1

## Phase

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.READINESS.V1

## Objective

Prepare a safe readiness plan for setting up the current controlled internal demo on a second internal machine.

This phase does not perform the second-machine installation.

This phase does not create an installer.

This phase does not create a commercial package.

This phase does not authorize client-facing demo, public demo, sales use, paid pilot use, production use, or installation on a client computer.

## Source Stable State

Source stable HEAD:

9c0f77127b12be387c1421b9e5f5620c8c0a8625

Source commit:

docs: add CID Local Media Agent internal demo readiness

Source tag:

cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-internal-demo-readiness-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_VISIBLE_REPORT_INTERNAL_DEMO_READINESS_PASS_READY_FOR_SECOND_MACHINE_SETUP_READINESS

## Current Decision

The internal demo remains:

READY_FOR_CONTROLLED_INTERNAL_DEMO_PLANNING_ONLY

The visible report remains:

APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY

## Second Machine Readiness Decision

The second-machine setup is:

READY_FOR_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_PLANNING_ONLY

This means the next activity may prepare a controlled internal setup plan for another internal workstation.

It does not mean installation has been tested.

It does not mean the demo is portable.

It does not mean there is a finished installer.

It does not mean a client may receive the software.

## Allowed Target Machine

The target machine may be only:

- a machine owned or controlled by the project owner
- an internal development workstation
- an internal review workstation
- a controlled laptop used only for internal demo preparation
- a clean internal WSL environment
- a clean internal Linux environment

## Blocked Target Machine

The target machine must not be:

- client computer
- productora computer
- school computer
- external producer computer
- investor computer
- sales event machine
- public demo machine
- production workstation with real media
- paid pilot machine
- unmanaged third-party machine

## Allowed Setup Purpose

The setup may be prepared only to validate:

- repository clone feasibility
- virtual environment creation
- dependency installation readiness
- controlled test execution
- controlled fixture availability
- direct CLI execution with controlled input
- visible report generation from controlled input
- local-only boundary messaging
- internal demo script consistency
- no real media dependency
- no network upload requirement
- no database write requirement

## Blocked Setup Purpose

The setup must not validate or claim:

- commercial installer readiness
- client installation readiness
- product distribution readiness
- public demo readiness
- sales demo readiness
- paid pilot readiness
- real scanner readiness
- real media processing readiness
- media probing readiness
- ffprobe execution readiness
- ffmpeg execution readiness
- sync readiness
- transcription readiness
- subtitle readiness
- timeline export readiness
- SaaS integration readiness
- license activation readiness

## Required Second-Machine Setup Boundaries

Any future second-machine setup must preserve:

- no real client files
- no production media
- no uncontrolled media folders
- no external uploads
- no database writes
- no SaaS connection
- no secret files copied
- no environment files copied
- no local database files copied
- no private client data copied
- no claim that this is an installer
- no claim that this is product-ready

## Allowed Setup Inputs

Allowed inputs:

- repository checkout
- project source files
- controlled fixture JSON
- controlled visible report output folder
- Python virtual environment
- documented setup commands
- internal demo script
- internal disclaimer text

## Blocked Setup Inputs

Blocked inputs:

- real client media
- production footage
- original camera files
- original sound files
- confidential script material
- private project data
- secret environment files
- local database files
- SaaS credentials
- license keys
- third-party customer data

## Required Setup Verification

A future second-machine setup must verify:

- repository path is controlled
- Python environment is isolated
- dependencies are installed from documented project requirements
- CLI help or direct execution works
- controlled fixture can generate a visible report
- generated report stays inside a controlled output folder
- generated report states client-facing readiness is false
- generated report states scanner execution by this renderer is false
- generated report states media probing by this renderer is false
- generated report states roadmap outputs are not generated
- local-only privacy language is visible
- internal-only disclaimer is visible

## Required Presenter Language

If shown internally on a second machine, the presenter must say:

This is a controlled internal second-machine setup plan.

This is not a commercial installer.

This is not a client installation.

This is not a finished product package.

This is not a public demo.

This is not a sales demo.

This does not scan real media.

This does not execute media probing tools.

This does not execute ffprobe.

This does not execute ffmpeg.

This does not sync audio.

This does not transcribe.

This does not generate subtitles.

This does not export timelines.

This does not upload to SaaS.

This does not write to a database.

## Stop Conditions

The setup must stop if:

- a client machine is proposed
- public demo use is proposed
- commercial installation is proposed
- product distribution is proposed
- real media is requested
- production footage is requested
- scanner execution is requested
- media probing execution is requested
- ffprobe or ffmpeg execution is requested
- sync output is requested
- transcription output is requested
- subtitle output is requested
- timeline export is requested
- SaaS upload is requested
- database write is requested
- license activation is requested
- installer signing is requested

## What This Phase Allows Next

This phase may allow a future phase to prepare:

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.V1

That future phase may create setup instructions for a controlled internal machine.

It must not create an installer.

It must not execute installation on a client machine.

It must not package the product for distribution.

It must not add real media capabilities.

## Validation Evidence Required

This readiness phase is accepted only with:

- second machine setup readiness test passing
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

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_READINESS_PASS_READY_FOR_SECOND_MACHINE_SETUP_PLAN
