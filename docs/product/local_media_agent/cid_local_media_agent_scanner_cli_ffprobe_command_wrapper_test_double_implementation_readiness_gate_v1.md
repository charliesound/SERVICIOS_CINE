# CID Local Media Agent — ffprobe Command Wrapper Test Double Implementation Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.IMPLEMENTATION.READINESS.GATE.V1`

## Objective

This readiness gate decides whether the CID Local Media Agent project is ready to prepare a future minimal implementation of the ffprobe command wrapper test double.

This phase does not implement the test double.

This phase does not implement the command wrapper.

This phase does not execute ffprobe, does not execute ffmpeg, does not add subprocess usage, and does not modify scanner runtime.

The only purpose is to confirm that enough contract and QA evidence exists before a future implementation phase is considered.

## Inputs reviewed

This gate reviews the following completed phases:

- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.V1`
- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.SANITIZED.V1`
- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.QA.GATE.V1`

It also relies on earlier wrapper and failure path phases:

- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.CONTRACT.V1`
- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.QA.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.IMPLEMENTATION.READINESS.GATE.V1`
- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.FAILURE_PATH.CONTRACT.V1`
- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.FAILURE_PATH.QA.GATE.V1`

## Readiness decision

The project is ready to plan a future test double implementation only if all of these are true:

- The test double contract exists.
- The test double QA gate exists.
- The sanitized contract test passes.
- The test double QA gate test passes.
- Required failure path modes are represented.
- Required structured result fields are represented.
- The injectable command-runner boundary remains explicit.
- Unit tests are required to use the test double.
- Real executable access remains outside unit tests.
- Real executable access remains behind a separate explicit gate.
- Privacy constraints remain explicit.
- Determinism requirements remain explicit.
- Runtime scanner changes remain blocked.
- Real command execution remains blocked.

## Future implementation constraints

A future implementation phase, if explicitly authorized later, must remain minimal and local to test support.

It may define a pure in-process test double data structure or helper.

It must not execute external commands.

It must not import the subprocess module.

It must not call the operating system shell.

It must not run ffprobe.

It must not run ffmpeg.

It must not read real media files.

It must not scan real client folders.

It must not change `scripts/cid_media_agent_scan.py`.

It must not change files under `src/`.

It must not change backend, frontend, Alembic, Docker, billing, workers, queue, storage, or cloud behavior.

## Required future output shape

A future test double implementation must preserve the contract result shape:

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

## Required future simulation modes

A future test double implementation must support:

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

## Non-goals

This readiness gate does not:

- implement the test double
- implement the wrapper
- introduce command execution
- introduce subprocess usage
- introduce shell usage
- execute ffprobe
- execute ffmpeg
- process media
- read media metadata
- change runtime scanner behavior
- change SaaS runtime behavior
- change database behavior
- change deployment behavior

## Gate result

The gate result is:

`READY_FOR_FUTURE_TEST_DOUBLE_IMPLEMENTATION_PLANNING_ONLY`

This means a future implementation planning phase may be considered.

It does not mean real command execution is approved.

It does not mean scanner runtime changes are approved.

It does not mean ffprobe execution is approved.

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.V1`
