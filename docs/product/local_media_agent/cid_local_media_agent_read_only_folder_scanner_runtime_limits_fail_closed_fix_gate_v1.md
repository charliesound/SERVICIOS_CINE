# CID Local Media Agent - Read Only Folder Scanner Runtime Limits Fail Closed Fix Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.RUNTIME_LIMITS.FAIL_CLOSED_FIX.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_RUNTIME_LIMITS_FAIL_CLOSED_FIX_GATE_V1_CLOSED`

## Defect discovered by QA

The adversarial QA gate found that monkeypatching `MAX_FILES=0` allowed the scanner to finish as completed instead of rejecting the runtime configuration or truncating fail-closed.

## Runtime SHA base

`9a10c9dba6d60b359ac5a4c06901b6c9313450ae727f2fb2cb3d761f707bf2fc`

## Scope

This phase is limited to exactly three files:

- `docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_runtime_limits_fail_closed_fix_gate_v1.md`
- `scripts/local_media_agent/read_only_folder_scanner.py`
- `tests/unit/test_cid_local_media_agent_read_only_folder_scanner_runtime_limits_fail_closed_fix_gate_v1.py`

This phase does not restore or modify QA archive files.

This phase does not modify `pyproject.toml`.

This phase does not create a CLI, `cid scan`, entrypoints, packaging, backend, frontend, DB, SaaS, Docker, Alembic, Stripe, auth, AI Jobs, or ledger changes.

This phase does not change the media extension allowlist.

This phase does not add media features.

## Fix contract

The runtime now validates internal limits at the start of `scan_read_only_folder`, before input root validation, path resolution, or filesystem traversal.

Valid runtime limit configuration is:

- `MAX_FILES` must be `int`, not `bool`, and greater than or equal to `1`.
- `MAX_ERRORS` must be `int`, not `bool`, and greater than or equal to `1`.
- `MAX_DEPTH` must be `int`, not `bool`, and greater than or equal to `0`.

Invalid runtime limits return immediately with:

- `status = READ_ONLY_FOLDER_SCAN_REJECTED`
- `errors = [RUNTIME_LIMIT_CONFIGURATION_REJECTED]`
- `files_seen = 0`
- `directories_seen = 0`
- `media_candidates = 0`
- `non_media_files = 0`
- `symlinks_rejected = 0`
- `total_bytes = 0`
- `truncated = false`

The rejected manifest remains sanitized and JSON-compatible.

The rejected manifest does not expose invalid values, constant names, paths, or raw exception text.

The invalid-limit path does not validate or resolve the input root, does not call `iterdir`, and does not call `lstat`.

## Normal behavior preserved

Normal scanner behavior remains unchanged for:

- `MAX_FILES = 5000`
- `MAX_DEPTH = 8`
- `MAX_ERRORS = 100`

`MAX_DEPTH=0` remains valid and permits only the validated root depth while rejecting entries at depth `1` before metadata is read.

## Next allowed phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.GATE.V1`

## Acceptance criteria

This fix gate can close only if:

- invalid `MAX_FILES`, `MAX_ERRORS`, and `MAX_DEPTH` configurations reject fail-closed;
- invalid-limit rejection occurs before input validation or filesystem traversal;
- invalid-limit manifests are sanitized and JSON-compatible;
- normal scanner behavior still works;
- implementation and readiness regression tests still pass;
- no unauthorized files or product areas are modified.
