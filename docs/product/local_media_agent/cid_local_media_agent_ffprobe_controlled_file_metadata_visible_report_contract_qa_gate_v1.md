# CID Local Media Agent - FFprobe Controlled Metadata Visible Report Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1`

## Objective

Validate the visible report contract for controlled ffprobe metadata.

This QA gate confirms that the visible report contract defines a safe human-readable report derived only from controlled metadata JSON.

## Source Stable State

HEAD:

`06c1dd031b8985e56214624a60423bea10f0fd91`

Commit:

`docs: add CID Local Media Agent ffprobe visible report contract`

Tag:

`cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-contract-v1-20260622`

## Source Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.V1`

## Required Source Files

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract.py`

## Required Validated Contract

The visible report contract must define these safe report sections:

- report title
- phase
- input policy
- redacted input filename
- preflight result
- format summary
- stream summary
- video stream summary
- audio stream summary
- safety boundary summary
- blocked operations summary
- human review required note
- next safe phase

## Required Report Boundaries

The visible report contract must forbid:

- full local paths
- real rodaje material references
- raw private file locations
- scanner output
- media processing output
- audio extraction output
- sync output
- transcription output
- subtitle output
- timeline output
- SaaS identifiers
- database identifiers
- installer claims
- client-facing claims
- public demo claims
- sales demo claims
- production use claims

## Required Safe Inputs

The visible report contract must require:

- `input_path_redacted` as filename only
- `input_policy` equal to `controlled_fixture_only`
- `ffprobe_command_kind` equal to `metadata_json`
- `metadata.format` as null or object
- `metadata.streams` as a list
- all blocked execution flags remaining false
- safe report behavior even when preflight result is failure
- no full path leakage

## Required Boundaries

This QA gate does not authorize:

- runtime report rendering
- real rodaje material
- real media files
- arbitrary folders
- scanner execution
- media processing
- audio extraction
- sync generation
- transcription generation
- subtitle generation
- timeline export
- SaaS upload
- database writes
- installer creation
- client-facing use
- public demo
- sales demo
- production use

## Validation Evidence Required

This QA gate is accepted only with:

- visible report contract QA gate test passing
- visible report contract test passing
- second fixture scenario QA gate test passing
- py_compile passing
- source stable state declared
- required source files present
- acceptance result declared
- next safe phase declared
- no runtime script staged
- diff check passing
- WSL/repo guard passing
- database backend regression guard passing
- no protected files staged

## QA Gate Decision

`PASS_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_CONTRACT_VALIDATED`

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_CONTRACT_QA_GATE_PASS_CLOSED`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.V1`
