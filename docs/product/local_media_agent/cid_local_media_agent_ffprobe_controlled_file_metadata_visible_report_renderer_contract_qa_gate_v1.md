# CID Local Media Agent - FFprobe Controlled Metadata Visible Report Renderer Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.QA.GATE.V1`

## Objective

Validate the visible report renderer contract for controlled ffprobe metadata.

This QA gate confirms that the renderer contract defines how a future renderer should convert already-safe controlled metadata JSON into a human-readable report without opening runtime rendering or real media use.

## Source Stable State

HEAD:

`46aeb2e58d3e32f518921745f5a38666d071df5a`

Commit:

`docs: add CID Local Media Agent ffprobe visible report renderer contract`

Tag:

`cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-contract-v1-20260622`

## Source Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.V1`

## Required Source Files

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract.py`
- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_qa_gate.py`

## Required Validated Contract

The renderer contract must define a future renderer that:

- accepts only already-safe controlled metadata payloads
- rejects or safely reports payloads with invalid input policy
- uses only redacted input filename
- requires metadata JSON command kind
- renders report title
- renders phase
- renders input policy
- renders redacted input filename
- renders preflight result
- renders format summary
- renders stream summary
- renders video stream summary
- renders audio stream summary
- renders safety boundary summary
- renders blocked operations summary
- renders human review required note
- renders next safe phase
- handles null format safely
- handles empty streams safely
- never exposes full local paths
- never includes private rodaje details
- never claims readiness for client-facing, public demo, sales demo, or production use

## Required Boundaries

This QA gate does not authorize:

- runtime renderer implementation
- real rodaje material
- real media files
- arbitrary folders
- scanner execution
- ffprobe execution on real media
- ffmpeg media processing
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

- visible report renderer contract QA gate test passing
- visible report renderer contract test passing
- visible report contract QA gate test passing
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

`PASS_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CONTRACT_VALIDATED`

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CONTRACT_QA_GATE_PASS_CLOSED`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.V1`
