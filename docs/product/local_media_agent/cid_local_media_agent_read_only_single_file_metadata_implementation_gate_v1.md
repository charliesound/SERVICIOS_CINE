# CID Local Media Agent — Read-Only Single-File Metadata Implementation Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.IMPLEMENTATION.GATE.V1`

## Result token

`LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_GATE_V1_CLOSED`

## Purpose

This gate adds the first minimal implementation for read-only metadata collection over exactly one controlled non-customer fixture file. The implementation is intentionally isolated, deterministic, and limited to Python standard library functionality.

The implementation does not inspect media streams. It only reads basic file properties that can be derived safely from the filesystem and a SHA256 digest over the controlled fixture.

## New implementation file

`scripts/local_media_agent/read_only_single_file_metadata.py`

## Target fixture

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`

Expected fixture identity inherited from the audited fixture pack:

```text
fixture_id: controlled_plain_text_marker_v1
bytes: 239
sha256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a
```

## Allowed behavior

The implementation may:

1. Resolve a supplied fixture root.
2. Resolve a supplied target path.
3. Verify that the target is inside the fixture root.
4. Verify that the relative path is exactly `media/controlled_plain_text_marker.txt`.
5. Read only file size and SHA256 from the target file.
6. Return deterministic JSON-compatible data.
7. Redact host-private absolute paths.
8. Return deterministic rejected results for contract violations.

## Output contract

A successful result must include:

```text
schema_version: cid.local_media_agent.read_only_single_file_metadata.v1
status: CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK
ok: true
mode: read_only_single_file
tool_policy: python_standard_library_only
external_tools_used: false
scanner_used: false
recursion_used: false
batch_used: false
```

The successful target block must expose only controlled path information:

```text
file_name: controlled_plain_text_marker.txt
extension: .txt
relative_path: media/controlled_plain_text_marker.txt
redacted_path: <CONTROLLED_FIXTURE_ROOT>/media/controlled_plain_text_marker.txt
```

The metadata block must expose:

```text
bytes
sha256
is_file
```

## Rejected result contract

A rejected result must use:

```text
status: CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_REJECTED
ok: false
```

Allowed deterministic reasons include:

```text
FIXTURE_ROOT_SYMLINK_REJECTED
FIXTURE_ROOT_NOT_FOUND
TARGET_SYMLINK_REJECTED
TARGET_FILE_NOT_FOUND
TARGET_OUTSIDE_CONTROLLED_FIXTURE_ROOT
TARGET_RELATIVE_PATH_NOT_ALLOWED
TARGET_BYTES_MISMATCH
TARGET_SHA256_MISMATCH
```

Rejected results must not leak host-private absolute paths.

## Explicit prohibitions

This gate does not authorize:

1. ffprobe or FFmpeg execution.
2. Scanner execution.
3. Recursive traversal.
4. Batch metadata collection.
5. Processing real media.
6. Processing customer material.
7. Reading production folders.
8. Writing metadata artifacts outside normal test/runtime stdout behavior.
9. Runtime integration with existing product commands.
10. SaaS, database, backend, frontend, installer, packaging, license, or activation changes.
11. Dependency or project configuration changes.
12. Modification of the fixture pack.

## CLI boundary

The implementation exposes a small CLI for isolated manual validation:

```bash
python scripts/local_media_agent/read_only_single_file_metadata.py \
  --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt \
  --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 \
  --expected-sha256 <fixture_sha256> \
  --expected-bytes <fixture_bytes> \
  --result-json
```

The CLI is not a scanner and must only process one explicitly supplied target path.

## Validation requirements

The implementation gate must validate:

1. The implementation file exists.
2. The implementation uses only Python standard library imports.
3. The implementation does not call external media tools.
4. The controlled fixture exists.
5. The controlled fixture manifest references the actual fixture digest and size.
6. A successful metadata result is deterministic.
7. Returned paths are redacted.
8. Outside-root targets are rejected.
9. Wrong relative paths are rejected.
10. Wrong bytes are rejected.
11. Wrong SHA256 is rejected.
12. The CLI emits JSON and returns non-zero for rejected targets.

## Closure statement

This gate is closed only when the isolated Python-standard-library implementation, its direct tests, prior safety gates, WSL guard, and staged-diff guards pass, and only the implementation file, this document, and the implementation test are staged.

Closure does not authorize media probing, scanner work, customer material, runtime integration, or packaging.
