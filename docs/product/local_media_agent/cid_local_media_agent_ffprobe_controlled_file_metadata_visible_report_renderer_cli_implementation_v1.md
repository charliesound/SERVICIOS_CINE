# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer CLI Implementation v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.V1`

## Objective

Implement a safe local-only CLI wrapper around the existing pure controlled metadata visible report renderer.

The CLI reads only controlled JSON payload files, calls the pure renderer, and prints or writes the returned human-readable visible report text.

## Previous Required Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.QA.GATE.V1`

## Runtime API

CLI module:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py`

Renderer module:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`

Renderer function:

`render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str`

## CLI Behavior

The CLI implementation:

- accepts a path to a controlled JSON payload file only
- requires the input path to be a file, not a directory
- requires the input path to have `.json` suffix
- parses JSON safely
- requires the parsed payload to be a dict
- requires required controlled payload fields
- calls `render_controlled_ffprobe_metadata_visible_report(payload)`
- prints the returned visible report text to stdout by default
- optionally writes returned report text to an explicit `.txt` or `.md` output path
- fails closed on invalid JSON, missing file, directory input, unsupported input suffix, non-dict JSON payload, unsafe output path, or renderer failure
- returns deterministic exit codes: `0` on success and non-zero on controlled failure

## Non-Authorization Boundaries

The CLI implementation does not allow:

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

## Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_IMPLEMENTATION_PASS_READY_FOR_QA_GATE`

## Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.QA.GATE.V1`
