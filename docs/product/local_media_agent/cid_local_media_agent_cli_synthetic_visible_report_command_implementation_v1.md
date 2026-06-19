# CID Local Media Agent — CLI Synthetic Visible Report Command Implementation v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.V1`

## Objective

This phase implements the first minimal development CLI wrapper for the synthetic visible report command.

The wrapper calls the existing synthetic Markdown visible report renderer.

## Upstream Authorization

Readiness gate:

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.READINESS.GATE.V1`

Commit:

`6d267c4`

Decision:

`READY_FOR_MINIMAL_CLI_WIRING_IMPLEMENTATION_WITH_RESTRICTIONS`

## Files Created

Implementation:

`scripts/cid_local_media_agent_synthetic_visible_report_cli.py`

Test:

`tests/unit/test_cid_local_media_agent_cli_synthetic_visible_report_command_implementation.py`

## Scope

Allowed:

- development CLI wrapper
- standard library only
- isolated script
- direct call to existing renderer
- command concept `synthetic-visible-report`
- allowed inputs `--fixture`, `--output-dir`, `--allow-overwrite`, `--format markdown`
- deterministic Markdown output filename `cid_local_media_agent_synthetic_visible_report_v1.md`
- concise safe success/failure messages
- no overwrite by default
- expected user errors return code 2
- help returns code 0
- success returns code 0

## No Goals

This phase does not implement:

- packaging
- installable entry point
- pyproject changes
- setup.py changes
- setup.cfg changes
- scanner integration
- scanner runtime changes
- SaaS integration
- backend integration
- frontend integration
- database integration
- Docker integration
- Alembic migration
- HTML rendering
- PDF rendering
- DOCX rendering
- XLSX rendering
- CSV rendering
- subtitle generation
- DaVinci Resolve export
- Avid export
- Premiere export
- OTIO export
- EDL export
- XML export
- FCPXML export
- external binary execution
- media probing
- video analysis
- audio analysis
- waveform sync
- timecode sync
- clap sync
- transcription
- translation
- real media processing
- private media processing
- client media upload
- network behavior
- licensing behavior
- installer behavior

## Runtime Safety

The wrapper:

- imports only standard library modules
- loads the existing renderer locally
- does not import or call scanner code
- does not expose media path arguments
- does not expose upload arguments
- does not expose sync, transcription, translation, subtitle, NLE, installer, licensing, database, backend, frontend, or SaaS options
- does not print fixture absolute paths in normal output
- does not print output directory absolute paths in normal output
- does not print stack traces for expected user errors

## User-Facing CLI Messages

Success message includes:

- generated filename
- synthetic demo reminder
- local-first reminder
- human review reminder
- no real media analysis reminder
- no client material upload reminder

Failure messages are intentionally generic and do not reveal private paths.

## QA Status

`CLI_SYNTHETIC_VISIBLE_REPORT_COMMAND_IMPLEMENTATION_V1_READY_FOR_VALIDATION`

Commit is blocked until target tests, related tests, staged scope safety check, fixture integrity check, renderer not modified check, scanner not modified check, packaging not modified check, runtime safety static check, WSL guard, and PostgreSQL-only regression guard pass.
