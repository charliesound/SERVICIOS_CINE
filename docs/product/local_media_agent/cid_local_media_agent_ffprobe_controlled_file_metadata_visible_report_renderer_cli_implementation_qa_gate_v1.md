# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer CLI Implementation QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.QA.GATE.V1`

## Objective

Validate that the controlled CLI implementation remains a safe local-only wrapper around the already implemented pure renderer.

This QA gate does not add CLI functionality.

## Previous Required Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.V1`

## Required Source Files

- `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`
- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation.py`

## Pure Renderer Contract

The CLI implementation must remain limited to the pure renderer:

`render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str`

## Allowed CLI Behavior

The existing CLI only allows:

- receive a controlled JSON payload file
- reject directory input
- reject non-json input
- parse JSON safely
- require a dict payload
- call `render_controlled_ffprobe_metadata_visible_report(payload)`
- print returned report text to stdout
- optionally write returned report text to a safe `.txt` or `.md` output path
- preserve redaction boundaries
- fail closed on invalid JSON, missing input, directory input, unsupported suffix, non-dict JSON, unsafe output suffix, or renderer failure
- return deterministic exit codes

The allowed behavior remains limited to controlled JSON payload to pure renderer to visible report text.

## Explicit Non-Authorization Boundaries

The CLI still does not allow:

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

`PASS_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_IMPLEMENTATION_VALIDATED`

## Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_IMPLEMENTATION_QA_GATE_PASS_CLOSED`

## Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.V1`
