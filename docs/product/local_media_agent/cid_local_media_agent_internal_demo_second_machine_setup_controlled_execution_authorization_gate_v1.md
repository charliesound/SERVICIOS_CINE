# CID Local Media Agent - Internal Demo Second Machine Setup Controlled Execution Authorization Gate v1

## Phase

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.AUTHORIZATION.GATE.V1

## Objective

Decide whether one future controlled internal second-machine setup execution may be authorized.

This gate exists after the second-machine setup execution readiness QA gate.

This gate does not execute setup.

This gate does not install the product.

This gate does not create an installer.

This gate does not create a commercial package.

This gate does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer.

## Source Stable State

Source stable HEAD:

b5ec8b425847d5df98da9049afd15144349b5a0a

Source commit:

test: add CID Local Media Agent second machine setup execution readiness QA gate

Source tag:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-execution-readiness-qa-gate-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_EXECUTION_READINESS_QA_GATE_PASS_READY_FOR_CONTROLLED_EXECUTION_AUTHORIZATION_GATE

## Human Authorization Decision

Decision:

AUTHORIZE_ONE_FUTURE_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_EXECUTION_PHASE

This means one later execution phase may be prepared for one internal controlled second-machine setup execution.

This gate does not execute that phase.

The execution phase must be separate.

The execution phase must be evidence-recorded.

The execution phase must remain internal-only.

The execution phase must use controlled fixture input only.

The execution phase must not use real media.

The execution phase must not become an installer phase.

The execution phase must not become a client delivery phase.

## Authorization Scope

This authorization gate allows preparation of one future controlled execution phase only for:

- one project-owner controlled internal second machine
- one controlled internal workspace
- one clean shell environment
- one repository clone or verified existing clone
- one expected HEAD
- one virtual environment
- one approved validation sequence
- one controlled fixture input set
- one visible report CLI execution using controlled fixture input
- one generated report under controlled output root
- one evidence record

## Explicit Non-Authorization

This authorization gate does not authorize:

- executing setup inside this phase
- commercial installation
- client installation
- productora installation
- school installation
- investor installation
- public demo
- sales demo
- paid pilot use
- production use
- installer creation
- installer signing
- license activation
- license server connection
- scanner execution on real media
- media probing on real files
- ffprobe on real files
- ffmpeg on real files
- audio synchronization
- transcription
- subtitle generation
- subtitle translation
- DaVinci Resolve timeline export
- Avid timeline export
- SaaS upload
- database writes
- copied environment secrets
- copied database files
- copied confidential script material
- copied client material
- copied production footage

## Required Preconditions Before Future Execution Phase

A future execution phase must verify:

- repository is clean before execution
- current branch is main
- local HEAD matches expected HEAD
- remote main matches expected HEAD
- required tag exists remotely
- machine owner is project owner
- machine is internal only
- machine is not client-owned
- machine is not a productora machine
- machine is not a school machine
- machine is not an investor machine
- workspace is controlled
- workspace is disposable
- workspace is outside client media folders
- workspace is outside production footage folders
- workspace is outside confidential project folders
- no environment secret files are copied
- no database files are copied
- no real media is copied
- no production footage is copied
- virtual environment is local to the controlled clone
- dependency installation is inside the virtual environment
- validation tests pass before visible report CLI execution
- fixture input is controlled
- output root is controlled
- generated report remains inside output root
- evidence record is written

## Required Evidence Record For Future Execution Phase

A future execution phase must record:

- phase name
- authorization source phase
- source HEAD
- source tag
- machine type
- machine owner confirmation
- operating system
- shell environment
- Python version
- Git version
- repository remote
- repository path
- branch
- local HEAD
- remote main HEAD
- virtual environment path
- dependency command
- validation commands
- fixture input path
- output root path
- visible report command shape
- generated report path
- generated report existence
- boundary compliance result
- stop reason if stopped
- final result

## Stop Conditions For Future Execution Phase

The future execution phase must stop if any of these occur:

- wrong repository path
- wrong branch
- expected HEAD mismatch
- remote main mismatch
- missing required remote tag
- dirty repository before execution
- unauthorized machine owner
- non-internal machine
- client-owned machine
- productora-owned machine
- school-owned machine
- investor-owned machine
- uncontrolled workspace
- workspace inside client media folder
- workspace inside production footage folder
- workspace inside confidential project folder
- copied environment secret file detected
- copied database file detected
- real media detected
- production footage detected
- confidential script material detected
- virtual environment missing
- dependency installation failure
- validation test failure
- fixture input missing
- output root missing
- output root outside controlled workspace
- generated report missing
- generated report outside controlled output root
- request to run scanner on real media
- request to run ffprobe on real files
- request to run ffmpeg on real files
- request to sync audio
- request to transcribe
- request to generate subtitles
- request to export timelines
- request to upload to SaaS
- request to write to database
- request to install on client machine
- request to create installer
- request to sign installer
- request to activate license
- request to show public demo
- request to show sales demo

## Allowed Future Execution Command Families

A future execution phase may include only command families that:

- create controlled workspace
- clone repository
- enter repository folder
- check current branch
- check local HEAD
- check remote main
- check required tag
- create virtual environment
- activate virtual environment
- install documented dependencies inside virtual environment
- run approved validation tests
- create controlled fixture input
- run visible report CLI with controlled fixture input
- write report under controlled output root
- print generated report path
- inspect generated report
- write evidence record

## Blocked Future Execution Command Families

A future execution phase must not include command families that:

- scan real media
- probe real media
- process production footage
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

## Presenter Language For Future Execution

The future execution phase must use this language:

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

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.CONTROLLED.EXECUTION.PLAN.V1

That phase may define the exact command plan for one future controlled internal second-machine setup execution.

It must not execute setup.

It must not install the product.

It must not create an installer.

It must not authorize client installation.

It must not authorize public demo use.

It must not authorize sales demo use.

## Validation Evidence Required

This authorization gate is accepted only with:

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

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_CONTROLLED_EXECUTION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_EXECUTION_PLAN
