# CID Local Media Agent - Internal Demo Second Machine Setup Plan v1

## Phase

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.V1

## Objective

Define the controlled internal setup plan for preparing the current CID Local Media Agent visible report demo on a second internal machine.

This phase creates setup instructions and validation boundaries.

This phase does not execute the setup on a second machine.

This phase does not create an installer.

This phase does not create a commercial package.

This phase does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer.

## Source Stable State

Source stable HEAD:

bccd5c794f8fa293e68964fbf9fbab05533ed6c8

Source commit:

docs: add CID Local Media Agent second machine setup readiness

Source tag:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-readiness-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_READINESS_PASS_READY_FOR_SECOND_MACHINE_SETUP_PLAN

## Current Decisions

The second-machine setup remains:

READY_FOR_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_PLANNING_ONLY

The internal demo remains:

READY_FOR_CONTROLLED_INTERNAL_DEMO_PLANNING_ONLY

The visible report remains:

APTO_CON_RESERVAS_INTERNAL_REVIEW_ONLY

## Setup Plan Decision

The second-machine setup plan is:

CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_PLAN_ONLY

This means setup instructions may be prepared for another internal workstation.

It does not mean the setup has been executed.

It does not mean the setup has passed on another machine.

It does not mean there is a portable installer.

It does not mean there is a client installer.

It does not mean the product is ready for sales or public demonstration.

## Target Machine Profile

Allowed target machine profile:

- project-owner controlled machine
- internal development laptop
- internal review laptop
- clean internal WSL Ubuntu environment
- clean internal Linux environment
- no client data
- no production media
- no confidential project files
- no SaaS credentials
- no copied environment secrets
- no copied local database files

Blocked target machine profile:

- client computer
- productora computer
- school computer
- investor computer
- public demo computer
- sales event computer
- paid pilot computer
- production workstation with real footage
- unmanaged third-party machine
- machine containing confidential client material

## Required Machine Prerequisites

The second internal machine must have:

- Git available
- Python 3 available
- Python virtual environment support available
- shell access available
- local write access to a controlled workspace
- network access only for repository clone and dependency installation
- no need for media hardware
- no need for GPU
- no need for ffprobe
- no need for ffmpeg
- no need for DaVinci Resolve
- no need for Avid
- no need for SaaS credentials
- no need for database credentials

## Controlled Workspace Policy

The workspace on the second machine must be:

- a clean internal folder
- outside any client media folder
- outside any production footage folder
- outside any confidential project folder
- separate from user downloads
- separate from desktop clutter
- dedicated to this controlled internal setup
- disposable after the internal demo
- free of .env files copied from the main machine
- free of database files copied from the main machine

## Setup Command Plan

The future second-machine setup may use this controlled sequence:

1. Create a clean internal workspace.
2. Clone the repository from the project remote.
3. Enter the repository folder.
4. Check that the current branch is main.
5. Check that HEAD matches the approved stable commit or an explicitly approved later commit.
6. Create a local Python virtual environment.
7. Activate the virtual environment.
8. Upgrade pip only inside the virtual environment.
9. Install project dependencies from documented project requirements.
10. Run the approved validation tests.
11. Create or copy only controlled fixture input.
12. Run the visible report CLI only with controlled fixture input.
13. Write output only to a controlled output folder.
14. Open only the generated visible report.
15. State the internal-only disclaimer before showing the report.

## Example Command Shape

The command shape may be documented as:

- mkdir -p ~/CID_INTERNAL_DEMO_SECOND_MACHINE
- cd ~/CID_INTERNAL_DEMO_SECOND_MACHINE
- git clone <project-remote-url> SERVICIOS_CINE
- cd SERVICIOS_CINE
- git checkout main
- git rev-parse HEAD
- python3 -m venv .venv
- source .venv/bin/activate
- python -m pip install --upgrade pip
- python -m pip install -r requirements.txt
- python -m pytest tests/unit/test_cid_local_media_agent_internal_demo_second_machine_setup_readiness.py -q
- python -m pytest tests/unit/test_cid_local_media_agent_visible_report_internal_demo_readiness.py -q
- python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py -q
- python -m pytest tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py -q
- python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_scanner_result_json> --output-root <controlled_output_root> --print-output-path

This is command-shape documentation only. It is not executed by this phase.

## Required Setup Validation

The future setup must validate:

- repository clone completed
- repository path is controlled
- HEAD is approved
- virtual environment exists
- virtual environment is active
- project dependencies installed inside the virtual environment
- approved test subset passes
- controlled fixture input exists
- output root is controlled
- visible report CLI returns success
- generated visible report exists
- generated visible report is inside the controlled output root
- generated visible report declares client-facing readiness false
- generated visible report declares scanner execution by this renderer false
- generated visible report declares media probing by this renderer false
- generated visible report declares roadmap outputs not generated
- generated visible report includes internal-only disclaimer

## Allowed Demonstration Output

Allowed output:

- generated markdown visible report
- terminal output showing test pass results
- terminal output showing generated report path
- internal setup notes
- internal demo checklist
- internal-only disclaimer

Blocked output:

- real media analysis
- real scanner result from client material
- ffprobe metadata from real media
- ffmpeg output
- synchronized audio
- transcription
- subtitles
- translated subtitles
- timeline export
- SaaS upload result
- database records
- installer package
- license activation evidence
- public demo material
- sales deck claim

## Required Presenter Language

The presenter must say:

This is a controlled internal second-machine setup plan.

This is not a finished installation.

This is not a commercial installer.

This is not a client installer.

This is not a public demo.

This is not a sales demo.

This uses controlled fixture input only.

This does not scan real media.

This does not execute ffprobe.

This does not execute ffmpeg.

This does not sync audio.

This does not transcribe.

This does not generate subtitles.

This does not export timelines.

This does not upload to SaaS.

This does not write to a database.

## Stop Conditions

The setup plan must stop if:

- a client machine is proposed
- a school machine is proposed
- a productora machine is proposed
- public demo use is proposed
- sales demo use is proposed
- paid pilot use is proposed
- product distribution is proposed
- installer creation is requested
- installer signing is requested
- license activation is requested
- real media is requested
- production footage is requested
- confidential script material is requested
- scanner execution is requested
- ffprobe execution is requested
- ffmpeg execution is requested
- sync output is requested
- transcription output is requested
- subtitle output is requested
- timeline export is requested
- SaaS upload is requested
- database write is requested

## Installation Boundary

This plan is not an installation record.

A later phase must be created before any actual second-machine setup execution.

The actual setup execution phase must capture:

- machine type
- operating system
- workspace path
- repository clone status
- HEAD validation
- virtual environment status
- dependency install status
- test results
- visible report generation result
- output path
- boundary compliance result

## Next Safe Phase

The next safe phase may be:

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.QA.GATE.V1

That phase may validate this plan.

After that, a separate execution phase may be created.

No execution is authorized by this plan alone.

## Validation Evidence Required

This setup plan phase is accepted only with:

- second machine setup plan test passing
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

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_PLAN_PASS_READY_FOR_SECOND_MACHINE_SETUP_PLAN_QA_GATE
