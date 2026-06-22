# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer CLI Visible Report Output Smoke Controlled Fixture v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.SMOKE.CONTROLLED.FIXTURE.V1`

## Objective

Create a controlled smoke test of visible output that validates the visible report generated from the existing controlled JSON fixture complies with the already closed visible output contract.

This phase uses only a controlled JSON fixture and the existing pure renderer.

It does not use real media, scanner, real ffprobe, ffmpeg, subprocess/process execution, network, or SaaS/DB.

This is a controlled smoke test.

## Previous Closed Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.CONTRACT.QA.GATE.V1`

## Authorized Chain

The only authorized chain remains:

controlled synthetic JSON fixture
-> existing local-only CLI
-> existing pure renderer
-> safe visible report text

## Required Files

- `tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json`
- `tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture.py`
- `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py`

## Smoke Test Behavior

This smoke test:

- loads the existing controlled JSON fixture
- calls the existing pure renderer function directly
- compares the output against the controlled expected visible report fixture
- validates that the visible report is safe, deterministic, and contract-compliant

This smoke test does not execute the CLI.

This smoke test does not execute real ffprobe.

This smoke test does not execute ffmpeg.

This smoke test does not use subprocess/process execution.

This smoke test does not use real media.

This smoke test does not use network.

This smoke test does not use SaaS/DB.

## Explicit Non-Authorization Boundaries

This phase does not authorize:

- real media
- scanner execution
- real ffprobe execution
- ffmpeg
- subprocess/process execution
- audio extraction
- sync
- transcription
- subtitles
- timeline export
- network
- SaaS/DB
- installer
- public demo
- client demo
- sales demo
- production use

## Functional Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_SMOKE_CONTROLLED_FIXTURE_PASS_READY_FOR_QA_GATE`

## Future Target Tag

`cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-smoke-controlled-fixture-v1-20260622`

## Next Microphase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.SMOKE.CONTROLLED.FIXTURE.QA.GATE.V1`
