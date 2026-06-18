# CID Local Media Agent — Scanner CLI ffprobe Failure Path Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.FAILURE_PATH.CONTRACT.V1`

## Objective

This phase defines the contract for future ffprobe failure-path handling in CID Local Media Agent.

The goal is to describe how future scanner/probe work must behave when technical media probing cannot succeed.

This phase is documentation/test-only.

## Current status

The current scanner must remain safe-baseline only.

The current scanner must not execute ffprobe.

The current scanner must not execute ffmpeg.

The current scanner must not add subprocess runtime.

The current scanner must not parse real technical media metadata.

The current scanner must not inspect real client media.

## Inputs covered by the future failure-path contract

Future failure-path handling must cover these situations:

1. ffprobe is not available on the machine.
2. ffprobe is available but returns a non-zero exit status.
3. ffprobe returns empty stdout.
4. ffprobe returns malformed JSON.
5. ffprobe times out.
6. ffprobe is denied access to a file.
7. The input path points to a non-media placeholder.
8. The input path points to an unsupported file.
9. The input path points to a missing file.
10. The input path is outside the allowed project root.
11. The input path is a directory instead of a file.
12. The input path cannot be safely represented in reports.

## Expected future output shape

Future failure-path output must be structured and safe.

A future failed probe result should contain:

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

## Required future error codes

Future implementations should reserve these error codes:

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

## Safety and privacy requirements

Failure-path handling must not leak:

- absolute local paths
- private user folders
- mounted host paths
- environment file names
- local database file names
- real project titles
- client names
- raw stderr by default
- raw stdout by default
- raw media metadata by default

Reports may include a safe relative label only when it is inside an approved project root.

## Placeholder package relationship

The existing synthetic placeholder package is allowed as controlled future input.

Expected placeholders:

- `synthetic_invalid_media_placeholder.bin`
- `synthetic_permission_denied_placeholder.dat`
- `synthetic_unsupported_media_placeholder.txt`

These files are not real video.

These files are not real audio.

These files must remain tiny synthetic non-media payloads.

## Runtime restrictions

This phase must not implement runtime probing.

This phase must not call ffprobe.

This phase must not call ffmpeg.

This phase must not add subprocess execution.

This phase must not modify `scripts/cid_media_agent_scan.py`.

This phase must not add worker code.

This phase must not add backend endpoints.

This phase must not modify CID SaaS runtime.

## Database and infrastructure restrictions

This phase must not touch:

- backend runtime
- database models
- migrations
- Docker
- frontend
- billing
- workers
- queue execution
- external storage
- cloud services

## Future implementation gate

A later implementation phase may only proceed if it explicitly adds:

1. a controlled command wrapper contract,
2. timeout handling,
3. safe stderr/stdout redaction,
4. tenant/client privacy rules,
5. no absolute path leakage,
6. deterministic failure fixtures,
7. human-readable safe errors,
8. tests for each failure code.

## Pass criteria

This phase passes when:

- the contract document exists
- the contract names the required failure cases
- the contract names the required error codes
- the contract keeps runtime execution out of scope
- the contract keeps real media out of scope
- the existing placeholder QA gate remains valid
- the existing placeholder creation tests remain valid
- WSL and database-regression guards remain clean

## Explicit non-goals

This phase does not:

- run media probes
- create real media fixtures
- execute external binaries
- introduce scanner runtime behavior
- create CLI flags
- create report output
- create JSON output files
- create SaaS API behavior
- create background jobs
- create billing behavior
- create tenant storage behavior

## Result

This contract prepares a safe future implementation path for ffprobe failure handling.

It does not authorize ffprobe execution yet.
