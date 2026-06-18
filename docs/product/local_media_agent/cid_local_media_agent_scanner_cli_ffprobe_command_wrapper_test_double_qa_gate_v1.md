# CID Local Media Agent — ffprobe Command Wrapper Test Double QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.QA.GATE.V1`

## Objective

This QA gate audits the ffprobe command wrapper test double contract before any future implementation of a command-runner boundary.

The gate checks that the contract is safe, deterministic, privacy-preserving, compatible with the failure path vocabulary, and explicitly blocks real command execution.

This phase is documentation/test-only. It does not implement the test double, does not implement the wrapper, does not execute ffprobe, does not execute ffmpeg, does not add subprocess usage, and does not modify scanner runtime.

## Inputs audited

This gate audits:

- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.V1`
- `CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.SANITIZED.V1`

The audited contract file is:

`docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_contract_v1.md`

The audited unit test file is:

`tests/unit/test_cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_contract.py`

## Required QA findings

The contract is accepted only if all of the following are true:

- The test double boundary is explicit.
- The future command runner is injectable.
- Unit tests must use the test double.
- Real executable access remains outside unit tests.
- Real executable access requires a separate explicit gate.
- All required simulation modes are declared.
- All failure path vocabulary is covered.
- The result shape is structured and safe.
- Determinism is required.
- Privacy restrictions are explicit.
- Raw commands must remain hidden.
- Redaction must be required.
- Safe report labels must be required.
- Real media metadata must not be emitted.
- Real filenames and absolute paths must not be emitted.
- No implementation is authorized by this gate.
- No runtime scanner file is modified by this gate.

## Required simulation coverage

The QA gate requires the test double contract to cover:

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

## Runtime prohibition

This QA gate does not authorize:

- command execution
- ffprobe execution
- ffmpeg execution
- subprocess usage
- shell execution
- reading real media files
- scanning real client folders
- changing `scripts/cid_media_agent_scan.py`
- changing files under `src/`
- changing backend, frontend, Alembic, Docker, billing, workers, queue, storage, or cloud behavior

## Acceptance decision

This QA gate passes only when the contract can be considered safe enough to prepare a future test-double implementation phase.

Passing this QA gate does not authorize real ffprobe execution.

Passing this QA gate does not authorize scanner runtime changes.

Passing this QA gate only authorizes a future test-double implementation planning phase or a minimal test-double implementation behind a separate explicit gate.

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.IMPLEMENTATION.READINESS.GATE.V1`
