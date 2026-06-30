# CID Local Media Agent — write-enabled export CLI root packaging metadata readiness gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.ROOT.PACKAGING.METADATA.READINESS.GATE.V1`

## Purpose

This doc/test-only readiness gate defines the exact conditions required before creating a real root `pyproject.toml` for the Local Media Agent package entry point.

This phase does not create `pyproject.toml`, does not add a package entry point, and does not modify runtime.

## Stable baseline

- Baseline HEAD: `6a416485957900fd004026c9d50bb95ecc15a1f0`
- Baseline tag: `cid-dev-stable-local-media-agent-write-enabled-export-cli-root-packaging-metadata-contract-v1-20260630`
- Accepted command name: `cid-local-media-agent-visible-report-write-enabled-export`
- Accepted module: `scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py`
- Accepted callable: `main`

## Readiness decision

A future implementation phase may create a root `pyproject.toml` only if it is explicitly scoped as root packaging metadata creation for the Local Media Agent command.

The future file must be minimal, controlled, and limited to the Local Media Agent packaging boundary.

## Required future implementation constraints

A future root `pyproject.toml` creation phase must:

- Create exactly one root-level `pyproject.toml`.
- Avoid editing `ai-dubbing-legal-studio/pyproject.toml`.
- Define one package entry point for the accepted command name.
- Point the command to the accepted module and accepted callable, unless a later explicit gate authorizes a wrapper.
- Avoid changing the accepted runtime implementation.
- Preserve existing parser options.
- Preserve dry-run behavior.
- Preserve controlled write authorization.
- Preserve fixture-owned output root restriction.
- Preserve no-overwrite behavior.
- Preserve single-artifact behavior.
- Preserve deterministic JSON output.

## Explicitly blocked in this phase

- Creating root `pyproject.toml`.
- Editing root packaging metadata.
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

- The root packaging metadata readiness gate test passes.
- The root packaging metadata contract test still passes.
- The target selection gate test still passes.
- The authorization gate test still passes.
- The readiness gate test still passes.
- The corrected QA gate test still passes.
- The accepted controlled implementation test still passes.
- Safety checks pass.
- WSL guard passes.
- Database regression guard passes.
- Only this root packaging metadata readiness gate doc and test are staged.
- The target tag is absent locally and remotely before tag creation.

## Expected result

`LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_ROOT_PACKAGING_METADATA_READINESS_GATE_V1_CLOSED`
