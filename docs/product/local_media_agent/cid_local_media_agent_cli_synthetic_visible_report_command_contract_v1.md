# CID Local Media Agent — CLI Synthetic Visible Report Command Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.CONTRACT.V1`

## Objective

This phase defines the contract for the future CLI command that will invoke the already implemented synthetic Markdown visible report renderer.

This phase is documentation/test-only.

It does not implement CLI wiring, command registration, packaging, entry points, installer behavior, scanner integration, SaaS integration, backend integration, frontend integration, database integration, Docker integration, Alembic migration, HTML rendering, PDF rendering, DOCX rendering, XLSX rendering, CSV rendering, subtitle generation, DaVinci Resolve export, Avid export, Premiere export, OTIO export, EDL export, XML export, FCPXML export, external binary execution, media probing, media processing, real media processing, network behavior, licensing behavior, or production delivery behavior.

## Upstream Stable Baseline

Latest stable upstream commit:

`0d4e322`

Latest stable upstream tag:

`cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-visible-report-markdown-renderer-qa-gate-v1-20260618`

Renderer implementation:

`scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`

Renderer implementation QA gate:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_markdown_renderer_qa_gate_v1.md`

Renderer implementation test:

`tests/unit/test_cid_local_media_agent_synthetic_visible_report_markdown_renderer_implementation.py`

Renderer QA gate test:

`tests/unit/test_cid_local_media_agent_synthetic_visible_report_markdown_renderer_qa_gate.py`

Synthetic fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

## Future Command Name

The future command name should be:

`synthetic-visible-report`

The future command may later live under a CLI such as:

`cid-local-media-agent synthetic-visible-report`

or under a temporary development script command, if explicitly authorized by a later implementation phase.

This contract does not decide packaging or installable entry point implementation.

## Future Command Purpose

The future command should generate a local Markdown demo report from the controlled synthetic fixture.

The command must remain:

- synthetic-only
- local-only
- deterministic
- human-review gated
- non-destructive
- no-overwrite by default
- no network by default
- no media-processing by default
- no scanner integration by default
- no SaaS integration by default

## Future Allowed Inputs

The future command may accept only:

- `--fixture`
- `--output-dir`
- `--allow-overwrite`
- `--format markdown`

The first implementation should make `--format markdown` either implicit or strictly fixed.

The only allowed fixture basename is:

`synthetic_demo_report_fixture_v1.json`

The output directory must already exist and must be caller supplied.

The future command must not accept:

- source media directory
- client media directory
- private workspace directory
- recursive scan directory
- project root output by default
- repository output by default
- upload URL
- SaaS endpoint
- API token
- database URL
- installer flags
- licensing flags
- sync flags
- transcription flags
- translation flags
- NLE export flags

## Future Allowed Output

The future command may create only this Markdown file:

`cid_local_media_agent_synthetic_visible_report_v1.md`

The future command must not create:

- HTML
- PDF
- DOCX
- XLSX
- CSV
- SRT
- VTT
- XML
- FCPXML
- EDL
- OTIO
- MOV
- MP4
- WAV
- database records
- SaaS records
- logs containing private paths
- reports committed to the repository

## Future Exit Behavior

The future command should use deterministic exit behavior:

- exit success when the Markdown report is created safely
- exit failure when fixture basename is not allowed
- exit failure when fixture file does not exist
- exit failure when output directory does not exist
- exit failure when output directory is unsafe
- exit failure when output file already exists and overwrite is not explicitly allowed
- exit failure when requested format is not Markdown
- exit failure when any network, SaaS, scanner, media, subtitle, or NLE operation is requested

## Future User-Facing Messages

The future command should show concise user-facing messages.

Success message should include:

- generated filename
- synthetic demo status
- local-first privacy reminder
- human review reminder

Failure messages should avoid:

- stack traces by default
- absolute paths when not needed
- usernames
- machine names
- client identifiers
- real project identifiers
- raw JSON dumps
- scanner dumps
- external binary logs

## Future Safety Requirements

The future command must preserve the renderer safety guarantees:

- no source-media scanning
- no real media probing
- no real media processing
- no waveform sync
- no timecode sync
- no clap sync
- no transcription
- no translation
- no subtitle generation
- no DaVinci Resolve export
- no Avid export
- no Premiere export
- no OTIO export
- no EDL export
- no XML export
- no FCPXML export
- no external binary execution
- no network calls
- no SaaS calls
- no backend calls
- no frontend calls
- no database calls
- no Docker use
- no Alembic use
- no installer behavior
- no licensing behavior

## Future Help Text Requirements

The future help text must state clearly:

- this is a synthetic local demo command
- it does not analyze real media
- it does not synchronize real audio/video
- it does not transcribe real audio
- it does not translate real dialogue
- it does not generate final subtitles
- it does not export to NLE
- it does not upload client material
- human review is mandatory
- CID is assistive and not substitutive

## Future Implementation Recommendation

The future implementation should be done in a later phase:

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.READINESS.GATE.V1`

That phase should still be documentation/test-only and should decide if CLI wiring can be implemented.

Only after that should a real implementation phase be considered.

## Still Blocked After This Contract

The following remain blocked:

- CLI implementation
- packaging
- installable entry point
- scanner integration
- SaaS integration
- backend integration
- frontend integration
- database integration
- Docker integration
- Alembic migration
- installer behavior
- licensing behavior
- real media processing
- external binary execution
- subtitle generation
- NLE export
- committed report artifacts

## QA Status

`CLI_SYNTHETIC_VISIBLE_REPORT_COMMAND_CONTRACT_READY_FOR_VALIDATION`

Commit is blocked until target tests, related tests, staged scope safety check, fixture integrity check, renderer not modified check, scanner not modified check, WSL guard, and PostgreSQL-only regression guard pass.
