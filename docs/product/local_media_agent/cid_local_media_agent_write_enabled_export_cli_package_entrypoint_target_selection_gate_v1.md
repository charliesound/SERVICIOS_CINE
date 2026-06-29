# CID Local Media Agent — write-enabled export CLI package entrypoint target selection gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.TARGET.SELECTION.GATE.V1`

## Purpose

This doc/test-only gate records that the controlled package entry point implementation is blocked until the correct packaging target is explicitly selected.

The current repository root does not expose a root-level packaging metadata file for the Local Media Agent command.

## Current packaging inspection result

- Root `pyproject.toml`: missing.
- Root `setup.cfg`: missing.
- Root `setup.py`: missing.
- Tracked nested packaging file found: `ai-dubbing-legal-studio/pyproject.toml`.
- The nested file currently contains pytest configuration only.
- The nested file is not authorized as the Local Media Agent package entry point target by this gate.

## Stable baseline

- Baseline HEAD: `87834e0f307f4bf83908a7e345a25bb79ceda687`
- Baseline tag: `cid-dev-stable-local-media-agent-write-enabled-export-cli-package-entrypoint-authorization-gate-v1-20260629`
- Accepted command name: `cid-local-media-agent-visible-report-write-enabled-export`
- Accepted module: `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py`
- Accepted callable: `main`

## Target selection decision

No package entry point implementation is allowed until a future phase explicitly selects one of these targets:

- Create a root-level packaging metadata file for the Local Media Agent command.
- Select an existing packaging metadata file only after proving it owns the Local Media Agent packaging boundary.
- Defer package entry point implementation and keep using the direct module invocation path.

## Explicitly blocked by this gate

- Editing `ai-dubbing-legal-studio/pyproject.toml` for the Local Media Agent command.
- Adding a package entry point to an unrelated nested project.
- Creating root packaging metadata without a dedicated implementation phase.
- Editing runtime implementation.
- Editing the accepted write primitive.
- Running real scanner code.
- Running real media probing tools.
- Running external process behavior.
- Adding network behavior.
- Adding SaaS persistence behavior.
- Backend work.
- Frontend work.
- Installer work.
- Client demo.
- Public demo.
- Production execution.
- Real media material.

## Closure validation

This phase can close only when:

- The target selection gate test passes.
- The authorization gate test still passes.
- The readiness gate test still passes.
- The corrected QA gate test still passes.
- The accepted controlled implementation test still passes.
- Safety checks pass.
- WSL guard passes.
- Database regression guard passes.
- Only this target selection gate doc and test are staged.
- The target tag is absent locally and remotely before tag creation.

## Expected result

`LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_TARGET_SELECTION_GATE_V1_CLOSED`
