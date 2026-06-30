# CID Local Media Agent — write-enabled export CLI root packaging metadata contract V1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.ROOT.PACKAGING.METADATA.CONTRACT.V1`

## Purpose

This doc/test-only contract defines the future root packaging metadata boundary for the Local Media Agent write-enabled visible report export CLI.

This phase does not create `pyproject.toml`, does not add a package entry point, and does not modify runtime.

## Stable baseline

- Baseline HEAD: `73856ba95694399db103235fa48e7bc11ebad0ab`
- Baseline tag: `cid-dev-stable-local-media-agent-write-enabled-export-cli-package-entrypoint-target-selection-gate-v1-20260629`
- Accepted command name: `cid-local-media-agent-visible-report-write-enabled-export`
- Accepted module: `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py`
- Accepted callable: `main`

## Packaging target decision

A future implementation phase may create a root-level `pyproject.toml` only if that phase is explicitly dedicated to root packaging metadata creation for the Local Media Agent command.

The nested file `ai-dubbing-legal-studio/pyproject.toml` remains out of scope for the Local Media Agent package entry point.

## Future root metadata contract

A future root `pyproject.toml` must be minimal and controlled.

It may define:

- Build system metadata only if required by the selected packaging backend.
- Project identity for the Local Media Agent packaging boundary.
- Exactly one script entry for the accepted command name.
- A script target pointing to the accepted module and callable, or to a minimal wrapper only if later authorized.

It must preserve:

- Existing parser surface.
- Dry-run behavior.
- Controlled write authorization.
- Fixture-owned output root restriction.
- No-overwrite behavior.
- Single-artifact behavior.
- No directory creation by the export CLI.
- Deterministic JSON output.

## Explicitly blocked in this phase

- Creating root `pyproject.toml`.
- Editing `ai-dubbing-legal-studio/pyproject.toml`.
- Adding a real package entry point.
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

- The root packaging metadata contract test passes.
- The target selection gate test still passes.
- The authorization gate test still passes.
- The readiness gate test still passes.
- The corrected QA gate test still passes.
- The accepted controlled implementation test still passes.
- Safety checks pass.
- WSL guard passes.
- Database regression guard passes.
- Only this root packaging metadata contract doc and test are staged.
- The target tag is absent locally and remotely before tag creation.

## Expected result

`LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_ROOT_PACKAGING_METADATA_CONTRACT_V1_CLOSED`
