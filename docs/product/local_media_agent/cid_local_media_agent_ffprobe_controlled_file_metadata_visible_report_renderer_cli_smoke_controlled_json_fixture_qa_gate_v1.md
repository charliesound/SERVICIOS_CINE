# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer CLI Smoke Controlled JSON Fixture QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.QA.GATE.V1`

## Objective

Validate that the existing controlled JSON fixture smoke test remains limited to controlled fixture data flowing through the existing local-only CLI and pure renderer into safe visible report output.

This QA gate does not add CLI functionality.

## Previous Required Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.V1`

## Required Source Files

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_json_fixture_v1.md`
- `tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_json_fixture.py`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`

## Validated Flow

The smoke fixture remains limited to:

controlled JSON fixture
to existing local-only CLI
to existing pure renderer
to safe visible report output

The pure renderer function remains:

`render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str`

## Fixture Requirements

The controlled smoke fixture must:

- be JSON
- parse into a dict
- be synthetic and controlled
- use `controlled_fixture_only` policy
- not contain real media metadata
- not contain real absolute paths
- not contain private material
- not contain real filenames
- not contain client names
- not contain project names
- not contain production names
- include redacted input marker only
- include controlled fixture marker
- keep safety flags false for real media, media processing, scanner execution, ffprobe execution, ffmpeg use, database write, network call, SaaS upload, audio extraction, sync, transcription, subtitles, timeline export, client-facing demo authorization, and production use authorization

## Smoke Test Requirements

The existing smoke test must validate:

- CLI stdout mode returns exit code 0
- CLI stdout contains safe visible report text
- CLI stdout includes only redacted input marker or redacted filename
- CLI stdout does not leak absolute paths
- CLI stdout does not contain private material
- CLI output-file mode writes a `.txt` or `.md` visible report
- output file content is safe
- fixture privacy and safety flags are checked

## Explicit Non-Authorization Boundaries

This QA gate does not authorize:

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

`PASS_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_SMOKE_CONTROLLED_JSON_FIXTURE_VALIDATED`

## Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_SMOKE_CONTROLLED_JSON_FIXTURE_QA_GATE_PASS_CLOSED`

## Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.CONTRACT.V1`
