# CID Local Media Agent — Scanner CLI ffprobe Command Wrapper QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.QA.GATE.V1`

## Objective

This phase audits the existing ffprobe command wrapper contract before any future implementation work.

The result of this phase is a documentary and test-only QA gate. It does not implement a wrapper, does not execute media tooling, does not add external process execution, and does not modify the scanner runtime.

## Source contracts audited

This QA gate depends on the following previous safe phases:

- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_contract_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md`
- `docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_qa_gate_v1.md`

## Scope

Allowed in this phase:

- Create this QA gate document.
- Create a unit test that validates the QA gate contract.
- Read existing contract documents.
- Read the scanner script as text for static safety checks.
- Run Python unit tests and repository guards.

Forbidden in this phase:

- No ffprobe execution.
- No media transcoding tool execution.
- No external process execution API added to runtime.
- No real media processing.
- No real media creation.
- No scanner runtime modification.
- No SaaS backend modification.
- No database, Alembic, Docker, frontend, billing, workers, queue, storage, or cloud changes.

## QA checks

### CW-QA-001 — Wrapper contract exists

The command wrapper contract must exist before this QA gate is considered valid.

### CW-QA-002 — Previous failure-path gates remain referenced

The QA gate must explicitly reference both the failure-path contract and the failure-path QA gate.

### CW-QA-003 — Structured input requirement is preserved

The wrapper contract must remain based on structured inputs rather than ad-hoc command text.

### CW-QA-004 — Shell strings remain forbidden

The wrapper contract must prohibit shell strings and must require a command argument list.

### CW-QA-005 — Timeout policy is mandatory

The wrapper contract must define timeout behavior for future ffprobe calls.

### CW-QA-006 — stdout and stderr redaction is mandatory

The wrapper contract must define safe redaction rules for stdout and stderr before report or log exposure.

### CW-QA-007 — Safe result shape is mandatory

The wrapper contract must define a safe normalized result shape for success and failure cases.

### CW-QA-008 — Failure-path error codes must be preserved

The wrapper contract must preserve the error code vocabulary from the failure-path contract.

### CW-QA-009 — Real media remains blocked

This gate does not allow real media files, real audiovisual material, production footage, client media, or private pilot material.

### CW-QA-010 — Scanner runtime remains untouched

The scanner runtime must not be modified by this phase.

### CW-QA-011 — Scanner runtime must remain free of external execution calls

The scanner runtime must remain free of reconstructed runtime execution tokens for process run calls, process Popen calls, and media transcoding command usage.

### CW-QA-012 — No sensitive literals or blocked database fallback language

This QA gate must not introduce secrets, credentials, private keys, local environment values, or blocked database fallback language.

### CW-QA-013 — Implementation remains blocked

Passing this QA gate does not authorize implementation of the wrapper. It only authorizes a later explicit implementation phase.

## Gate decision

`PASS_DOC_TEST_ONLY_QA_GATE_READY_FOR_FUTURE_IMPLEMENTATION_PHASE`

This means:

- The command wrapper contract can be treated as audited at documentary level.
- A later implementation phase may be proposed.
- No implementation is authorized by this phase.
- No ffprobe or media processing execution is authorized by this phase.
