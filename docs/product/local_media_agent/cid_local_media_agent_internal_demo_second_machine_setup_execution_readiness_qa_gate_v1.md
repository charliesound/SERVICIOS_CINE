# CID Local Media Agent - Internal Demo Second Machine Setup Execution Readiness QA Gate v1

## Phase

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.QA.GATE.V1

## Objective

Validate the controlled internal second-machine setup execution readiness before any future controlled execution authorization phase.

This QA gate confirms that execution readiness is complete, internally scoped, evidence-driven, and safe.

This QA gate does not execute setup on a second machine.

This QA gate does not install the product.

This QA gate does not create an installer.

This QA gate does not create a commercial package.

This QA gate does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer.

## Source Stable State

Source stable HEAD:

c54521d5a1cdc4f4aabd0f0af5989be5aa4385aa

Source commit:

docs: add CID Local Media Agent second machine setup execution readiness

Source tag:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-execution-readiness-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_EXECUTION_READINESS_PASS_READY_FOR_EXECUTION_READINESS_QA_GATE

## QA Gate Decision

The execution readiness is:

PASS_READY_FOR_CONTROLLED_SECOND_MACHINE_SETUP_EXECUTION_AUTHORIZATION_GATE

This means a later phase may prepare an explicit authorization gate for a controlled internal second-machine setup execution.

It does not mean setup execution is authorized by this QA gate.

It does not mean setup execution has happened.

It does not mean installation has happened.

It does not mean an installer exists.

It does not mean a client may receive the software.

It does not mean a public demo is authorized.

It does not mean a sales demo is authorized.

## Required Source Artifacts

This QA gate requires:

- second-machine setup execution readiness document
- second-machine setup execution readiness test
- second-machine setup plan QA gate document
- second-machine setup plan QA gate test
- second-machine setup plan document
- second-machine setup plan test
- second-machine setup readiness document
- second-machine setup readiness test
- internal demo readiness document
- internal demo readiness test
- visible report runtime CLI
- visible report runtime generator

## Execution Readiness Completeness Criteria

The execution readiness must define:

- phase
- objective
- source stable state
- readiness decision
- required source artifacts
- allowed target machine
- blocked target machine
- required target machine evidence
- controlled workspace requirements
- allowed execution command families
- blocked execution command families
- required readiness checklist
- required failure handling
- presenter boundary
- execution authorization boundary
- next safe phase
- validation evidence
- acceptance result

## Machine Eligibility Criteria

The execution readiness must allow only:

- project-owner controlled internal machine
- internal development laptop
- internal review laptop
- clean internal WSL Ubuntu environment
- clean internal Linux environment
- machine without client material
- machine without production footage
- machine without confidential script material
- machine without copied environment secrets
- machine without copied local database files
- machine with a disposable internal workspace

The execution readiness must block:

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
- machine containing real production media

## Evidence Criteria

The execution readiness must require evidence for:

- machine owner confirmation
- machine type
- operating system
- shell environment
- Python version
- Git version
- workspace path
- workspace creation command
- repository remote used
- cloned repository path
- checked branch
- local HEAD
- expected HEAD
- virtual environment path
- dependency installation command
- validation commands
- visible report command shape
- output root path
- generated report path
- boundary compliance result

## Controlled Workspace Criteria

The execution readiness must require a workspace that is:

- created only for this internal setup
- outside any client media folder
- outside any production footage folder
- outside any confidential project folder
- outside desktop clutter
- outside downloads clutter
- disposable after review
- free of copied secrets
- free of copied database files
- free of real media
- free of production footage
- dedicated to controlled fixture input and generated internal output

## Allowed Command Criteria

The execution readiness may allow only:

- create controlled workspace
- clone repository
- enter repository folder
- check current branch
- check HEAD
- create virtual environment
- activate virtual environment
- install documented dependencies inside the virtual environment
- run approved validation tests
- create controlled fixture input
- run visible report CLI with controlled fixture input
- write generated report to controlled output root
- print generated report path
- inspect generated markdown report

## Blocked Command Criteria

The execution readiness must block:

- scanning real media
- probing real media
- processing production footage
- running ffprobe on real files
- running ffmpeg on real files
- synchronizing audio
- transcribing audio
- generating subtitles
- translating subtitles
- exporting DaVinci timelines
- exporting Avid timelines
- uploading to SaaS
- writing to database
- copying secrets
- copying environment files
- copying database files
- installing on client machine
- creating installer package
- signing installer
- activating license
- connecting license server
- presenting as public demo
- presenting as sales demo

## Failure Handling Criteria

The execution readiness must stop future execution if any readiness condition fails.

Required stop reasons include:

- wrong machine type
- unauthorized machine owner
- non-internal machine
- client material detected
- production footage detected
- confidential script material detected
- workspace path not controlled
- expected HEAD mismatch
- branch mismatch
- virtual environment missing
- dependency installation failure
- validation test failure
- fixture input missing
- output root not controlled
- generated report missing
- generated report outside controlled output root
- any request to use real media
- any request to create an installer
- any request to show a public demo
- any request to show a sales demo
- any request to install on a client computer

## Presenter Boundary Criteria

The execution readiness must require this language:

This is a controlled internal setup execution.

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

## Authorization Boundary Criteria

This QA gate does not authorize setup execution.

This QA gate does not authorize installation.

This QA gate does not authorize client delivery.

This QA gate does not authorize public presentation.

This QA gate does not authorize sales presentation.

A later controlled authorization gate must exist before any execution phase.

The future execution phase must be separate.

The future execution phase must record evidence.

The future execution phase must remain internal-only.

The future execution phase must use controlled fixture input only.

The future execution phase must not become an installer phase.

The future execution phase must not become a client delivery phase.

## Next Safe Phase

The next safe phase may be:

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.AUTHORIZATION.GATE.V1

That phase may decide whether to authorize one controlled internal second-machine setup execution.

It must not execute setup.

It must not create an installer.

It must not authorize client installation.

It must not authorize public demo use.

It must not authorize sales demo use.

## Validation Evidence Required

This QA gate is accepted only with:

- second machine setup execution readiness QA gate test passing
- second machine setup execution readiness test passing
- second machine setup plan QA gate test passing
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

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_EXECUTION_READINESS_QA_GATE_PASS_READY_FOR_CONTROLLED_EXECUTION_AUTHORIZATION_GATE
