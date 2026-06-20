# CID Local Media Agent - Internal Demo Second Machine Setup Execution Readiness v1

## Phase

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.V1

## Objective

Prepare readiness for a future controlled internal second-machine setup execution.

This phase defines target machine criteria, execution boundaries, allowed commands, evidence capture, failure handling, and stop conditions before any future setup execution.

This phase does not execute setup on a second machine.

This phase does not install the product.

This phase does not create an installer.

This phase does not create a commercial package.

This phase does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer.

## Source Stable State

Source stable HEAD:

982d4e9bdbebc55678bebf482a18e3ee5fa6eed9

Source commit:

test: add CID Local Media Agent second machine setup plan QA gate

Source tag:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-plan-qa-gate-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_PLAN_QA_GATE_PASS_READY_FOR_SECOND_MACHINE_SETUP_EXECUTION_READINESS

## Readiness Decision

The controlled internal second-machine setup execution readiness is:

READY_FOR_CONTROLLED_INTERNAL_SECOND_MACHINE_SETUP_EXECUTION_READINESS_QA_GATE

This means the future execution readiness plan may be validated.

It does not mean setup execution is authorized.

It does not mean setup execution has happened.

It does not mean installation has happened.

It does not mean an installer exists.

It does not mean a client may receive the software.

It does not mean a public or sales demonstration is authorized.

## Required Source Artifacts

This execution readiness phase requires:

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

## Allowed Target Machine

A future controlled setup execution may only target:

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

## Blocked Target Machine

A future controlled setup execution must not target:

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

## Required Target Machine Evidence

Before any future execution, the operator must capture:

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

## Controlled Workspace Requirements

The future workspace must be:

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

## Allowed Execution Command Families

A future execution phase may allow only:

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

## Blocked Execution Command Families

A future execution phase must block:

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

## Required Readiness Checklist

The future execution readiness must confirm:

- target machine is allowed
- target machine is internal
- target machine has no client material
- target machine has no production footage
- workspace is controlled
- workspace is disposable
- repository clone is from approved remote
- HEAD is approved
- branch is main
- virtual environment is local
- dependencies are installed only inside virtual environment
- validation tests pass
- fixture input is controlled
- visible report output is controlled
- generated report declares client-facing readiness false
- generated report declares scanner execution by this renderer false
- generated report declares media probing by this renderer false
- generated report declares roadmap outputs not generated
- operator confirms no real media was used

## Required Failure Handling

If any readiness condition fails, the future execution must stop.

Stop reasons include:

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

## Presenter Boundary

For any future internal second-machine execution, the presenter must say:

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

## Execution Authorization Boundary

This readiness phase does not authorize setup execution.

A later QA gate must validate this execution readiness before any controlled execution phase.

The future execution phase must be separate.

The future execution phase must record evidence.

The future execution phase must still be internal-only.

The future execution phase must still use controlled fixture input only.

The future execution phase must not become an installer phase.

The future execution phase must not become a client delivery phase.

## Next Safe Phase

The next safe phase may be:

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.QA.GATE.V1

That phase may validate this readiness.

It must not execute setup.

It must not create an installer.

It must not authorize client installation.

It must not authorize public demo use.

It must not authorize sales demo use.

## Validation Evidence Required

This execution readiness phase is accepted only with:

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

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_EXECUTION_READINESS_PASS_READY_FOR_EXECUTION_READINESS_QA_GATE
