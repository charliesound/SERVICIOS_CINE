# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer CLI Smoke Controlled JSON Fixture v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.V1`

## Objective

Validate the existing controlled CLI with a synthetic controlled JSON payload fixture.

This phase uses only a controlled JSON payload fixture.

It does not use real media metadata, real shoot material, private material, real filenames, real absolute paths, client names, project names, or production names.

## Previous Required Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.QA.GATE.V1`

## Required Files

- `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`
- `tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json`

## Controlled Fixture Contract

The fixture is a synthetic controlled metadata payload only.

The fixture includes:

- phase
- `input_policy` equal to `controlled_fixture_only`
- `input_path_redacted`
- synthetic format summary
- synthetic streams summary
- safe flags showing no media processing, no scanner, no ffmpeg, no database, no network
- controlled fixture marker

## Smoke Behavior

The smoke test executes the CLI only against the controlled JSON fixture.

It validates stdout mode and temporary `.txt` or `.md` output-file mode.

## Explicit Non-Authorization Boundaries

This phase does not authorize:

- real media file use
- arbitrary folder use
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

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_SMOKE_CONTROLLED_JSON_FIXTURE_PASS_READY_FOR_QA_GATE`

## Next Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.QA.GATE.V1`
