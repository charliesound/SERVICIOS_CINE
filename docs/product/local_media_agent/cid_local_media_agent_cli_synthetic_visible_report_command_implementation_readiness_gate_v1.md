# CID Local Media Agent — CLI Synthetic Visible Report Command Implementation Readiness Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.READINESS.GATE.V1`

## Objective

This phase decides whether a first minimal CLI wiring implementation for the synthetic visible report command may be authorized.

This phase is documentation/test-only.

It does not implement CLI wiring, command registration, packaging, installable entry points, scanner integration, SaaS integration, backend integration, frontend integration, database integration, Docker integration, Alembic migration, HTML rendering, PDF rendering, DOCX rendering, XLSX rendering, CSV rendering, subtitle generation, DaVinci Resolve export, Avid export, Premiere export, OTIO export, EDL export, XML export, FCPXML export, external binary execution, media probing, media processing, real media processing, network behavior, licensing behavior, installer behavior, or production delivery behavior.

## Upstream Stable Baseline

Latest stable upstream commit:

`dd13871`

Latest stable upstream tag:

`cid-dev-stable-local-media-agent-cli-synthetic-visible-report-command-contract-v1-20260618`

CLI command contract:

`docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_contract_v1.md`

CLI command contract test:

`tests/unit/test_cid_local_media_agent_cli_synthetic_visible_report_command_contract.py`

Renderer implementation:

`scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`

Renderer implementation test:

`tests/unit/test_cid_local_media_agent_synthetic_visible_report_markdown_renderer_implementation.py`

Renderer QA gate test:

`tests/unit/test_cid_local_media_agent_synthetic_visible_report_markdown_renderer_qa_gate.py`

Synthetic fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

## Readiness Decision

`READINESS_DECISION=READY_FOR_MINIMAL_CLI_WIRING_IMPLEMENTATION_WITH_RESTRICTIONS`

Reason:

The Markdown renderer is implemented and QA-gated. The future CLI command contract is closed and defines strict inputs, output, messages, exit behavior, and blocked scope.

A first CLI wiring implementation may be authorized only if it remains local, synthetic-only, development-scoped, non-installable, non-packaged, and does not modify scanner behavior.

## Implementation Authorization Boundary

The next implementation phase may create only a minimal development CLI wrapper for the synthetic visible report command.

Allowed future implementation characteristics:

- pure Python
- standard library only
- isolated script or module
- calls the existing synthetic Markdown renderer
- command name concept: `synthetic-visible-report`
- allowed inputs only: `--fixture`, `--output-dir`, `--allow-overwrite`, `--format markdown`
- output only: `cid_local_media_agent_synthetic_visible_report_v1.md`
- no overwrite by default
- concise success and failure messages
- deterministic exit behavior
- no stack traces by default for expected user errors
- no absolute path leakage in normal messages
- no media input arguments
- no source-media scanning
- no scanner integration
- no network calls
- no SaaS calls
- no database calls
- no backend calls
- no frontend calls
- no external binary execution
- no ffprobe execution
- no ffmpeg execution
- no real media probing
- no real media processing
- no subtitle generation
- no NLE export
- no packaging
- no installable entry point

## Recommended Future Implementation Shape

The future implementation should prefer a separate development script, for example:

`scripts/cid_local_media_agent_synthetic_visible_report_cli.py`

The future implementation should not modify:

`scripts/cid_media_agent_scan.py`

The future implementation should not modify:

- `pyproject.toml`
- `setup.py`
- `setup.cfg`
- package entry point configuration
- backend files
- frontend files
- database files
- Docker files
- Alembic files

The future implementation should use tests with `tmp_path` and subprocess-free direct function testing where possible.

## Future CLI Behavior

The future CLI wrapper should support:

`synthetic-visible-report --fixture tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json --output-dir <controlled-output-dir> --format markdown`

It may also support:

`synthetic-visible-report --fixture tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json --output-dir <controlled-output-dir> --format markdown --allow-overwrite`

The future CLI wrapper must reject:

- missing fixture
- wrong fixture basename
- missing output directory
- unsafe output directory
- existing output without explicit overwrite
- non-Markdown format
- source media paths
- scan paths
- upload endpoints
- tokens
- database URLs
- sync options
- transcription options
- translation options
- subtitle options
- NLE export options
- installer options
- licensing options

## Future Required Test Coverage

The first CLI implementation must include tests proving:

- help text states synthetic local demo scope
- help text states no real media analysis
- help text states no sync, transcription, translation, final subtitles, NLE export, or upload
- command accepts only the contract inputs
- command rejects non-Markdown format
- command rejects wrong fixture basename
- command rejects missing output directory
- command rejects unsafe output directory
- command refuses overwrite by default
- command allows overwrite only with `--allow-overwrite`
- command creates only the deterministic Markdown filename
- command output remains inside the caller-supplied controlled output directory
- command does not modify the fixture
- command does not modify the renderer
- command does not modify scanner code
- command does not call scanner code
- command does not call network libraries
- command does not call SaaS services
- command does not call database services
- command does not execute external binaries
- command does not execute ffprobe
- command does not execute ffmpeg
- command does not process real media
- command does not create HTML, PDF, DOCX, XLSX, CSV, SRT, VTT, XML, FCPXML, EDL, OTIO, MOV, MP4, or WAV
- command messages avoid private paths, usernames, machine names, client identifiers, and real project identifiers
- generated Markdown still includes synthetic demo, local-first, human review, no-real-media, no-sync, no-transcription, no-translation, no-NLE-export, and assistive-CID notices

## Still Blocked After This Readiness Gate

Even if this readiness gate passes, the following remain blocked until explicit future phases:

- packaging
- installable entry point
- production CLI distribution
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
- Windows/macOS/Linux installer
- signed binaries
- updater behavior
- activation behavior
- iLok/PACE behavior

## Proposed Next Phase If This Gate Passes

The next recommended phase is:

`CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.V1`

That future phase may implement a minimal development CLI wrapper only under the restrictions above.

## QA Status

`CLI_SYNTHETIC_VISIBLE_REPORT_COMMAND_IMPLEMENTATION_READINESS_GATE_READY_FOR_VALIDATION`

Commit is blocked until target tests, related tests, staged scope safety check, fixture integrity check, renderer not modified check, scanner not modified check, no CLI wiring staged check, runtime safety static check, WSL guard, and PostgreSQL-only regression guard pass.
