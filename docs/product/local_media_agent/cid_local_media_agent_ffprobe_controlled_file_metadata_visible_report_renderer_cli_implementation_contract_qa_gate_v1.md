# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer CLI Implementation Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.QA.GATE.V1`

## Objective

Validate the CLI implementation contract for a future local-only CLI wrapper around the already implemented pure renderer.

This QA gate does not implement CLI runtime.

## Previous Required Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.V1`

## Renderer Runtime Reference

Existing pure renderer runtime:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`

Existing pure renderer function:

`render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str`

## Required Source Files

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation_contract.py`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`

## Allowed Future CLI Behavior

The future CLI implementation contract only allows:

- receive a controlled JSON payload file
- parse that JSON safely
- pass the parsed dict to `render_controlled_ffprobe_metadata_visible_report(payload)`
- print or write returned human-readable visible report text
- preserve redaction boundaries
- fail closed on invalid JSON, missing required controlled payload fields, unsafe input path, or unsupported input type

The allowed behavior remains limited to controlled JSON payload to pure renderer to visible report text.

## Explicit Non-Authorization Boundaries

This QA gate and the next implementation must not allow:

- real media files
- arbitrary folders
- directory scanning
- scanner execution
- ffprobe execution
- ffmpeg execution
- subprocess/process execution
- audio extraction
- sync
- transcription
- subtitle generation
- timeline export
- network calls
- SaaS/DB access
- installer creation
- public demo
- sales demo
- client-facing demo
- production use

## QA Gate Decision

`PASS_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_IMPLEMENTATION_CONTRACT_VALIDATED`

## Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_IMPLEMENTATION_CONTRACT_QA_GATE_PASS_CLOSED`

## Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.V1`
