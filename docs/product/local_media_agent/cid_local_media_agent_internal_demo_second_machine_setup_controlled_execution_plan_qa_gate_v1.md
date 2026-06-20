# CID Local Media Agent - Internal Demo Second Machine Setup Controlled Execution Plan QA Gate v1

## Phase

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.QA.GATE.V1

## Objective

Validate the exact command plan for one future controlled internal second-machine setup execution.

This QA gate does not execute setup.

This QA gate does not install the product.

This QA gate does not create an installer.

This QA gate does not create a commercial package.

This QA gate does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer.

## Source Stable State

Source stable HEAD:

056d1b86233a6584e8d85702d2dbadc99dfba257

Source commit:

docs: add CID Local Media Agent controlled execution plan

Source tag:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-plan-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PLAN_PASS_READY_FOR_PLAN_QA_GATE

## QA Gate Decision

Decision:

PASS_READY_FOR_ONE_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_EXECUTION_PHASE

This means a later phase may execute exactly one controlled internal second-machine setup execution using the validated plan.

This QA gate does not execute that phase.

The execution phase must be separate.

The execution phase must be evidence-recorded.

The execution phase must remain internal-only.

The execution phase must use controlled fixture input only.

The execution phase must not use real media.

The execution phase must not become an installer phase.

The execution phase must not become a client delivery phase.

## Required Source Artifacts

This QA gate requires:

- controlled execution plan document
- controlled execution plan test
- controlled execution authorization gate document
- controlled execution authorization gate test
- execution readiness QA gate document
- execution readiness QA gate test
- execution readiness document
- execution readiness test
- setup plan QA gate document
- setup plan QA gate test
- setup plan document
- setup plan test
- setup readiness document
- setup readiness test
- internal demo readiness test
- visible report runtime CLI
- visible report runtime generator

## Plan Completeness Criteria

The controlled execution plan must define:

- phase
- objective
- source stable state
- plan decision
- execution plan scope
- machine preconditions
- repository preconditions
- controlled workspace plan
- exact future command plan
- approved validation tests
- controlled fixture plan
- evidence record plan
- required stop conditions
- explicitly blocked commands
- presenter language
- next safe phase
- validation evidence
- acceptance result

## Exact Command Plan Criteria

The plan must include only command families for:

- creating a controlled workspace
- entering the controlled workspace
- cloning the repository
- entering the repository
- verifying branch
- verifying local HEAD
- verifying remote main
- verifying required remote tag
- creating a virtual environment
- activating the virtual environment
- installing documented dependencies inside the virtual environment
- running approved validation tests
- creating controlled fixture and output folders
- creating a controlled scanner-result fixture
- running the visible report CLI with controlled fixture input only
- inspecting the generated report path
- writing an evidence record

## Required Expected HEAD

The plan must require this expected HEAD:

056d1b86233a6584e8d85702d2dbadc99dfba257

## Required Source Tag

The plan must require this source tag:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-controlled-execution-plan-v1-20260620

## Controlled Workspace Criteria

The plan must use a controlled internal workspace shape:

/tmp/cid_local_media_agent_second_machine_controlled_execution_v1

The workspace must be disposable.

The workspace must be outside client media folders.

The workspace must be outside production footage folders.

The workspace must be outside confidential project folders.

The workspace must not contain real media.

The workspace must not contain production footage.

The workspace must not contain client media.

The workspace must not contain confidential scripts.

The workspace must not contain environment secret files.

The workspace must not contain database files.

The workspace must not contain installer artifacts.

The workspace must not contain license activation files.

The workspace must not contain public demo assets.

The workspace must not contain sales demo assets.

## Approved Validation Criteria

The plan must run these validation tests before any visible report CLI execution:

- controlled execution plan test
- controlled execution authorization gate test
- execution readiness QA gate test
- execution readiness test
- setup plan QA gate test
- setup plan test
- setup readiness test
- internal demo readiness test
- visible report runtime CLI test
- visible report runtime CLI implementation QA gate test
- visible report runtime generator test
- controlled runtime implementation QA gate test

## Controlled Fixture Criteria

The plan must create only a controlled scanner-result fixture.

The fixture must be generated from `_valid_scanner_result`.

The fixture path must be:

/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json

The fixture must not reference real media.

The fixture must not reference production footage.

The fixture must not reference client material.

The fixture must not include confidential script material.

## Visible Report CLI Criteria

The plan may run only:

scripts/local_media_agent/visible_report_runtime_cli.py

The CLI must use:

--scanner-result-json /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_fixture_input/controlled_scanner_result.json

The CLI must write under:

--output-root /tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output

The CLI may print the output path with:

--print-output-path

The generated report must remain under:

/tmp/cid_local_media_agent_second_machine_controlled_execution_v1/controlled_output/05_reports/cid_local_media_agent_visible_report_v1.md

## Evidence Record Criteria

The plan must write an evidence record named:

controlled_execution_evidence_v1.json

The evidence record must declare:

- internal_only true
- controlled_fixture_only true
- real_media_used false
- client_material_used false
- installer_created false
- client_installation false
- public_demo false
- sales_demo false
- database_write false
- saas_upload false
- expected HEAD
- source tag
- authorization source phase
- created UTC timestamp

## Required Stop Conditions

The future execution phase must stop before visible report CLI execution if:

- machine owner is not project owner
- machine is client-owned
- machine is productora-owned
- machine is school-owned
- machine is investor-owned
- workspace is not controlled
- workspace is inside client media folder
- workspace is inside production footage folder
- workspace is inside confidential project folder
- repository remote is unexpected
- branch is not main
- local HEAD does not match expected HEAD
- remote main does not match expected HEAD
- required remote tag is missing
- repository is dirty before execution
- virtual environment cannot be created
- dependency installation fails
- approved validation tests fail
- controlled fixture cannot be created
- output root is not controlled
- real media is requested
- production footage is requested
- client media is requested
- confidential script material is requested
- environment secret file is requested
- database file is requested
- installer action is requested
- license activation action is requested
- public demo action is requested
- sales demo action is requested
- SaaS upload is requested
- database write is requested

## Explicitly Blocked Commands

The future execution phase must not include commands that:

- run scanner on real media
- run media probing on real files
- run ffprobe on real files
- run ffmpeg on real files
- synchronize audio
- transcribe audio
- generate subtitles
- translate subtitles
- export DaVinci Resolve timelines
- export Avid timelines
- upload to SaaS
- write to database
- copy secrets
- copy environment files
- copy database files
- create installer package
- sign installer
- activate license
- connect license server
- install on client computer
- present public demo
- present sales demo

## Presenter Language Criteria

The future execution phase must state:

This is one controlled internal second-machine setup execution.

This is not a commercial installation.

This is not a client installation.

This is not an installer.

This is not a public demo.

This is not a sales demo.

This uses controlled fixture input only.

This does not scan real media.

This does not probe real media.

This does not sync audio.

This does not transcribe.

This does not generate subtitles.

This does not export timelines.

This does not upload to SaaS.

This does not write to a database.

## Next Safe Phase

The next safe phase may be:

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.V1

That phase may execute one controlled internal second-machine setup execution using the validated plan.

It must remain internal-only.

It must use controlled fixture input only.

It must write an evidence record.

It must stop on any stop condition.

It must not install on a client machine.

It must not create an installer.

It must not authorize public demo use.

It must not authorize sales demo use.

It must not use real media.

## Validation Evidence Required

This controlled execution plan QA gate is accepted only with:

- controlled execution plan QA gate test passing
- controlled execution plan test passing
- controlled execution authorization gate test passing
- second machine setup execution readiness QA gate test passing
- second machine setup execution readiness test passing
- second machine setup plan QA gate test passing
- second machine setup plan test passing
- second machine setup readiness test passing
- internal demo readiness test passing
- CLI test passing
- CLI implementation QA gate passing
- runtime generator test passing
- controlled runtime implementation QA gate passing
- supporting implemented runtime chain tests passing
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing

## Acceptance Result

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_PLAN_QA_GATE_PASS_READY_FOR_ONE_CONTROLLED_INTERNAL_EXECUTION
