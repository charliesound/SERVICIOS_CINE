# CID Local Media Agent — Scanner CLI ffprobe Failure Path QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.FAILURE_PATH.QA.GATE.V1`

## Objective

This QA gate audits the existing ffprobe failure-path contract before any future implementation phase.

The gate verifies that the contract is complete enough to guide later failure handling while keeping runtime probing out of scope.

## Scope

This phase is documentation/test-only.

It audits:

- the failure-path contract document
- the expected future failure cases
- the expected future error codes
- the future safe output shape
- the privacy restrictions
- the relationship with synthetic placeholders
- the explicit implementation gate
- compatibility with the current safe scanner baseline

## Required source contract

The source contract under QA is:

`docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md`

## Required test contract

The source test under QA is:

`tests/unit/test_cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract.py`

## Required failure cases

The source contract must keep coverage for:

- tool unavailable
- non-zero tool exit
- empty stdout
- malformed JSON
- timeout
- access denied
- non-media placeholder input
- unsupported input
- missing input
- input outside allowed root
- directory input
- unsafe report label

## Required error codes

The source contract must keep these error codes:

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

## Required future output fields

The source contract must keep these fields:

- `probe_status`
- `error_code`
- `safe_reason`
- `media_probe_attempted`
- `tool_name`
- `tool_available`
- `exit_code`
- `stdout_present`
- `stderr_present`
- `timed_out`
- `safe_file_label`
- `relative_path_allowed`
- `metadata_partial`
- `human_review_required`

## Privacy and report safety

The source contract must continue to prohibit:

- absolute path leakage
- private folder leakage
- mounted host path leakage
- environment file leakage
- local database file leakage
- raw stdout by default
- raw stderr by default
- raw media metadata by default

Only safe relative labels may be used in future reports.

## Runtime restrictions

This QA gate does not execute ffprobe.

This QA gate does not execute ffmpeg.

This QA gate does not add subprocess execution.

This QA gate does not modify scanner runtime.

This QA gate does not modify backend runtime.

This QA gate does not modify database models.

This QA gate does not create media files.

This QA gate does not create report outputs.

## Implementation gate

A future implementation may only proceed after a separate approved phase defines:

- a controlled command wrapper
- timeout rules
- safe stdout and stderr redaction
- deterministic failure fixtures
- safe labels
- human-readable error mapping
- tests for every failure code

## Pass criteria

This QA gate passes only if:

- the source failure-path contract exists
- the source failure-path contract tests pass
- all required failure cases remain documented
- all required error codes remain documented
- all required output fields remain documented
- runtime execution remains out of scope
- scanner runtime still has no media execution subprocess
- existing placeholder QA/create tests remain valid
- WSL guard passes
- database-regression guard passes

## Explicit non-goals

This phase does not:

- implement a command wrapper
- implement subprocess calls
- run media probes
- call external binaries
- add scanner CLI flags
- add JSON report output
- add backend endpoints
- add workers
- add queue behavior
- add billing behavior
- add storage behavior

## Result

This QA gate confirms whether the failure-path contract is safe to use as the basis for a later command-wrapper contract.

It does not authorize ffprobe execution.
