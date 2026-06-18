# CID Local Media Agent — Scanner CLI ffprobe Command Wrapper Implementation Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.IMPLEMENTATION.READINESS.GATE.V1`

## Objective

This phase decides whether the ffprobe command wrapper line is ready to propose a future explicit minimal implementation phase.

This is a documentary and test-only readiness gate. It does not implement the wrapper, does not execute ffprobe, does not execute ffmpeg, does not add process execution code, does not process media, and does not modify scanner runtime.

## Previous stable chain

This readiness gate depends on the following audited chain:

- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_qa_gate_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_contract_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_qa_gate_v1.md`

## Scope

Allowed in this phase:

- Create this readiness gate document.
- Create a unit test that validates this readiness gate.
- Read existing Local Media Agent contracts as text.
- Read the scanner runtime as text for static safety checks.
- Run unit tests and repository guards.

Forbidden in this phase:

- No wrapper implementation.
- No ffprobe execution.
- No ffmpeg execution.
- No real media processing.
- No real media creation.
- No process execution code added to runtime.
- No scanner runtime modification.
- No SaaS backend modification.
- No database, Alembic, Docker, frontend, billing, workers, queue, storage, or cloud changes.
- No private pilot material.
- No client footage.
- No production footage.

## Readiness checks

### IRG-001 — Failure-path contract exists

The failure-path contract must exist and define the future failure vocabulary before implementation can be proposed.

### IRG-002 — Failure-path QA gate exists

The failure-path QA gate must exist and must have audited the failure-path contract.

### IRG-003 — Command wrapper contract exists

The command wrapper contract must exist and define the future wrapper behavior.

### IRG-004 — Command wrapper QA gate exists

The command wrapper QA gate must exist and must have audited the wrapper contract.

### IRG-005 — Structured inputs remain mandatory

A future implementation phase must accept structured inputs. It must not accept arbitrary command text from users, reports, filenames, labels, metadata, or external agents.

### IRG-006 — Command argument list remains mandatory

A future implementation phase must build a command argument list. Shell command strings remain forbidden.

### IRG-007 — Timeout remains mandatory

A future implementation phase must define a bounded timeout and convert timeout behavior into a safe normalized failure result.

### IRG-008 — stdout and stderr redaction remains mandatory

A future implementation phase must redact stdout and stderr before exposing any output to reports, logs, UI, JSON, Markdown, or operator-facing diagnostics.

### IRG-009 — Failure-path error codes remain mandatory

A future implementation phase must preserve the error code vocabulary defined by the failure-path contract.

### IRG-010 — Safe result shape remains mandatory

A future implementation phase must return a normalized safe result object for both success and failure.

### IRG-011 — Real media remains blocked for the next phase

The next phase after this readiness gate must still use synthetic fixtures, mocks, contract-level checks, or static text inspection. It must not use real media.

### IRG-012 — Scanner runtime remains untouched by this gate

This readiness gate must not modify `scripts/cid_media_agent_scan.py`.

### IRG-013 — Implementation must be explicit and separate

Passing this readiness gate does not authorize implementation. Any implementation must be opened as a separate phase with its own scope, no-goals, tests, guards, and human approval.

### IRG-014 — Future implementation must be minimal

The future implementation phase, if approved, should be minimal and isolated. It should avoid broad scanner integration, SaaS integration, UI work, database work, storage work, billing work, workers, queues, Docker, or cloud changes.

### IRG-015 — Future implementation should start with test doubles

The safest next implementation-oriented step should use test doubles or a command-runner abstraction before any real ffprobe execution is allowed.

## Gate decision

`PASS_READY_TO_PROPOSE_EXPLICIT_MINIMAL_WRAPPER_IMPLEMENTATION_PHASE`

Meaning:

- The contract chain is ready enough to propose a future minimal implementation phase.
- The future implementation phase is not automatically authorized.
- The next phase must remain explicit, narrow, reviewable, and guarded.
- Real ffprobe execution remains blocked until a later explicit authorization.
- Real media remains blocked.
- Scanner runtime integration remains blocked until a later explicit integration phase.

## Recommended next phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.V1`

Rationale:

Before adding any real process execution, define the test-double boundary for the future wrapper. This keeps the project safe, allows deterministic tests, and avoids accidental media tooling execution.
