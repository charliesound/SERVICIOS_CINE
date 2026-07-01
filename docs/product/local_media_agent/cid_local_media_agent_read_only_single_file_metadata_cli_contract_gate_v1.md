# CID Local Media Agent — Read-Only Single-File Metadata CLI Contract Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTRACT.GATE.V1`

## Result token

`LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTRACT_GATE_V1_CLOSED`

## Gate type

Documentation and test only.

This gate defines the contract for a future isolated command-line entrypoint around the already audited read-only single-file metadata implementation. It does not create the command, does not register any console script, and does not change packaging configuration.

## Prior stable dependencies

This gate depends on these closed states:

- `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_READINESS_GATE_V1_CLOSED`
- `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_QA_GATE_V1_CLOSED`
- `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_GATE_V1_CLOSED`
- `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_READINESS_GATE_V1_CLOSED`
- `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CONTRACT_GATE_V1_CLOSED`
- `LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_READINESS_GATE_V1_CLOSED`
- `LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_INTEGRITY_QA_GATE_V1_CLOSED`

## Future isolated entrypoint placeholder

`cid-local-media-agent-read-only-single-file-metadata`

This name is contractual only in this gate. It must not be registered in project packaging until a separate implementation gate authorizes it.

## Controlled fixture boundary

The future CLI may only target this controlled fixture during the initial implementation line:

`tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt`

Expected identity:

- bytes: `239`
- sha256: `a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a`
- fixture root: `tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1`
- allowed relative path: `media/controlled_plain_text_marker.txt`

## Allowed future CLI arguments

The future CLI contract allows only these arguments in the initial isolated implementation:

- `--target-path`
- `--fixture-root`
- `--expected-sha256`
- `--expected-bytes`
- `--result-json`

No other operational argument is approved by this contract.

## Required future success behavior

The future CLI must support two output modes.

### JSON mode

When `--result-json` is present and validation succeeds, stdout must contain parseable JSON with:

- `ok: true`
- `status: READ_ONLY_SINGLE_FILE_METADATA_COLLECTED`
- `mode: READ_ONLY_SINGLE_FILE_METADATA`
- `target.file_name`
- `target.extension`
- `target.relative_path`
- `target.redacted_path`
- `target.bytes`
- `target.sha256`
- `target.is_file`
- `safety.python_standard_library_only: true`
- `safety.external_media_tools_used: false`
- `safety.scanner_used: false`
- `safety.batch_used: false`
- `safety.recursion_used: false`

### Plain mode

When `--result-json` is absent and validation succeeds, stdout must contain a status-only success line:

`READ_ONLY_SINGLE_FILE_METADATA_COLLECTED`

Plain output must not print absolute local paths.

## Required future exit codes

- exit code `0`: success
- exit code `2`: deterministic validation rejection

The contract intentionally does not define additional exit codes in this phase.

## Required deterministic rejection reasons

The future CLI must preserve deterministic rejection reasons from the audited implementation:

- `TARGET_OUTSIDE_CONTROLLED_FIXTURE_ROOT`
- `TARGET_RELATIVE_PATH_NOT_ALLOWED`
- `TARGET_IS_SYMLINK`
- `TARGET_NOT_FOUND`
- `TARGET_BYTES_MISMATCH`
- `TARGET_SHA256_MISMATCH`

Every rejection response must avoid leaking private absolute paths.

## Path redaction contract

All success and error payloads must use this redaction style:

`<CONTROLLED_FIXTURE_ROOT>/media/controlled_plain_text_marker.txt`

The CLI must not print the absolute repository path, user home path, or temp extraction path.

## Explicit prohibitions

This CLI contract does not authorize:

- batch mode
- recursive traversal
- scanner integration
- ffprobe execution
- FFmpeg execution
- external media tool execution
- real media processing
- customer material
- fixture modification
- packaging registration
- console script registration
- installer work
- SaaS integration
- backend integration
- frontend integration

## Staged scope allowed by this gate

Only these files may be staged by this gate:

- `docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py`

## Decision

`READY_FOR_SEPARATE_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_READINESS_GATE_WITH_ISOLATED_ENTRYPOINT_CONTRACT`

## Next allowed phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.IMPLEMENTATION.READINESS.GATE.V1`

That future phase may review whether to implement the isolated entrypoint, but it must still avoid product-wide integration unless another explicit gate authorizes it.
