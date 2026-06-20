# CID Local Media Agent - Internal Demo Second Machine Setup Plan QA Gate v1

## Phase

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.PLAN.QA.GATE.V1

## Objective

Validate the controlled internal second-machine setup plan before any future setup execution readiness phase.

This QA gate confirms that the setup plan is complete, bounded, internally scoped, and safe.

This QA gate does not execute the setup on a second machine.

This QA gate does not create an installer.

This QA gate does not create a commercial package.

This QA gate does not authorize client-facing demo, public demo, sales demo, paid pilot use, production use, or installation on a client computer.

## Source Stable State

Source stable HEAD:

0ff9636d8b40f121dfff22e9eebc2ba1d2a75fb8

Source commit:

docs: add CID Local Media Agent second machine setup plan

Source tag:

cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-plan-v1-20260620

Source accepted result:

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_PLAN_PASS_READY_FOR_SECOND_MACHINE_SETUP_PLAN_QA_GATE

## QA Gate Decision

The second-machine setup plan is:

PASS_READY_FOR_CONTROLLED_SECOND_MACHINE_SETUP_EXECUTION_READINESS

This means a later phase may prepare controlled execution readiness for an internal second-machine setup.

It does not mean setup execution is authorized.

It does not mean installation has been performed.

It does not mean an installer exists.

It does not mean a client may receive the software.

It does not mean the product is ready for sales, public demo, paid pilot, or production use.

## Required Source Artifacts

This QA gate requires:

- second-machine setup plan document
- second-machine setup plan test
- second-machine setup readiness document
- second-machine setup readiness test
- internal demo readiness document
- internal demo readiness test
- internal demo script preparation document
- internal demo script preparation test
- visible report runtime CLI
- visible report runtime generator

## Plan Completeness Criteria

The setup plan must define:

- phase
- objective
- source stable state
- current decisions
- setup plan decision
- target machine profile
- required machine prerequisites
- controlled workspace policy
- setup command plan
- example command shape
- required setup validation
- allowed demonstration output
- blocked demonstration output
- required presenter language
- stop conditions
- installation boundary
- next safe phase
- validation evidence
- acceptance result

## Safety Boundary Criteria

The setup plan must explicitly block:

- actual setup execution by the plan alone
- commercial installer creation
- client installer creation
- client machine use
- productora machine use
- school machine use
- public demo use
- sales demo use
- paid pilot use
- product distribution
- installer signing
- license activation
- real media use
- production footage use
- scanner execution
- ffprobe execution
- ffmpeg execution
- sync output
- transcription output
- subtitle output
- timeline export
- SaaS upload
- database write

## Internal-Only Criteria

The setup plan must allow only:

- project-owner controlled machine
- internal development laptop
- internal review laptop
- clean internal WSL Ubuntu environment
- clean internal Linux environment
- controlled workspace
- controlled fixture input
- controlled output folder
- internal-only disclaimer
- internal setup notes
- generated markdown visible report from controlled facts

## Technical Scope Criteria

The setup plan must make clear:

- no media hardware is required
- no GPU is required
- ffprobe is not required
- ffmpeg is not required
- DaVinci Resolve is not required
- Avid is not required
- SaaS credentials are not required
- database credentials are not required
- the visible report renderer does not scan real media
- the visible report renderer does not probe real media
- roadmap outputs remain not generated

## Execution Boundary Criteria

The setup plan must state:

This plan is not an installation record.

A later phase must be created before any actual second-machine setup execution.

No execution is authorized by this plan alone.

Any future execution phase must capture machine type, operating system, workspace path, repository clone status, HEAD validation, virtual environment status, dependency install status, test results, visible report generation result, output path, and boundary compliance result.

## Required Future Phase

The next safe phase may be:

CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.SECOND.MACHINE.SETUP.EXECUTION.READINESS.V1

That phase may prepare readiness for a controlled internal setup execution.

It must not execute the setup.

It must not create an installer.

It must not authorize client installation.

It must not authorize public demo use.

It must not authorize sales demo use.

## Validation Evidence Required

This QA gate is accepted only with:

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

LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_PLAN_QA_GATE_PASS_READY_FOR_SECOND_MACHINE_SETUP_EXECUTION_READINESS
