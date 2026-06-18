# CID Local Media Agent — ffprobe Command Wrapper Test Double Minimal Implementation Plan v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.V1`

## Objective

This document defines the minimal future implementation plan for the CID Local Media Agent ffprobe command wrapper test double.

This is a planning-only phase.

It does not implement the test double.

It does not implement the command wrapper.

It does not execute ffprobe.

It does not execute ffmpeg.

It does not add subprocess usage.

It does not modify scanner runtime.

It does not process media.

## Background

The previous readiness gate produced:

`READY_FOR_FUTURE_TEST_DOUBLE_IMPLEMENTATION_PLANNING_ONLY`

That result allows planning a minimal test double implementation, but it does not authorize implementation in this phase.

The future test double must exist only to support safe unit tests for a future command wrapper boundary.

## Minimal future implementation target

A future implementation may create a small pure-Python test support helper.

The helper must be deterministic, in-process, and side-effect free.

It must not call the operating system.

It must not inspect installed binaries.

It must not read real media files.

It must not scan folders.

It must not import the subprocess module.

It must not execute external commands.

It must not require ffprobe or ffmpeg.

## Proposed future file location

A future implementation may be placed under test support only, for example:

`tests/support/local_media_agent/ffprobe_command_runner_test_double.py`

The exact path must be confirmed in the future implementation phase.

The implementation must not be placed in runtime scanner code.

The implementation must not modify:

- `scripts/cid_media_agent_scan.py`
- files under `src/`
- backend code
- frontend code
- Alembic migrations
- Docker files
- billing code
- workers
- queue
- storage
- cloud integration

## Proposed future public API

A future test double may expose a simple factory or class with explicit mode selection.

Example conceptual API only:

- configure a simulation mode
- provide a safe report label
- provide synthetic requested args
- return a structured result object

This document does not create that API.

## Required future result shape

The future test double must return a structured result with:

- `tool_name`
- `requested_args`
- `exit_code`
- `stdout_text`
- `stderr_text`
- `duration_ms`
- `timed_out`
- `error_kind`
- `safe_report_label`
- `redaction_applied`
- `raw_command_hidden`
- `created_by_test_double`

The future result must not include private absolute paths, real media metadata, raw executable commands, real filenames, or client folder names.

## Required future modes

The future test double must support these modes:

- `SUCCESS_VALID_JSON`
- `FFPROBE_NOT_AVAILABLE`
- `FFPROBE_NON_ZERO_EXIT`
- `FFPROBE_EMPTY_STDOUT`
- `FFPROBE_INVALID_JSON`
- `FFPROBE_TIMEOUT`
- `FFPROBE_ACCESS_DENIED`
- `INPUT_NOT_MEDIA`
- `INPUT_UNSUPPORTED`
- `INPUT_MISSING`
- `INPUT_OUTSIDE_ALLOWED_ROOT`
- `INPUT_IS_DIRECTORY`
- `SAFE_REPORT_LABEL_REQUIRED`

Each mode must map to the existing failure path vocabulary.

## Minimal future behavior

The future implementation should:

- generate synthetic stdout only for `SUCCESS_VALID_JSON`
- generate synthetic stderr only when needed for a safe failure simulation
- keep `raw_command_hidden` true
- keep `redaction_applied` true
- require a safe report label
- avoid real paths
- avoid real filenames
- avoid real media metadata
- avoid nondeterministic timing
- use fixed synthetic duration values
- produce the same output for the same mode and safe label

## Required future unit tests

The future implementation phase must include tests for:

- one success result
- every failure mode
- deterministic repeated calls
- safe label requirement
- hidden raw command
- redaction flag
- no private path leakage
- no real media metadata leakage
- no subprocess module import
- no ffprobe execution
- no ffmpeg execution
- no scanner runtime changes

## Explicit non-authorization

This plan does not authorize:

- creating the test double implementation now
- implementing the command wrapper
- executing ffprobe
- executing ffmpeg
- adding subprocess usage
- touching scanner runtime
- touching SaaS runtime
- touching database behavior
- touching deployment behavior
- touching installer behavior
- scanning real client media

## Acceptance criteria for this plan

This plan is accepted only if:

- the phase remains documentation/test-only
- only this document and its unit test are changed
- the future implementation remains constrained to test support
- no runtime file is changed
- no external command execution is introduced
- no subprocess usage is introduced
- no media processing is introduced
- all required result fields are preserved
- all required modes are preserved
- the next phase remains explicit and gated

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.QA.GATE.V1`
