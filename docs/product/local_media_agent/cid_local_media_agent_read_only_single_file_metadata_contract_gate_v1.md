# CID Local Media Agent — Read-Only Single-File Metadata Contract Gate V1

## Gate identity

- phase: `CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CONTRACT.GATE.V1`
- result token: `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CONTRACT_GATE_V1_CLOSED`
- status: `CONTRACT_ONLY_DOC_TEST_GATE`
- decision: `READY_FOR_SEPARATE_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_READINESS_GATE_WITH_FIXTURE_BOUNDARIES`

## Purpose

This gate defines the read-only single-file metadata contract for the controlled non-customer fixture pack. It does not implement metadata extraction, it does not execute any external media tool, and it does not mutate the fixture pack.

The contract exists so that a later implementation readiness gate can be evaluated without ambiguity. The next allowed gate is a separate implementation readiness gate, not direct implementation.

## Dependency chain

This contract depends on the closed fixture chain:

1. `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1`
2. `CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1`
3. `CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.READINESS.GATE.V1`

## Fixture boundary

- fixture root: `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1`
- fixture file: `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`
- fixture id: `controlled_plain_text_marker_v1`
- expected bytes: `239`
- expected SHA256: `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`

The contract is limited to one exact fixture file. It does not authorize folder scanning, recursive traversal, batch processing, glob expansion, symbolic link following, or any other file discovery behavior.

## Input contract

A future implementation must accept a structured input object with these required fields:

- `fixture_root`: must equal `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1`
- `target_file`: must equal `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`
- `expected_fixture_id`: must equal `controlled_plain_text_marker_v1`
- `expected_bytes`: must equal `239`
- `expected_sha256`: must equal `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`
- `mode`: must equal `read_only_single_file_metadata`

The input contract must reject absolute paths outside the fixture root, parent traversal, wildcard paths, multiple files, hidden file discovery, customer material, and real production material.

## Output contract

A future implementation must return a deterministic result object. The result object must include:

- `status`
- `fixture_id`
- `target_file`
- `bytes`
- `sha256`
- `read_only`
- `scanner_used`
- `external_media_tool_used`
- `fixture_mutated`
- `customer_material_used`
- `metadata`
- `errors`

The success status must be `READ_ONLY_SINGLE_FILE_METADATA_CONTRACT_VERIFIED`.

The `metadata` object is limited to safe file-level metadata at this stage: file name, suffix, relative path under fixture root, byte size, and SHA256. Media-stream metadata, codec metadata, container metadata, duration, frame rate, audio stream count, and video stream count are not part of this contract.

## Failure modes

A future implementation must provide explicit failure modes for:

- `TARGET_FILE_MISSING`
- `TARGET_FILE_NOT_A_FILE`
- `TARGET_FILE_OUTSIDE_FIXTURE_ROOT`
- `TARGET_FILE_MULTIPLE_MATCHES_FORBIDDEN`
- `TARGET_FILE_BYTES_MISMATCH`
- `TARGET_FILE_SHA256_MISMATCH`
- `CUSTOMER_MATERIAL_FORBIDDEN`
- `REAL_PRODUCTION_MATERIAL_FORBIDDEN`
- `SCANNER_USAGE_FORBIDDEN`
- `EXTERNAL_MEDIA_TOOL_USAGE_FORBIDDEN`
- `FIXTURE_MUTATION_FORBIDDEN`

Failure objects must be deterministic and must not include absolute private machine paths. A redaction policy is required for any diagnostic text.

## Explicit non-goals

This contract gate does not authorize:

- execution of ffprobe
- execution of FFmpeg
- scanner implementation
- recursive folder traversal
- batch media processing
- video or audio fixture creation
- customer material
- real production material
- SaaS integration
- database integration
- backend or frontend changes
- installer work
- pyproject or dependency changes
- runtime command changes
- fixture mutation

## Safety invariants

The future implementation must prove these invariant values:

- `read_only` must be `true`
- `scanner_used` must be `false`
- `external_media_tool_used` must be `false`
- `fixture_mutated` must be `false`
- `customer_material_used` must be `false`
- `real_production_material_used` must be `false`

The contract must preserve the no-recursion policy, the no-batch policy, the no-customer-material policy, and the no-external-media-tool policy.

## Future safe chain order

1. Read-only single-file metadata contract gate.
2. Read-only single-file metadata implementation readiness gate.
3. Read-only single-file metadata implementation gate on the controlled fixture only.
4. Visible report over controlled fixture metadata.
5. Scanner minimum limited to the controlled fixture root, only after separate gates.

## Closure criteria

This gate may close only when the contract is documented, tested, committed, tagged, and pushed without adding implementation code, without running external media tools, and without modifying the controlled fixture pack.

Closure result: `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CONTRACT_GATE_V1_CLOSED`
