# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer CLI Implementation Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.V1`

## Objective

Define the expected future implementation behavior for a local-only CLI wrapper around the already implemented pure controlled ffprobe metadata visible report renderer.

This is an implementation contract only.

No CLI runtime is implemented in this phase.

No runtime scripts are modified in this phase.

## Previous Required Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.CONTRACT.QA.GATE.V1`

## Renderer Runtime Reference

Existing pure renderer runtime:

`scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`

Existing pure renderer function:

`render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str`

## Future CLI Input Contract

The future CLI input must be a controlled JSON payload file only.

The input payload must already be safe and controlled before the CLI passes it to the pure renderer.

The future CLI must fail closed for:

- invalid JSON
- missing required controlled payload fields
- unsafe input path
- unsupported input type
- real media files
- arbitrary folders

## Future CLI Allowed Behavior

The future CLI behavior is limited to:

- receive a path to a controlled JSON payload
- parse that JSON safely
- pass the parsed dict to `render_controlled_ffprobe_metadata_visible_report(payload)`
- print or write the returned human-readable visible report text
- preserve redaction boundaries
- fail closed on invalid JSON, missing required controlled payload fields, unsafe input path, or unsupported input type

## Future CLI Blocked Capabilities

The future CLI must not:

- accept real media files
- accept arbitrary folders
- scan directories
- execute ffprobe
- execute ffmpeg
- execute subprocess/process commands
- perform audio extraction
- perform sync
- perform transcription
- generate subtitles
- export timelines
- call network services
- access SaaS/DB
- create installers
- be public-demo ready
- be sales-demo ready
- be client-facing ready
- be production-ready

## Output Contract

The future CLI may print the returned human-readable visible report text to stdout.

The future CLI may write the returned report text only to a controlled output target in a future explicitly authorized phase.

The future CLI must preserve all redaction boundaries from the pure renderer.

## Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE`

## Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.QA.GATE.V1`
