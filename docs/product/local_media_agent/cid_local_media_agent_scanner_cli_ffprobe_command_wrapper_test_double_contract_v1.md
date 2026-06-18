# CID Local Media Agent — ffprobe Command Wrapper Test Double Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.V1`

## Objective

This document defines the future test double contract for the safe command-runner boundary used by the CID Local Media Agent ffprobe command wrapper.

The purpose is to make the future wrapper testable without executing external binaries, without reading real media, without probing real files, and without changing scanner runtime behavior.

This phase is documentation/test-only. It does not implement the wrapper, does not implement a command runner, does not execute ffprobe, does not execute ffmpeg, and does not process media.

## Context

Previous phases defined:

- ffprobe availability and metadata schema expectations.
- Synthetic placeholder outputs.
- Failure path contracts.
- Failure path QA gate.
- Safe command wrapper contract.
- Command wrapper QA gate.
- Command wrapper implementation readiness gate.

This phase defines the test double contract that must exist before any future implementation can safely introduce an executable command boundary.

## Test double boundary

The future wrapper must be able to receive a command-runner dependency through an explicit boundary.

The test double must simulate command-runner outcomes without invoking the operating system.

The future wrapper must not require real external binaries for unit tests.

The test double must return structured results only.

## Required result shape

A command-runner test double result must expose these fields:

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

The result may include additional diagnostic fields only if they are safe, deterministic, and do not reveal private paths or media content.

## Required simulation modes

The test double must be able to simulate:

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

Each mode must map to the failure path contract without executing a real process.

## Determinism requirements

The test double must be deterministic.

For the same configured mode and input label, it must return the same structured result.

It must not depend on wall-clock timing, filesystem state, installed binaries, real media metadata, network access, machine hostname, username, or absolute local paths.

## Privacy requirements

The test double must not emit:

- real media filenames
- real directory names
- absolute local paths
- private user names
- raw command strings
- raw stdout or stderr from an external executable
- real media metadata
- source script text
- production costs
- shooting dates
- private project identifiers

Only safe labels and synthetic placeholder values are allowed.

## Wrapper integration expectations

When a future wrapper implementation is allowed, it must use an injectable command-runner boundary.

Unit tests must use the test double.

Real executable access, if ever allowed, must remain outside unit tests and behind a separate explicit gate.

The test double must validate wrapper behavior for success, error mapping, timeout handling, output parsing, redaction, safe labels, and failure path consistency.

## Non-goals

This phase does not:

- implement a command runner
- implement the wrapper
- execute ffprobe
- execute ffmpeg
- add process execution
- scan real media
- read real media files
- modify scanner runtime
- modify backend services
- modify frontend code
- modify billing, workers, queue, storage, or cloud behavior
- add installer logic
- add desktop activation logic

## Acceptance criteria

This contract is accepted only if:

- the phase remains documentation/test-only
- only this document and its unit contract test are changed
- test double modes cover all required failure paths
- privacy constraints are explicit
- deterministic behavior is required
- future wrapper tests are required to use the test double
- no real command execution is authorized
- no runtime scanner file is modified

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.QA.GATE.V1`
