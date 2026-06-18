# CID Local Media Agent — Scanner CLI ffprobe Command Wrapper Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.CONTRACT.V1`

## Objective

This phase defines the contract for a future safe ffprobe command wrapper in CID Local Media Agent.

The wrapper contract describes how a later implementation must prepare command arguments, apply timeouts, redact output, classify failures and protect client privacy.

This phase is documentation/test-only.

## Current status

The current scanner remains safe-baseline only.

This phase does not execute ffprobe.

This phase does not execute ffmpeg.

This phase does not add subprocess execution.

This phase does not modify scanner runtime.

This phase does not inspect real client media.

This phase does not create media files.

## Source contracts

This contract builds on the existing failure-path contract and QA gate:

- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_qa_gate_v1.md`

## Future wrapper responsibility

A future command wrapper may only be responsible for:

- validating a candidate media path against the approved project root
- preparing a deterministic ffprobe argument list
- enforcing a timeout
- capturing stdout and stderr separately
- limiting retained stdout and stderr
- redacting private path fragments
- converting raw process results into safe structured probe results
- mapping wrapper failures to stable error codes
- never returning raw command lines in reports
- never returning executable paths in reports

## Required future wrapper inputs

A later implementation should accept only explicit structured inputs:

- `project_root`
- `candidate_relative_path`
- `timeout_seconds`
- `allowed_probe_fields`
- `redaction_policy`
- `max_stdout_bytes`
- `max_stderr_bytes`
- `human_review_required_by_default`

The wrapper must not accept shell strings.

The wrapper must not accept arbitrary command fragments.

The wrapper must not accept user-provided executable paths.

The wrapper must not accept network URLs.

## Required future command policy

A later implementation must build commands as an argument list.

A later implementation must not use shell execution.

A later implementation must not interpolate user text into a shell command.

A later implementation must not inherit unsafe environment behavior.

A later implementation must not follow paths outside the approved root.

A later implementation must not write media-derived data outside the approved output root.

## Required future timeout policy

The future wrapper must define:

- default timeout
- maximum timeout
- timeout error code
- timeout safe reason
- timeout cleanup behavior
- no retry by default

Timeouts must map to `FFPROBE_TIMEOUT`.

## Required future redaction policy

The future wrapper must redact:

- absolute local paths
- private user folder fragments
- mounted host path fragments
- environment file names
- local database file names
- executable paths
- raw command lines
- raw stderr by default
- raw stdout by default
- oversized output

Only safe relative labels may be retained.

## Required future result shape

A future wrapper result must include:

- `wrapper_status`
- `probe_status`
- `error_code`
- `safe_reason`
- `safe_file_label`
- `candidate_relative_path`
- `tool_name`
- `tool_available`
- `media_probe_attempted`
- `timeout_seconds`
- `timed_out`
- `exit_code`
- `stdout_present`
- `stderr_present`
- `stdout_bytes_retained`
- `stderr_bytes_retained`
- `metadata_partial`
- `redaction_applied`
- `human_review_required`

## Required future error mapping

The future wrapper must preserve compatibility with the failure-path contract codes:

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

## Placeholder relationship

The wrapper contract may use existing synthetic placeholders in a later test phase.

The existing placeholders remain non-media synthetic files.

No real video is authorized.

No real audio is authorized.

No client material is authorized.

## Implementation gate

A future implementation phase may proceed only after another explicit approval.

That later phase must add tests for:

- no shell execution
- deterministic argument list
- timeout handling
- stdout redaction
- stderr redaction
- path-policy rejection
- unsupported input
- invalid input
- tool unavailable
- safe result shape
- no absolute path leakage
- no command-line leakage
- human-readable safe errors

## Explicit non-goals

This phase does not:

- implement a wrapper function
- call external binaries
- run media probes
- add scanner CLI flags
- add JSON report generation
- modify scanner runtime
- modify backend runtime
- modify database models
- add migrations
- modify Docker
- modify frontend
- add workers
- add queue behavior
- add billing behavior
- add storage behavior
- create real media fixtures

## Pass criteria

This phase passes when:

- the wrapper contract exists
- the wrapper contract references the failure-path contract
- the wrapper contract defines input restrictions
- the wrapper contract defines command policy
- the wrapper contract defines timeout policy
- the wrapper contract defines redaction policy
- the wrapper contract defines safe result shape
- the wrapper contract preserves failure-path error codes
- scanner runtime remains unchanged
- existing failure-path QA gate remains valid
- WSL guard passes
- database-regression guard passes

## Result

This contract prepares a safe future path for an ffprobe command wrapper.

It does not authorize ffprobe execution.
