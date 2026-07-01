# CID Local Media Agent — Read-Only Single-File Metadata Implementation QA Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.IMPLEMENTATION.QA.GATE.V1`

## Result token

`LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_QA_GATE_V1_CLOSED`

## Purpose

This gate audits the isolated read-only single-file metadata implementation before any product CLI, scanner, batch workflow, external media tool, SaaS/database integration, installer, or customer-material path is allowed to depend on it.

The implementation under QA is:

`scripts/local_media_agent/read_only_single_file_metadata.py`

The only controlled target remains:

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`

Expected bytes:

`239`

Expected SHA256 from `manifest.controlled.json`:

`a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`

## QA scope

This gate verifies that the implementation:

1. uses `python_standard_library_only`;
2. exposes `collect_read_only_single_file_metadata` and `run_cli`;
3. produces `CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK` for the controlled fixture;
4. produces `CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_REJECTED` for deterministic contract violations;
5. redacts host-private absolute paths;
6. reports only the controlled relative path and `<CONTROLLED_FIXTURE_ROOT>` redacted path;
7. keeps `external_tools_used`, `scanner_used`, `recursion_used`, and `batch_used` false;
8. rejects target paths outside the controlled fixture root;
9. rejects missing targets deterministically;
10. rejects byte mismatch deterministically;
11. rejects SHA256 mismatch deterministically;
12. keeps the fixture pack unchanged.

## Explicit non-goals

This gate does not add or authorize:

- ffprobe execution;
- FFmpeg execution;
- directory scanner behavior;
- recursive traversal;
- batch mode;
- real media analysis;
- customer material;
- pyproject entrypoints;
- SaaS/database integration;
- backend/frontend changes;
- installer changes;
- fixture modifications.

## Acceptance decision

`IMPLEMENTATION_QA_PASS_FOR_CONTROLLED_SINGLE_FILE_METADATA_ONLY`

A later gate may prepare CLI integration only after this QA gate is closed and only if the same boundaries remain active.
